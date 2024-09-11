# Library imports
from vex import *
from math import atan2, degrees
# ------------------------
# Code by Eric & Peter (mostly Eric)
# Team 75477M 'Frij'
# High Stakes 2024-2025
# ------------------------
# Wiring Guide
# left drivebase motors: 1, 2, 3
# right drivebase motors: 4, 5, 6
# lift: left 7, right 8
# intake: 9
#
# inertial: 20
# lift rotation: 19
#
# PTO: A
# Goal clamp: B
# Paddle: C
# Sorter: D


# Brain
brain=Brain()

# Controllers
controller_1 = Controller(PRIMARY)
controller_2 = Controller(PARTNER)

# Motors (A front, C back)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, True)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
left_motor_c = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)
right_motor_a = Motor(Ports.PORT4, GearSetting.RATIO_18_1, False)
right_motor_b = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)
right_motor_c = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

left_lift = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)
right_lift = Motor(Ports.PORT8, GearSetting.RATIO_18_1, True)
lift = MotorGroup(left_lift, right_lift)

intake = Motor(Ports.PORT9, GearSetting.RATIO_6_1, False)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24 , 377.1, 304.8, MM, 5/3)

# Sensor & Pneumatics
inertial = Inertial(Ports.PORT20)
lift_rotation = Rotation(Ports.PORT12, False)
odometry = Rotation(Ports.PORT18, False)
optical = Optical(Ports.PORT17)

lift_rotation.set_position(360, DEGREES)


pto = DigitalOut(brain.three_wire_port.f)
clamp = DigitalOut(brain.three_wire_port.b)
paddle = DigitalOut(brain.three_wire_port.c)
sorter = DigitalOut(brain.three_wire_port.d)
indicator = DigitalOut(brain.three_wire_port.e)

# Variables initialisation
left_drive_smart_stopped = 0
right_drive_smart_stopped = 0
left_drive_smart_speed = 0
right_drive_smart_speed = 0
pto_status = 0 #0 drivebase, 1 lift
clamp_status = 0 #0 release, 1 clamp
lift_status = 0
ring_sort_status = "Both"

