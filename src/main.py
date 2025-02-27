# Library imports
from vex import *

# ------------------------
# Code by Eric & Peter (mostly Eric)
# Team 75477M 'Frij'
# High Stakes 2024-2025
# ------------------------

# --------------------------------------
# Wiring Guide
# Updated: 2025-02-24

# Port 01 : Front left motor
# Port 02 : Middle left motor
# Port 03 : Back left motor
# Port 04 : Front right motor
# Port 05 : [BROKEN]
# Port 06 : [BROKEN]
# Port 07 : Radio
# Port 08 : Odometry
# Port 09 : Inertial top
# Port 10 : Inertial bottom
# Port 11 : Left PTO motor
# Port 12 : Right PTO motor
# Port 13 : -
# Port 14 : -
# Port 15 : -
# Port 16 : -
# Port 17 : -
# Port 18 : Middle right motor
# Port 19 : Back right motor
# Port 20 : -
# Port 21 : -

# Port A  : -
# Port B  : Goal clamp
# Port C  : -
# Port D  : Lift angle
# Port E  : PTO
# Port F  : -
# Port G  : -
# Port H  : -
# --------------------------------------

# Brain
brain=Brain()

# Controllers
controller_1 = Controller(PRIMARY)
controller_2 = Controller(PARTNER)

# Drivetrain (A front, C back)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, True)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
left_motor_c = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)

right_motor_a = Motor(Ports.PORT4, GearSetting.RATIO_18_1, False)
right_motor_b = Motor(Ports.PORT18, GearSetting.RATIO_18_1, False)
right_motor_c = Motor(Ports.PORT19, GearSetting.RATIO_18_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24 , 377.1, 304.8, MM, 5/3)

# PTO
left_lift = Motor(Ports.PORT11, GearSetting.RATIO_18_1, False)
right_lift = Motor(Ports.PORT12, GearSetting.RATIO_18_1, True)
lift = MotorGroup(left_lift, right_lift)

# Autonomous: Inertial (1 top, 2 bottom), odometry & auto-clamping
imu_1 = Inertial(Ports.PORT9 )
imu_2 = Inertial(Ports.PORT10)
odometry = Rotation(Ports.PORT8, False)
clamp_distance = Distance(Ports.PORT13) # CHANGE PORT

# Pneumatics (3-pin)
clamp = DigitalOut(brain.three_wire_port.b)
change_name = DigitalOut(brain.three_wire_port.c) # CHANGE VAR NAME
lift_angle = DigitalOut(brain.three_wire_port.d)
pto = DigitalOut(brain.three_wire_port.e)

# ---------------------- DELETE --------------------------
intake = Motor(Ports.PORT9, GearSetting.RATIO_6_1, False)
odometry_turn = Rotation(Ports.PORT14, False)
lift_rotation = Rotation(Ports.PORT16, False)
optical = Optical(Ports.PORT17)
distance = Distance(Ports.PORT15)
# --------------------------------------------------------

# Variables initialisation
left_drive_smart_stopped = 0
right_drive_smart_stopped = 0
left_drive_smart_speed = 0
right_drive_smart_speed = 0

pto_status = 0 # 0 drivebase, 1 lift
clamp_status = False # 0 release, 1 clamp
lift_status = "stop" # 'up', 'down' and 'stop' (direction of lift)
lift_stage = 0 # 0 low, 2 high
lift_angle_status = 0 # 0 low angle, 1 high angle

# DELETE : ring sort
ring_sort_status = "Both" # 'Red', 'Blue' and 'Both'
storage = []

# Controller screen print
def cprint(_input: Any):
    s = str(_input)
    controller_1.screen.clear_screen()
    controller_1.screen.set_cursor(1,1)
    controller_1.screen.print(s)

# SS GUI init
brain.screen.draw_image_from_file("begin.png", 0, 0)

# Side Selection GUI
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

