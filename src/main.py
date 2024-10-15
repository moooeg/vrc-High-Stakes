# Library imports
from vex import *
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
lift_rotation = Rotation(Ports.PORT16, False)
odometry = Rotation(Ports.PORT18, False)
optical = Optical(Ports.PORT17)
distance = Distance(Ports.PORT15)
lift_rotation.set_position(360, DEGREES)


pto = DigitalOut(brain.three_wire_port.f)
clamp = DigitalOut(brain.three_wire_port.b)
paddle = DigitalOut(brain.three_wire_port.c)
indicator = DigitalOut(brain.three_wire_port.e)
elevation = DigitalOut(brain.three_wire_port.d)

# Variables initialisation
left_drive_smart_stopped = 0
right_drive_smart_stopped = 0
left_drive_smart_speed = 0
right_drive_smart_speed = 0
pto_status = 0 #0 drivebase, 1 lift
clamp_status = 0 #0 release, 1 clamp
lift_status = "stop" #direction of lift, up, down and stop
lift_stage = 0 # 0 lowest, 2 heighest
ring_sort_status = "Both" #Red, Blue and Both
storage = []
elevation_status = 0 #0 down, 1 up

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
def drivetrain_turn_right(target_angle: float):
    #change kp, ki, kd, accoding to the robot
    kp = 0.4
    ki = 0.25
    kd = 0.2
    previous_error = 0
    integral = 0
    inertial.set_heading(1, DEGREES)
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
    
def drivetrain_turn_left(target_angle: float):
    #change kp, ki, kd, accoding to the robot
    kp = 0.4
    ki = 0.25
    kd = 0.2
    previous_error = 0
    integral = 0
    inertial.set_heading(359.5, DEGREES)
    drivetrain.turn(LEFT)
    current_angle = inertial.heading(DEGREES)
    while not (target_angle - 0.5 < current_angle < target_angle + 0.5):
        error = current_angle - target_angle
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
def drivetrain_forward(target_turns: float, unit: str = "turns"):
    if unit == "mm":
        target_turns = target_turns / 159.59
    kp = 1
    ki = 2.5
    kd = 2
    previous_error = 0
    integral = 0
    drivetrain.drive(FORWARD)
    initial_turns = odometry.position(TURNS)
    current_turns = odometry.position(TURNS)
    false_condition_start_time = None
    false_condition_duration = 0
    while True:
        error = target_turns - (current_turns - initial_turns)
        integral += error
        integral = max(min(integral, 30), -30)
        derivative = error - previous_error
        odometry_output = (kp * error) + (ki * integral) + (kd * derivative)
        previous_error = error
        odometry_output = max(min(odometry_output, 100), -100)
        drivetrain.set_drive_velocity(odometry_output, PERCENT)
        current_turns = odometry.position(TURNS)
        if not (target_turns - 0.05 < current_turns - initial_turns < target_turns + 0.05):
            # Reset the timer if the condition is false
            false_condition_start_time = None
        else:
            # Start tracking time if the condition has just become false
            if false_condition_start_time is None:
                false_condition_start_time = brain.timer.time(MSEC)
            else:
                false_condition_duration = brain.timer.time(MSEC) - false_condition_start_time

        # Break the loop if the condition has been false for more than 0.5 seconds
        if false_condition_duration >= 500:
            break
    drivetrain.set_stopping(HOLD)
    drivetrain.stop()
    wait(100, MSEC)
    drivetrain.set_stopping(COAST)


# ring holding list def
def add_color(new_color):
    if len(storage) >= 2:
        storage.pop(0)  # Remove the first color if the list is full
    storage.append(new_color)

'''
def autopath(plan_list): #coordinate and radius needs to be mm, in form of [rp.Coordinate(x, y)]
    for i in range(len(plan_list[0])):
        drivetrain_turn(plan_list[0][i])
        drivetrain_forward(plan_list[1][i]/159.59) #convert mm into turns'''
         