brain.screen.draw_image_from_file("begin.png", 0, 0)
'''
# auto path planner
class Coordinate:
    def __init__(self, x: float, y: float):
        self.x = round(x, 2)
        self.y = round(y, 2)

    def is_valid(self) -> bool:
        if self.x == -200000:
            return False
        return True

    def get_distance_to(self, other) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def get_angle(self, end) -> float:
        if type(end) != Coordinate:
            raise TypeError()

        x = end.x - self.x
        y = end.y - self.y

        angle_rad = atan2(y, x)

        angle_deg = degrees(angle_rad)

        rotation_angle = 90 - angle_deg

        if rotation_angle < 0:
            rotation_angle += 360

        if rotation_angle > 359.9:
            return rotation_angle - 359.9

        return rotation_angle

    def __str__(self):
        return f'[{self.x}, {self.y}]'

# return -1 if negative, or 1 otherwise
def sgn(num: float) -> int:
    if num >= 0:
        return 1
    else:
        return -1

# helper function for line_circle_intersection
def LCI_check(point: Coordinate, line_start: Coordinate, line_end: Coordinate) -> Coordinate:
    min_x = min(line_start.x, line_end.x)
    max_x = max(line_start.x, line_end.x)
    min_y = min(line_start.y, line_end.y)
    max_y = max(line_start.y, line_end.y)
    if not min_x <= point.x <= max_x:
        return Coordinate(-200000, -200000)

    if not min_y <= point.y <= max_y:
        return Coordinate(-200000, -200000)

    return point

# Return the coordinate of two intersection between the circle and line
def line_circle_intersection(currentPos: Coordinate, pt1: Coordinate, pt2: Coordinate, lookAheadDis: float) -> list[Coordinate]:
    currentX = currentPos.x
    currentY = currentPos.y
    x1 = pt1.x - currentX
    y1 = pt1.y - currentY
    x2 = pt2.x - currentX
    y2 = pt2.y - currentY

    # For math calculation
    dx = x2 - x1
    dy = y2 - y1
    dr = (dx ** 2 + dy ** 2) ** 0.5
    D = x1 * y2 - x2 * y1

    discriminant = lookAheadDis ** 2 * dr ** 2 - D ** 2
    # No intersection
    if discriminant < 0:
        return [Coordinate(-200000, -200000), Coordinate(-200000, -200000)]
    # One intersection (tangent)
    if discriminant == 0:
        point_x = D * dy / dr ** 2 + currentX
        point_y = -1 * D / dr ** 2 + currentY
        return [LCI_check(Coordinate(point_x, point_y), pt1, pt2), Coordinate(-200000, -200000)]

    # Two intersection
    point_1_x = (D * dy + sgn(dy) * dx * discriminant ** 0.5) / dr ** 2 + currentX
    point_1_y = (-1 * D * dx + abs(dy) * discriminant ** 0.5) / dr ** 2 + currentY

    point_2_x = (D * dy - sgn(dy) * dx * discriminant ** 0.5) / dr ** 2 + currentX
    point_2_y = (-1 * D * dx - abs(dy) * discriminant ** 0.5) / dr ** 2 + currentY

    return [LCI_check(Coordinate(point_1_x, point_1_y), pt1, pt2), LCI_check(Coordinate(point_2_x, point_2_y), pt1, pt2)]

def get_move_plan(path: list[Coordinate], radius: float) -> list:
    lastPoint = 0
    nextPoint = lastPoint + 1
    currentPosition = path[0]
    currentAngle = 0

    result = [[],[]]

    while True:
        # If next point in the search circle
        if currentPosition.get_distance_to(path[nextPoint]) <= radius:
            lastPoint += 1
            nextPoint += 1

        if lastPoint == len(path)-1:
            break

        intersection_one, intersection_two = line_circle_intersection(currentPosition, path[lastPoint], path[nextPoint], radius)

        if not intersection_one.is_valid() and not intersection_two.is_valid():
            # No intersection
            target = path[nextPoint]
        elif not intersection_one.is_valid():
            # One intersection (point two)
            target = intersection_two
        elif not intersection_two.is_valid():
            # One intersection (point one)
            target = intersection_one
        else:
            # Two intersection
            distance_one = path[nextPoint].get_distance_to(intersection_one)
            distance_two = path[nextPoint].get_distance_to(intersection_two)
            if distance_one < distance_two:
                target = intersection_one
            else:
                target = intersection_two

        if nextPoint == len(path)-1:
            target = path[nextPoint]

        turn_angle = currentPosition.get_angle(target)
        relevant_turn_angle = round((turn_angle - currentAngle) % 360, 2)

        if relevant_turn_angle > 359.9:
            relevant_turn_angle -= 359.9

        distance = round(currentPosition.get_distance_to(target), 2)
        
        result[0].append(relevant_turn_angle)
        result[1].append(distance)

        currentPosition = target
        currentAngle = (currentAngle + relevant_turn_angle) % 360

    return result
'''