def curvature(radius, speed, direction: TurnType, target_turns, time): #all units in inches
    #change accoding to the robot
    track_width = 0.5
    kp = 0.75
    ki = 0.11
    false_condition_start_time = brain.timer.time(MSEC)
    time_integral = 0
    left_drive_smart.spin(FORWARD)
    right_drive_smart.spin(FORWARD)
    while True:
        time_left = false_condition_start_time+time-brain.timer.time(MSEC)
        time_integral+=time_left
        time_integral = max(min(time_integral, 100), -100)
        pid_output = (speed/100)*(kp*time_left) + (ki*time_integral)
        if direction == LEFT:
            left_drive_smart.set_velocity(speed*pid_output*(radius-(track_width/2)))
            right_drive_smart.set_velocity(speed*pid_output*(radius+(track_width/2)))
        else:
            left_drive_smart.set_velocity(speed*pid_output*(radius+(track_width/2)))
            right_drive_smart.set_velocity(speed*pid_output*(radius-(track_width/2)))
        if time_left < 0:
            drivetrain.stop()
    
# PID turn def
def inertial_turnto(target_angle: float):
    #change kp, ki, kd, accoding to the robot
    kp = 0.75
    ki = 0.11
    kd = 0.4
    previous_error = 0
    integral = 0
    false_condition_start_time = None
    false_condition_duration = 0
    current_angle = (imu_1.heading(DEGREES)+abs(imu_2.heading(DEGREES)-360))/2
    right_off = (target_angle-current_angle+360)%360
    left_off = 360-right_off
    while True:
        current_angle = (imu_1.heading(DEGREES)+abs(imu_2.heading(DEGREES)-360))/2
        right_off = (target_angle - current_angle+360)%360
        left_off = 360-right_off
        if right_off > left_off:
            error = left_off
            drivetrain.turn(LEFT)
        else:
            error = right_off
            drivetrain.turn(RIGHT) 
        integral += error
        integral *= 0.95
        derivative = error - previous_error
        pid_output = (kp * error) + (ki * integral) + (kd * derivative)
        previous_error = error
        pid_output = max(min(pid_output, 100), -100)
        drivetrain.set_turn_velocity(pid_output, PERCENT)
        
        if not (target_angle - 1 < current_angle < target_angle + 1):
            false_condition_start_time = None
        else:
            if false_condition_start_time == None:
                false_condition_start_time = brain.timer.time(MSEC)
            elif false_condition_start_time + 100 <= brain.timer.time(MSEC):
                break
    drivetrain.stop()
    imu_1.set_heading(target_angle)
    imu_2.set_heading(abs(target_angle-360))

# odometry def
def drivetrain_forward(target_turns: float, speed=100, time_out=0, unit: str = "turns"):
    movement_start_time = brain.timer.time(MSEC)
    if unit == "mm":
        target_turns = target_turns / 159.59
    kp = 40
    ki = 0.03
    kd = 1
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
        integral *= 0.95
        derivative = error - previous_error
        odometry_output = (kp * error) + (ki * integral) + (kd * derivative)
        previous_error = error
        odometry_output = (speed/100)*max(min(odometry_output, 100), -100)
        drivetrain.set_drive_velocity(odometry_output, PERCENT)
        current_turns = odometry.position(TURNS)
        if not (target_turns - 0.5 < current_turns - initial_turns < target_turns+0.2):
            # Reset the timer if the condition is false
            false_condition_start_time = None
        else:
            if false_condition_start_time == None:
                false_condition_start_time = brain.timer.time(MSEC)
            elif false_condition_start_time + 100 <= brain.timer.time(MSEC):
                break
        if movement_start_time-brain.timer.time(MSEC) > time_out and time_out > 0:
            break
    drivetrain.stop()