# Autonomous def
def autonomous(): #2 share goal side, 1 share ring side
    global ring_sort_status
    intake.set_velocity(100, PERCENT)
    if team_position == "red_1":
        drivetrain_forward(2.1)
        drivetrain.turn(LEFT, 40, PERCENT)
        wait(0.85, SECONDS)
        drivetrain.stop()
        drivetrain_forward(-0.33)
        intake.spin(FORWARD)
        wait(0.36, SECONDS)
        intake.stop()
        wait(0.2, SECONDS)
        drivetrain_forward(0.5)
        drivetrain.turn(RIGHT, 60, PERCENT)
        wait(0.99, SECONDS)
        drivetrain.stop()
        drivetrain.drive(REVERSE, 50, PERCENT)
        wait(2.5, SECONDS)
        drivetrain.stop()
        clamp.set(True)
        wait(0.3, SECONDS)
        drivetrain_forward(0.2)
        drivetrain.turn(RIGHT, 50, PERCENT)
        wait(0.9, SECONDS)
        drivetrain.stop()
        intake.spin(FORWARD)
        drivetrain_forward(2.3)
        drivetrain.turn(RIGHT, 50, PERCENT)
        wait(0.7, SECONDS)
        drivetrain.stop()
        drivetrain_forward(1.4)
        wait(0.5, SECONDS)
        drivetrain_forward(-1)
        drivetrain.turn(LEFT, 50, PERCENT)
        wait(0.2, SECONDS)
        drivetrain.stop()
        drivetrain_forward(1.3)
        wait(0.5, SECONDS)
        drivetrain_forward(-0.5)
        '''drivetrain.drive(REVERSE, 50, PERCENT)
        wait(1.5, SECONDS)
        drivetrain.stop()
        wait(0.5, SECONDS)
        clamp.set(True)
        drivetrain_turn_right(50)
        intake.spin(FORWARD)
        drivetrain_forward(3.5)
        drivetrain_turn_right(70)
        drivetrain_forward(1.3)
        wait(0.5, SECONDS)
        drivetrain_forward(-0.5)
        drivetrain_turn_right(15)
        drivetrain_forward(0.8)
        wait(0.5, SECONDS)
        drivetrain_forward(-2)
        drivetrain_turn_right(60)
        drivetrain_forward(6)'''

    if team_position == "red_2":
        pass
        
    if team_position == "blue_1":
        drivetrain_forward(2.1)
        drivetrain.turn(RIGHT, 40, PERCENT)
        wait(0.85, SECONDS)
        drivetrain.stop()
        drivetrain_forward(-0.33)
        intake.spin(FORWARD)
        wait(0.36, SECONDS)
        intake.stop()
        wait(0.2, SECONDS)
        drivetrain_forward(0.5)
        drivetrain.turn(LEFT, 60, PERCENT)
        wait(0.99, SECONDS)
        drivetrain.stop()
        drivetrain.drive(REVERSE, 50, PERCENT)
        wait(2.5, SECONDS)
        drivetrain.stop()
        clamp.set(True)
        wait(0.3, SECONDS)
        drivetrain_forward(0.2)
        drivetrain.turn(LEFT, 50, PERCENT)
        wait(0.9, SECONDS)
        drivetrain.stop()
        intake.spin(FORWARD)
        drivetrain_forward(2.2)
        drivetrain.turn(LEFT, 55, PERCENT)
        wait(0.7, SECONDS)
        drivetrain.stop()
        drivetrain_forward(1.4)
        wait(0.5, SECONDS)
        drivetrain_forward(-1)
        drivetrain.turn(RIGHT, 45, PERCENT)
        wait(0.2, SECONDS)
        drivetrain.stop()
        drivetrain_forward(1.2)
        wait(0.5, SECONDS)
        drivetrain_forward(-0.5)
             
    if team_position == "blue_2":
        pass
    
    if team_position == "skill":
        intake.spin(FORWARD)
        wait(0.36, SECONDS)
        intake.stop()
        wait(0.2, SECONDS)
        drivetrain_forward(0.5)
        drivetrain.turn(RIGHT, 40, PERCENT)
        wait(0.85, SECONDS)
        drivetrain.stop()
        