# team and side choosing
def team_choosing():
    team = ""
    position = ""
    while True:
        if controller_1.buttonL1.pressing():
            brain.screen.draw_image_from_file( "red_1_confirmed.png", 0, 0)
            while controller_1.buttonL1.pressing():
                wait(5, MSEC)
            return "red_1"
        elif controller_1.buttonL2.pressing():
            brain.screen.draw_image_from_file( "red_2_confirmed.png", 0, 0)
            while controller_1.buttonL2.pressing():
                wait(5, MSEC)
            return "red_2"
        elif controller_1.buttonR1.pressing():
            brain.screen.draw_image_from_file( "blue_1_confirmed.png", 0, 0)
            while controller_1.buttonR1.pressing():
                wait(5, MSEC)
            return "blue_1"
        elif controller_1.buttonR2.pressing():
            brain.screen.draw_image_from_file( "blue_2_confirmed.png", 0, 0)
            while controller_1.buttonR2.pressing():
                wait(5, MSEC)
            return "blue_2"
        if brain.screen.pressing() and 8 <= brain.screen.y_position() <= 26:
            # Team choosing
            if 139 <= brain.screen.x_position() <= 240:
                # Red
                team = "red"
                brain.screen.draw_image_from_file( "red_begin.png", 0, 0)
                position = ""
            elif 249 <= brain.screen.x_position() <= 351:
                # Blue
                team = "blue"
                brain.screen.draw_image_from_file("blue_begin.png", 0, 0)
                position = ""
            elif 358 <= brain.screen.x_position() <= 461:
                # Skill
                team = "skill"
                brain.screen.draw_image_from_file( "skill_begin.png", 0, 0)
                position = ""
        elif brain.screen.pressing() and 19 <= brain.screen.x_position() <= 138 and not team == "":
            # Position sellction
            if brain.screen.y_position() > 52 and brain.screen.y_position() < 73:
                if team == "red":
                    # Red 1
                    brain.screen.draw_image_from_file( "red_1.png", 0, 0)
                elif team == "blue":
                    # Blue 1
                    brain.screen.draw_image_from_file( "blue_1.png", 0, 0)
                elif team == "skill":
                    # Skill confirm
                    brain.screen.draw_image_from_file( "skill_confirmed.png", 0, 0)
                    return "skill"
                position = "1"
            elif brain.screen.pressing() and 85 <= brain.screen.y_position() <= 107 and not team == "":
                if team == "red":
                    # Red 2
                    brain.screen.draw_image_from_file( "red_2.png", 0, 0)
                elif team == "blue":
                    # Blue 2
                    brain.screen.draw_image_from_file( "blue_2.png", 0, 0)
                position = "2"
            elif brain.screen.pressing() and 120 <= brain.screen.y_position() <= 142 and not team == "":
                if team == "red":
                    # Red confirm
                    if position == "1":
                        # Red 1 confirm
                        brain.screen.draw_image_from_file( "red_1_confirmed.png", 0, 0)
                    elif position == "2":
                        # Red 2 confirm
                        brain.screen.draw_image_from_file( "red_2_confirmed.png", 0, 0)
                elif team == "blue":
                    # Blue confirm
                    if position == "1":
                        # Blue 1 confirm
                        brain.screen.draw_image_from_file( "blue_1_confirmed.png", 0, 0)
                    elif position == "2":
                        # Blue 2 confirm
                        brain.screen.draw_image_from_file( "blue_2_confirmed.png", 0, 0)
                return team + "_" + position
            while brain.screen.pressing():
                wait(5, MSEC)
        wait(5, MSEC)

# PID turn def
def drivetrain_turn(target_angle):
    #change kp, ki, kd, accoding to the robot
    kp = 0.4
    ki = 0.25
    kd = 0.2
    previous_error = 0
    integral = 0
    inertial.set_heading(0.5, DEGREES)
    drivetrain.turn(RIGHT)
    current_angle = inertial.heading(DEGREES)
    while not (target_angle - 0.5 < current_angle < target_angle + 0.5):
        error = target_angle - current_angle
        integral += error
        integral = max(min(integral, 30), -30)
        derivative = error - previous_error
        pid_output = (kp * error) + (ki * integral) + (kd * derivative)
        previous_error = error
        pid_output = max(min(pid_output, 100), -100)
        drivetrain.set_turn_velocity(pid_output, PERCENT)
        current_angle = inertial.heading(DEGREES)
    drivetrain.stop()