def drivetrain_turn(target_turns: float, speed=100, time_out = 0):
    movement_start_time = brain.timer.time(MSEC)
    kp = 57
    ki = 0.02
    kd = 25
    previous_error = 0
    integral = 0
    drivetrain.turn(RIGHT)
    initial_turns = odometry_turn.position(TURNS)
    current_turns = odometry_turn.position(TURNS)
    false_condition_start_time = None
    false_condition_duration = 0
    while True:
        error = target_turns - (current_turns - initial_turns)
        integral += error
        integral = max(min(integral, 30), -30)
        derivative = error - previous_error
        odometry_output = (kp * error) + (ki * integral) + (kd * derivative)
        previous_error = error
        odometry_output = (speed/100)*max(min(odometry_output, 100), -100)
        drivetrain.set_turn_velocity(odometry_output, PERCENT)
        current_turns = odometry_turn.position(TURNS)
        if not (target_turns - 0.2 < current_turns - initial_turns < target_turns+0.2):
            # Reset the timer if the condition is false
            false_condition_start_time = None
        else:
            # Start tracking time if the condition has just become false
            if false_condition_start_time is None:
                false_condition_start_time = brain.timer.time(MSEC)
            else:
                false_condition_duration = brain.timer.time(MSEC) - false_condition_start_time

        # Break the loop if the condition has been false for more than 0.5 seconds
        if false_condition_duration >= 50:
            break
        elif movement_start_time-brain.timer.time(MSEC) > time_out and time_out > 0:
            break
    drivetrain.stop()

# ring holding list def
def add_color(new_color):
    if len(storage) >= 2:
        storage.pop(0)  # Remove the first color if the list is full
    storage.append(new_color)

#auto clamp def
def goal_clamp():
    global clamp_status
    while True:
        if controller_1.buttonL2.pressing():
            clamp_status = not clamp_status
            clamp.set(clamp_status)
            while controller_1.buttonL2.pressing():
                wait(500, MSEC)
        elif clamp_status == False and clamp_distance.object_distance() < 17:
            clamp_status = True
            clamp.set(clamp_status)
        elif clamp_status == True and clamp_distance.object_distance() > 34:
            clamp_status = False
            clamp.set(clamp_status)
             
#ring sorting function
def ring_sorting_auto(colour):
    while True:
        if 0 < optical.hue() < 30:
            add_color("RED")
        if 160.0 < optical.hue() < 250.0: # type: ignore
            add_color("BLUE")
        if colour == "RED":
            if distance.object_distance() < 15.0 and len(storage) > 0 and storage[0] == "RED":
                intake.set_velocity(100, PERCENT)
                wait(100, MSEC)
                intake.spin_for(REVERSE, 2, TURNS)
                while distance.object_distance() < 15.0:
                    wait(30, MSEC)
                storage.pop(0)
        elif colour == "BLUE":
            if distance.object_distance() < 15.0 and len(storage) > 0 and storage[0] == "BLUE":
                intake.set_velocity(100, PERCENT)
                wait(100, MSEC)
                intake.spin_for(REVERSE, 2, TURNS)
                while distance.object_distance() < 15.0:
                    wait(30, MSEC)
                storage.pop(0)
                
