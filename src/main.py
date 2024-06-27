# Library imports
from vex import *
# ------------------------
# Code by Eric & Peter (mostly Eric)
# Team 75477M 'Frij'
# ... 2024-2025
# ------------------------
# Wiring Guide


# Brain
brain=Brain()

# Controllers
controller_1 = Controller(PRIMARY)
controller_2 = Controller(PARTNER)

# Motors (A front, C back)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, True)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b)
right_motor_a = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)
right_motor_b = Motor(Ports.PORT4, GearSetting.RATIO_18_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b)

left_lift = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)
right_lift = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)
lift = MotorGroup(left_lift, right_lift)

intake = Motor(Ports.PORT7, GearSetting.RATIO_6_1, False)
# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24, 377.1, 304.8, MM, 5/3)

# Sensor & Pneumatics
inertial = Inertial(Ports.PORT20)
leftwheel_rotation = Rotation(Ports.PORT19, False)
lift_rotation = Rotation(Ports.PORT18, False)

lift_rotation.set_position(0, DEGREES)

pto = DigitalOut(brain.three_wire_port.a)
clamp = DigitalOut(brain.three_wire_port.b)

# Variables initialisation
left_drive_smart_stopped = 0
right_drive_smart_stopped = 0
left_drive_smart_speed = 0
right_drive_smart_speed = 0
pto_status = 0 #0 drivebase, 1 lift
clamp_status = 0 #0 release, 1 clamp
lift_status = 0

brain.screen.draw_image_from_file("begin.png", 0, 0)
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
    kp = 0.18
    ki = 0.139
    kd = 0.05
    previous_error = 0
    integral = 0
    inertial.set_heading(0.5, DEGREES)
    drivetrain.turn(RIGHT)
    drivetrain.set_stopping(HOLD)
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

# PID straight def
def drivetrain_straight(distance):
    #change kp, ki, kd, accoding to the robot
    kp = 0.18
    ki = 0.139
    kd = 0.05
    #distance
    kp_d= 0.5
    ki_d= 0.1
    kd_d= 0.1
    max_speed = 50
    distance_error = distance - (rightwheel_rotation+leftwheel_rotation)/720* math.Pi * 82.55
    previous_distance_error = 0
    #angle
    error = 0
    previous_error = 0
    integral = 0
    leftwheel_rotation.set_position(0, DEGREES)
    righttwheel_rotation.set_position(0, DEGREES)
    
    left_drive_smart.set_velocity(max_speed, PERCENT)
    right_drive_smart.set_velocity(max_speed, PERCENT)
    left_drive_smart.spin(FORWARD)
    right_drive_smart.spin(FORWARD)
    drivetrain.set_stopping(HOLD)
    while distance_error > 0.5:
        while not (leftwheel_rotation.angle() == rightwheel_rotation.angle()):
            error = leftwheel_rotation.angle() - rightwheel_rotation.angle()
            integral += error
            integral = max(min(integral, 30), -30)
            derivative = error - previous_error
            pid_output = (kp * error) + (ki * integral) + (kd * derivative)
            previous_error = error
            pid_output = max(min(pid_output, max_speed), -max_speed)
            
        integral_d += distance_error
        integral_d = max(min(integral_d, 30), -30)
        derivative_d = distance_error - previous_distance_error
        speed_pid_output = (kp_d * distance_error) + (ki_d * integral_d) + (kd_d * derivative_d)
        max_speed = max(min(speed_pid_output, 80), 5)
        left_drive_smart.set_velocity(max_speed+pid_output, PERCENT)
        right_drive_smart.set_velocity(max_speed-pid_output, PERCENT)
        distance_error = distance - (rightwheel_rotation.angle()-leftwheel_rotation.angle())/720* math.Pi * 82.55
    drivetrain.stop()

# Autonomous def
def autonomous():
    if team_position == "red_1" or team_position == "blue_1":
        pass
    if team_position == "red_2" or team_position == "blue_2":
        pass

#  Driver Control def
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, pto_status, clamp_status, lift_status
    drivetrain.set_stopping(COAST)
    # Process every 20 milliseconds
    while True:
    # Status Update
        pto.set(pto_status)
    # Drive Train
        #arcade drive
        max_speed = 70
        rotate = max_speed*controller_1.axis1.position()/100
        forward = 100*math.sin(((controller_1.axis3.position()**3)/636620))

        left_drive_smart_speed = forward + rotate
        right_drive_smart_speed = forward - rotate

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
            
        if controller_1.buttonL1.pressing():
            if lift_status == 0:
                if pto_status == 0:
                    pto_status = 1
                    pto.set(pto_status)
                    wait(500, MSEC)
                    lift_status = "up"
                    lift.stop()
                    lift.set_stopping(HOLD)
                    lift.spin(FORWARD, 100, PERCENT)
                elif pto_status == 1:
                    lift_status = "down"
                    lift.spin(REVERSE, 100, PERCENT)
            while controller_1.buttonL1.pressing():
                wait(30, MSEC)

        if lift_status == "up" and lift_rotation.position(TURNS) < -1.3-0.3:
            lift.stop()
            lift_status = 0
        if lift_status == "down" and lift_rotation.position(TURNS) > 0:
            lift.stop()
            lift_status = 0
            pto_status = 0
            lift.set_stopping(COAST)
            wait(200, MSEC)
            pto.set(pto_status)
            
        if controller_1.buttonL2.pressing():
            clamp_status = not clamp_status
            clamp.set(clamp_status)
            while controller_1.buttonL2.pressing():
                wait(30, MSEC)
            
            
        #testing code
        '''
        if pto_status == 1:
            if controller_1.buttonB.pressing():
                lift.spin(REVERSE, 100, PERCENT)
            
            elif controller_1.buttonA.pressing():
                lift.spin(FORWARD, 100, PERCENT)
            else:
                lift.stop()
        
        if controller_1.buttonY.pressing():
            pto_status = not pto_status
            pto.set(pto_status)
            lift.stop()
            if pto_status == 1:
                lift.set_stopping(HOLD)
            else:
                lift.set_stopping(COAST)
            while controller_1.buttonY.pressing():
                wait(30, MSEC)
        '''  

#choose team
team_position = team_choosing() 
# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)