# odometry def
def drivetrain_forward(target_turns):
    kp = 1
    ki = 2.5
    kd = 2
    previous_error = 0
    integral = 0
    drivetrain.drive(FORWARD)
    initial_turns = odometry.position(TURNS)
    current_turns = odometry.position(TURNS)
    while not(target_turns-0.1 < current_turns - initial_turns < target_turns+0.1):
        error = target_turns-(current_turns-initial_turns)
        integral += error
        integral = max(min(integral, 30), -30)
        derivative = error - previous_error
        odometry_output = (kp * error) + (ki * integral) + (kd * derivative)
        previous_error = error
        odometry_output = max(min(odometry_output, 100), -100)
        drivetrain.set_drive_velocity(odometry_output, PERCENT)
        current_turns = odometry.position(TURNS)
    drivetrain.set_stopping(HOLD)
    drivetrain.stop()
    wait(100, MSEC)
    drivetrain.set_stopping(COAST)

#autopath def
'''
def autopath(coor_list, radius): #coordinate and radius needs to be mm, in form of [rp.Coordinate(x, y)]
    plan = get_move_plan(coor_list, radius)
    for i in range(len(plan[0])):
        drivetrain_turn(plan[0][i])
        drivetrain_forward(plan[1][i]/159.64) #convert mm into turns'''
         
# Autonomous def
def autonomous():
    if team_position == "red_1" or team_position == "blue_2":
        drivetrain.set_drive_velocity(80, PERCENT)
        intake.set_velocity(100, PERCENT)
        drivetrain.drive(REVERSE)
        wait(0.83, SECONDS)
        drivetrain.stop()
        wait(0.3, SECONDS)
        clamp_status = 1
        clamp.set(clamp_status)
        intake.set_timeout(1, SECONDS)
        intake.spin_for(FORWARD, 100, TURNS)
        drivetrain.turn(LEFT, 45, PERCENT)
        wait(1, SECONDS)
        intake.spin(REVERSE)
        drivetrain.drive(FORWARD, 50, PERCENT)
        intake.spin(FORWARD)
        wait(1, SECONDS)
        drivetrain.stop()
        drivetrain.turn(RIGHT, 75, PERCENT)
        wait(1, SECONDS)
        drivetrain.stop()
        drivetrain.drive(FORWARD)
        wait(1, SECONDS)
        intake.stop()
        drivetrain.stop()

    if team_position == "blue_1" or team_position == "red_2":
        drivetrain.set_drive_velocity(80, PERCENT)
        intake.set_velocity(100, PERCENT)
        drivetrain.drive(REVERSE)
        wait(0.83, SECONDS)
        drivetrain.stop()
        wait(0.3, SECONDS)
        clamp_status = 1
        clamp.set(clamp_status)
        intake.set_timeout(1, SECONDS)
        intake.spin_for(FORWARD, 100, TURNS)
        drivetrain.turn(RIGHT, 45, PERCENT)
        wait(1, SECONDS)
        intake.spin(REVERSE)
        drivetrain.drive(FORWARD, 50, PERCENT)
        intake.spin(FORWARD)
        wait(1, SECONDS)
        drivetrain.stop()
        drivetrain.turn(LEFT, 75, PERCENT)
        wait(1, SECONDS)
        drivetrain.stop()
        drivetrain.drive(FORWARD)
        wait(1, SECONDS)
        intake.stop()
        drivetrain.stop()

    if team_position == "red_2" or team_position == "blue_2":
        pass
    if team_position == "skill":
        drivetrain.drive_for(REVERSE, 200, MM)
        clamp.set(True)
        wait(0.5, SECONDS)
        intake.spin(FORWARD, 100, PERCENT)
        drivetrain.turn_for(RIGHT, 60, DEGREES, True)
        drivetrain.drive_for(REVERSE, 5000, MM)
        drivetrain.stop()