#  Driver Control def
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, pto_status, clamp_status, lift_status, lift_stage, ring_sort_status, elevation_status, ring_sort_status, storage
    drivetrain.set_stopping(COAST)
    lift_status = 0
    brain.timer.clear()
    if team_position == "red_1" or team_position == "red_2":
        ring_sort_status = "BLUE"
    if team_position == "blue_1" or team_position == "blue_2":
        ring_sort_status = "RED"
    # Process every 20 milliseconds
    while True:
    # Status Update
        pto.set(pto_status)
    # Drive Train
        #arcade drive
        ratio = 1.4
        forward = 100*math.sin(((controller_1.axis3.position()**3)/636620))
        rotate_dynamic = (100/ratio)*math.sin((abs((forward**3))/636620))*math.sin(((controller_1.axis1.position()**3)/636620))
        rotate_linear = 50*math.sin(((controller_1.axis1.position()**3)/636620))
        rotate_linear_lift = 35*math.sin(((controller_1.axis1.position()**3)/636620))

        if -35 <= forward <= 35:
            if lift_stage != 0:
                left_drive_smart_speed = forward + rotate_linear_lift
                right_drive_smart_speed = forward - rotate_linear_lift
            else:
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
            
    #intake color sensor
        if optical.color() == Color.RED:
            add_color("RED")
        if 160.0 < optical.hue() < 250.0: # type: ignore
            add_color("BLUE")
            
    #intake filter control
        if controller_1.buttonR1.pressing(): # normal intake filter
            intake.spin(FORWARD, 100, PERCENT)
            if ring_sort_status == "RED":
                if distance.object_distance() < 15.0 and storage[0] == "RED":
                    intake.set_velocity(100, PERCENT)
                    wait(100, MSEC)
                    intake.spin_for(REVERSE, 2, TURNS)
                    while distance.object_distance() < 15.0:
                        wait(30, MSEC)
                    storage.pop(0)
            elif ring_sort_status == "BLUE":
                if distance.object_distance() < 15.0 and storage[0] == "BLUE":
                    intake.set_velocity(100, PERCENT)
                    wait(100, MSEC)
                    intake.spin_for(REVERSE, 2, TURNS)
                    while distance.object_distance() < 15.0:
                        wait(30, MSEC)
                    storage.pop(0)
        elif controller_1.buttonR2.pressing(): # wall goal intake filter
            intake.spin(FORWARD, 100, PERCENT)
            if ring_sort_status == "RED":
                if distance.object_distance() < 15.0 and storage[0] == "BLUE":
                    intake.set_velocity(100, PERCENT)
                    intake.spin_for(REVERSE, 6, TURNS)
                    while distance.object_distance() < 15.0:
                        wait(30, MSEC) 
                    storage.pop(0)
                if distance.object_distance() < 15.0 and storage[0] == "RED":
                    intake.set_velocity(100, PERCENT)
                    wait(100, MSEC)
                    intake.spin_for(REVERSE, 2, TURNS)
                    while distance.object_distance() < 15.0:
                        wait(30, MSEC)
                    storage.pop(0)
            elif ring_sort_status == "BLUE":
                if distance.object_distance() < 15.0 and storage[0] == "RED":
                    intake.set_velocity(100, PERCENT)
                    intake.spin_for(REVERSE, 6, TURNS)
                    while distance.object_distance() < 15.0:
                        wait(30, MSEC) 
                    storage.pop(0)
                if distance.object_distance() < 15.0 and storage[0] == "BLUE":
                    intake.set_velocity(100, PERCENT)
                    wait(100, MSEC)
                    intake.spin_for(REVERSE, 2, TURNS)
                    while distance.object_distance() < 15.0:
                        wait(30, MSEC)
                    storage.pop(0)     
        else:
            intake.stop()
       
    # paddle control
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
                
    # lift contol
        if controller_1.axis2.position() > 95:
            lift_status = "up"
            pto_status = 1
            pto.set(pto_status)
            wait(50, MSEC)
            lift.spin(REVERSE, 100, PERCENT)
        if controller_1.axis2.position() < -95:
            lift_status = "down"
            lift.spin(FORWARD, 80, PERCENT)
            
        '''if lift_stage == 0:
            if lift_rotation.position(TURNS) < 0.65 and lift_status == "up":
                lift.set_stopping(HOLD)
                lift_status = "stop"
                lift_stage = 1
                lift.stop()
        elif lift_stage == 1:
            if lift_rotation.position(TURNS) < -0.1 and lift_status == "up":
                lift.set_stopping(HOLD)
                lift_status = "stop"
                lift_stage = 2
                lift.stop()'''
        if lift_rotation.position(TURNS) < -0.1 and lift_status == "up":
            lift.set_stopping(HOLD)
            lift_status = "stop"
            lift_stage = 2
            lift.stop()
        
        if lift_rotation.position(TURNS) > 0.99 and lift_status == "down":
            lift.stop()
            lift.set_stopping(COAST)
            lift_status = "stop"
            lift_stage = 0
            pto_status = 0
            pto.set(pto_status)
            
    #elevation
        if controller_1.buttonX.pressing():
            elevation_status = not elevation_status
            elevation.set(elevation_status)
            if clamp_status == 1:
                clamp_status = 0
                clamp.set(clamp_status)
            while controller_1.buttonX.pressing():
                wait(30, MSEC)

#choose team
team_position = team_choosing() 
inertial.calibrate()
# Compe tition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)