def ring_sorting():
    while True:
        if False:
            if controller_1.buttonR1.pressing():
                intake.spin(FORWARD, 100, PERCENT)
            elif controller_1.buttonR2.pressing():
                intake.spin(REVERSE, 100, PERCENT)
            else:
                intake.stop()
        else:
            if controller_1.buttonR1.pressing() and not controller_1.buttonR2.pressing(): # normal intake filter
                intake.spin(FORWARD, 100, PERCENT)
                if ring_sort_status == "RED":
                    if distance.object_distance() < 15.0 and len(storage) > 0 and storage[0] == "RED":
                        wait(50, MSEC)
                        intake.set_velocity(100, PERCENT)
                        intake.spin_for(REVERSE, 2, TURNS)
                        while distance.object_distance() < 15.0:
                            wait(10, MSEC)
                        storage.pop(0)
                elif ring_sort_status == "BLUE":
                    if distance.object_distance() < 15.0 and len(storage) > 0 and storage[0] == "BLUE":
                        wait(50, MSEC)
                        intake.set_velocity(100, PERCENT)
                        intake.spin_for(REVERSE, 2, TURNS)
                        while distance.object_distance() < 15.0:
                            wait(10, MSEC)
                        storage.pop(0)
            elif controller_1.buttonR2.pressing() and not controller_1.buttonR1.pressing(): # wall goal intake filter
                intake.spin(FORWARD, 100, PERCENT)
                if ring_sort_status == "RED":
                    if distance.object_distance() < 30.0 and len(storage) > 0 and storage[0] == "BLUE":
                        intake.set_velocity(100, PERCENT)
                        intake.spin_for(REVERSE, 6, TURNS)
                        while distance.object_distance() < 15.0:
                            wait(30, MSEC) 
                        storage.pop(0)
                    if distance.object_distance() < 15.0 and len(storage) > 0 and storage[0] == "RED":
                        intake.set_velocity(100, PERCENT)
                        wait(80, MSEC)
                        intake.spin_for(REVERSE, 2, TURNS)
                        while distance.object_distance() < 15.0:
                            wait(30, MSEC)
                        storage.pop(0)
                elif ring_sort_status == "BLUE":
                    if distance.object_distance() < 30.0 and len(storage) > 0 and storage[0] == "RED":
                        intake.set_velocity(100, PERCENT)
                        intake.spin_for(REVERSE, 6, TURNS)
                        while distance.object_distance() < 15.0:
                            wait(30, MSEC) 
                        storage.pop(0)
                    if distance.object_distance() < 15.0 and len(storage) > 0 and storage[0] == "BLUE":
                        intake.set_velocity(100, PERCENT)
                        wait(80, MSEC)
                        intake.spin_for(REVERSE, 2, TURNS)
                        while distance.object_distance() < 15.0:
                            wait(30, MSEC)
                        storage.pop(0)
            elif controller_1.buttonR1.pressing() and controller_1.buttonR2.pressing():
                intake.spin(REVERSE, 100, PERCENT)
            elif not controller_1.buttonR1.pressing() or not controller_1.buttonR2.pressing():
                intake.stop()

#lift up auto def
def lift_up(height):
    pto.set(True)
    wait(0.2, SECONDS)
    lift.spin(REVERSE, 100, PERCENT)
    while lift_rotation.position(TURNS) > height:
       wait(50, MSEC)
    lift.set_stopping(HOLD)
    lift.stop()

# Autonomous def
def autonomous(): #2 share goal side, 1 share ring side
    global ring_sort_status, clamp_status
    intake.set_velocity(100, PERCENT)
    if team_position == "red_1":
        pass

    if team_position == "red_2":
        pass
        
    if team_position == "blue_1":
        pass
             
    if team_position == "blue_2":
        pass
        
    if team_position == "skill":
        pass
        