#  Driver Control def
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, pto_status, clamp_status, lift_status
    drivetrain.set_stopping(COAST)
    lift_status = 0
    brain.timer.clear()
    # Process every 20 milliseconds
    while True:
    # Status Update
        pto.set(pto_status)
    # Drive Train
        #arcade drive
        ratio = 1.5
        forward = 100*math.sin(((controller_1.axis3.position()**3)/636620))
        rotate_dynamic = (100/ratio)*math.sin((abs((forward**3))/636620))*math.sin(((controller_1.axis1.position()**3)/636620))
        rotate_linear = 50*math.sin(((controller_1.axis1.position()**3)/636620))

        if -35 <= forward <= 35:
            left_drive_smart_speed = forward + rotate_linear
            right_drive_smart_speed = forward - rotate_linear
        else:
            left_drive_smart_speed = forward + rotate_dynamic
            right_drive_smart_speed = forward - rotate_dynamic

        if left_drive_smart_speed < 3 and left_drive_smart_speed > -3:
            if left_drive_smart_stopped:
                if pto_status == 0:
                    left_lift.stop()
                left_drive_smart.stop()
                left_drive_smart_stopped = 0
        else:
            left_drive_smart_stopped = 1
        if right_drive_smart_speed < 3 and right_drive_smart_speed > -3:
            if right_drive_smart_stopped:
                if pto_status == 0:
                    right_lift.stop()
                right_drive_smart.stop()
                right_drive_smart_stopped = 0
        else:
            right_drive_smart_stopped = 1

        if left_drive_smart_stopped:
            left_drive_smart.set_velocity(left_drive_smart_speed, PERCENT)
            if pto_status == 0:
                    left_lift.set_velocity(left_drive_smart_speed, PERCENT)
                    left_lift.spin(FORWARD)
            left_drive_smart.spin(FORWARD)
        if right_drive_smart_stopped:
            if pto_status == 0:
                    right_lift.set_velocity(right_drive_smart_speed, PERCENT)
                    right_lift.spin(FORWARD)
            right_drive_smart.set_velocity(right_drive_smart_speed, PERCENT)
            right_drive_smart.spin(FORWARD)
        
        if controller_1.buttonR1.pressing():
            intake.spin(FORWARD, 100, PERCENT)
        elif controller_1.buttonR2.pressing():
            intake.spin(REVERSE, 100, PERCENT)
                
        else:
            intake.stop()
       
        # control
        if controller_1.buttonL1.pressing():
            paddle.set(True)
        else:
            paddle.set(False)
            
        # goal clamp control
        if controller_1.buttonL2.pressing():
            clamp_status = not clamp_status
            clamp.set(clamp_status)
            indicator.set(not clamp_status)
            while controller_1.buttonL2.pressing():
                wait(30, MSEC)
            
        # ring sorting status control
        if controller_2.buttonA.pressing():
            if ring_sort_status == "Red":
                ring_sort_status = "Blue"
            else:
                ring_sort_status = "Red"
            while controller_1.buttonA.pressing():
                wait(30, MSEC)
        elif controller_2.buttonB.pressing():
            ring_sort_status = "Both"
            while controller_1.buttonB.pressing():
                wait(30, MSEC)
            
        #lift contol
        if controller_1.axis2.position() > 90:
            lift_status = "up"
            pto_status = 1
            pto.set(pto_status)
            lift_rotation.set_position(360, DEGREES)
            wait(300, MSEC)
            lift.spin(REVERSE, 100, PERCENT)
            
        if controller_1.axis2.position() < -90:
            lift_status = "down"
            lift.spin(FORWARD, 80, PERCENT)
            
            
        if lift_rotation.position(DEGREES) < 65 and lift_status == "up":
            lift.set_stopping(HOLD)
            lift_status = 0
            lift.stop()
        
        if lift_rotation.position(DEGREES) > 355 and lift_status == "down":
            lift.stop()
            lift.set_stopping(COAST)
            lift_status = 0
            pto_status = 0
            pto.set(pto_status)


#choose team
team_position = team_choosing() 
# Compe tition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)