#  Driver Control def
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped, pto_status, clamp_status, lift_status, lift_stage, ring_sort_status, lift_angle_status, ring_sort_status, storage
    drivetrain.set_stopping(COAST)
    lift_status = 0
    integral_rotate = 0
    brain.timer.clear()
    intake.set_velocity(100, PERCENT)
    if team_position == "red_1" or team_position == "red_2":
        ring_sort_status = "BLUE"
    elif team_position == "blue_1" or team_position == "blue_2":
        ring_sort_status = "RED"
    elif team_position == "skill":
        ring_sort_status = "BLUE"
        intake.spin(FORWARD)
        wait(0.36, SECONDS)
        intake.stop()
    Thread(ring_sorting)
    Thread(goal_clamp)
    # Process every 20 milliseconds
    while True:
    # Status Update
        pto.set(pto_status)
    # Drive Train(integral)
        ratio = 1  # Bigger the number, less sensitive
        integral_decay_rate = 0.000003  # Rate at which integral decays
        forward = 100 * math.sin(((controller_1.axis3.position()**3) / 636620))
        if controller_1.axis3.position() < 0:
            forward = 0.8 * forward
        rotate_dynamic = (100 / ratio) * math.sin((abs((forward**3)) / 636620)) * math.sin(((controller_1.axis1.position()**3) / 636620))
        rotate_linear = 70 * math.sin(((controller_1.axis1.position()**3) / 636620))
        rotate_linear_lift = 35 * math.sin(((controller_1.axis1.position()**3) / 636620))
        max_integral_limit = 0.4*rotate_dynamic
        
        # Accumulate integral when joystick is pushed
        if abs(controller_1.axis1.position()) >= 30:
            integral_rotate += rotate_dynamic * integral_decay_rate
            if integral_rotate > 0:
                integral_rotate = min(integral_rotate, max_integral_limit)  # Cap the integral value
            elif integral_rotate < 0:
                integral_rotate = max(integral_rotate, max_integral_limit)
        else:
            integral_rotate = 0  # Reset the integral when joystick is back below 30

        # Add integral component to turning calculation
        if -30 <= forward <= 30:
            if lift_stage != 0:
                left_drive_smart_speed = forward + rotate_linear_lift
                right_drive_smart_speed = forward - rotate_linear_lift
            else:
                left_drive_smart_speed = forward + rotate_linear
                right_drive_smart_speed = forward - rotate_linear
        else:
            # Use the integral component
            left_drive_smart_speed = forward + rotate_dynamic - integral_rotate
            right_drive_smart_speed = forward - rotate_dynamic + integral_rotate

        if abs(left_drive_smart_speed) < 3:
            if left_drive_smart_stopped:
                if pto_status == 0:
                    left_lift.stop()
                left_drive_smart.stop()
                left_drive_smart_stopped = 0
        else:
            left_drive_smart_stopped = 1

        if abs(right_drive_smart_speed) < 3:
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
            right_drive_smart.set_velocity(right_drive_smart_speed, PERCENT)
            if pto_status == 0:
                right_lift.set_velocity(right_drive_smart_speed, PERCENT)
                right_lift.spin(FORWARD)
            right_drive_smart.spin(FORWARD)
            
    #intake color sensor
        if optical.color() == Color.RED:
            add_color("RED")
        if 160.0 < optical.hue() < 250.0: # type: ignore
            add_color("BLUE")
        
            
    # lift contol
        if controller_1.axis2.position() > 95 and lift_stage == 0:
            lift_status = "up"
            pto_status = 1
            pto.set(pto_status)
            wait(50, MSEC)
            lift.spin(REVERSE, 100, PERCENT)
        if controller_1.axis2.position() < -95 and lift_stage == 1:
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
        if lift_rotation.position(TURNS) < 0.3 and lift_status == "up":
            lift.set_stopping(HOLD)
            lift_status = "stop"
            lift_stage = 1
            lift.stop()
        
        if lift_rotation.position(TURNS) > 1 and lift_status == "down":
            lift.stop()
            lift.set_stopping(COAST)
            lift_status = "stop"
            lift_stage = 0
            pto_status = 0
            pto.set(pto_status)
            
    # Lift angle control
        if controller_1.buttonX.pressing():
            lift_angle_status = not lift_angle_status
            lift_angle.set(lift_angle_status)
            if clamp_status == 1:
                clamp_status = 0
                clamp.set(clamp_status)
            while controller_1.buttonX.pressing():
                wait(30, MSEC)

    # thing
        if controller_1.axis2.position() > 95:
            lift.spin(REVERSE, 70, PERCENT)
        elif controller_1.axis2.position() < -95:
            lift.spin(FORWARD, 70, PERCENT)
        else:
            lift.stop()
    
    #skill blue alliance stake

#choose team
team_position = team_choosing()
imu_1.calibrate()
imu_2.calibrate()
while imu_1.calibrate():
    wait(50, MSEC) 
# Compe tition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)