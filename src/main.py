# Library imports
from vex import *

# ------------------------
# Code by Eric & Peter (mostly Eric)
# Team 75477M 'Frij'
# High Stakes 2024-2025
# ------------------------

# --------------------------------------
# Wiring Guide
# Updated: 2025-03-27

# Port 01 : RF Motor
# Port 02 : intake stage 2
# Port 03 : -
# Port 04 : -
# Port 05 : [BROKEN]
# Port 06 : [BROKEN]
# Port 07 : -
# Port 08 : -
# Port 09 : intake stage 1
# Port 10 : L PTO Motor
# Port 11 : R PTO Motor
# Port 12 : RB Motor
# Port 13 : -
# Port 14 : -
# Port 15 : -
# Port 16 : -
# Port 17 : lift rotation
# Port 18 : LF Motor
# Port 19 : LB Motor
# Port 20 : [BROKEN]
# Port 21 : Radio

# Port A  : Intake Lift [SOLENOID RB]
# Port B  : Elevation   [SOLENOID RT]
# Port C  : PTO         [SOLENOID LB]
# Port D  : Goal Clamp  [SOLENOID LT]
# Port E  : -
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
left_motor_a = Motor(Ports.PORT18, GearSetting.RATIO_18_1, True)
left_motor_b = Motor(Ports.PORT19, GearSetting.RATIO_18_1, False)
# left_motor_c = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
left_drive_smart = MotorGroup(left_motor_a,  left_motor_b)

right_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_motor_b = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)
# right_motor_c = Motor(Ports.PORT19, GearSetting.RATIO_18_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b)

drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24 , 377.1, 304.8, MM, 5/3)

# PTO
left_lift = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
right_lift = Motor(Ports.PORT11, GearSetting.RATIO_18_1, True)
lift = MotorGroup(left_lift, right_lift)

# Autonomous: Inertial (1 top, 2 bottom), odometry & auto-clamping
imu_1 = Inertial(Ports.PORT16)
imu_2 = Inertial(Ports.PORT17)
odometry = Rotation(Ports.PORT8, False)
clamp_distance = Distance(Ports.PORT13) # CHANGE PORT

# Pneumatics (3-pin)
intake_lift = DigitalOut(brain.three_wire_port.a)
elevation = DigitalOut(brain.three_wire_port.b)
pto = DigitalOut(brain.three_wire_port.c)
clamp = DigitalOut(brain.three_wire_port.d)

intake1 = Motor(Ports.PORT9, GearSetting.RATIO_6_1, False)
intake2 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
odometry_turn = Rotation(Ports.PORT14, False)
lift_rotation = Rotation(Ports.PORT17, False)
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

# Controller screen print
def cprint(_input: Any):
    s = str(_input)
    controller_1.screen.clear_screen()
    controller_1.screen.set_cursor(1,1)
    controller_1.screen.print(s)

# SS GUI init
brain.screen.draw_image_from_file("begin.png", 0, 0)

# Side Selection GUI
class ButtonPosition:
    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        x1, y1: top left

        x2, y2: bottom right
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def pressing(self, x: int, y: int) -> bool:
        """
        Return true if the passed x and y coordinate is inside this button
        """
        return (self.x1 <= x <= self.x2) and (self.y1 <= y <= self.y2)

GUI_BUTTONS_POSITIONS = {
    "top": {
        "1": ButtonPosition(139, 8, 240, 26),
        "2": ButtonPosition(249, 8, 351, 26),
        "3": ButtonPosition(358, 8, 461, 26)
    },
    "side": {
        "1": ButtonPosition(19, 52, 138, 73),
        "2": ButtonPosition(19, 85, 138, 107),
        "3": ButtonPosition(19, 120, 138, 142)
    }
}

def wait_until_release(button, time) -> None:
    """
    Block until the passed button is no longer pressed

    Args:
        button (Button): the button to be listen, chould be anything with a "pressing" method
        time: time to wait in ms
    """
    while button.pressing():
        wait(time, MSEC)

# Side Selection GUI
def team_choosing() -> str:
    """
    Start choosing team, can use controller button to select or use GUI on brain.

    Returns:
        str: Literal [ "red_1", "red_2", "blue_1", "blue_2", "skill" ]
    """
    # SS GUI init
    brain.screen.draw_image_from_file("begin.png", 0, 0)

    team = ""
    position = ""
    confirmed = False

    while True:
        wait(5, MSEC)

        # exit
        if confirmed:
            brain.screen.draw_image_from_file(team+position+"_confirmed.png", 0, 0)
            return team + position

        # controller
        if controller_1.buttonL1.pressing():
            team = "red"
            position = "_1"
            confirmed = True
        elif controller_1.buttonL2.pressing():
            team = "red"
            position = "_2"
            confirmed = True
        elif controller_1.buttonR1.pressing():
            team = "blue"
            position = "_1"
            confirmed = True
        elif controller_1.buttonR2.pressing():
            team = "blue"
            position = "_2"
            confirmed = True

        # brain
        if brain.screen.pressing():
            x = brain.screen.x_position()
            y = brain.screen.y_position()

            if GUI_BUTTONS_POSITIONS["top"]["1"].pressing(x, y):
                team = "red"
                position = ""
                brain.screen.draw_image_from_file("red_begin.png", 0, 0)
            elif GUI_BUTTONS_POSITIONS["top"]["2"].pressing(x, y):
                team = "blue"
                position = ""
                brain.screen.draw_image_from_file("blue_begin.png", 0, 0)
            elif GUI_BUTTONS_POSITIONS["top"]["3"].pressing(x, y):
                team = "skill"
                position = ""
                brain.screen.draw_image_from_file("skill_begin.png", 0, 0)

            if team:
                if GUI_BUTTONS_POSITIONS["side"]["1"].pressing(x, y):
                    if team == "skill":
                        confirmed = True
                    else:
                        position = "_1"
                        brain.screen.draw_image_from_file(team+"_1.png", 0, 0)
                elif GUI_BUTTONS_POSITIONS["side"]["2"].pressing(x, y) and team != "skill":
                    position = "_2"
                    brain.screen.draw_image_from_file(team+"_2.png", 0, 0)
                elif GUI_BUTTONS_POSITIONS["side"]["3"].pressing(x, y) and position and team != "skill":
                    confirmed = True
            
            wait_until_release(brain.screen, 50)

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

#ladybrown def
def ladybrown():
    stage = 0 #0: down, 1: loading, 2: over the top
    lift_status = "stop"
    while True:
        if controller_1.axis2.position() > 95:  
            if stage == 0:  # Move from Stage 0 to Stage 1
                lift_status = "up"
                pto_status = 1
                stage = 1
                pto.set(pto_status)
                lift.spin(REVERSE, 100, PERCENT)
                while controller_1.axis2.position() > 95:
                    wait(50, MSEC)
            elif stage == 1:  # Move from Stage 1 to Stage 2
                lift_status = "up"
                lift.spin(REVERSE, 100, PERCENT)

        if lift_rotation.position(TURNS) > 1.23 and lift_status == "up" and stage == 1:
            lift.set_stopping(HOLD)
            lift_status = "stop"
            stage = 2
            lift.stop()

        if controller_1.axis2.position() < 10 and stage == 2:  # Release joystick → Move to Stage 1
            lift_status = "down"
            lift.spin(FORWARD, 80, PERCENT)

        if lift_rotation.position(TURNS) < 1.23 and lift_status == "down" and stage == 2:
            lift.set_stopping(HOLD)
            lift_status = "stop"
            stage = 1
            lift.stop()

        if controller_1.axis2.position() < -95 and stage == 1:  # Pull joystick down → Move to Stage 0
            lift_status = "down"
            lift.spin(FORWARD, 80, PERCENT)

        if lift_rotation.position(TURNS) < 1.01 and lift_status == "down" and stage == 1:
            lift_status = "stop"
            lift.set_stopping(COAST)
            lift.stop()
            pto_status = 0
            stage = 0
            pto.set(pto_status)
        '''
        if controller_1.axis2.position() > 95 and stage == 0:
            lift_status = "up"
            pto_status = 1
            pto.set(pto_status)
            wait(50, MSEC)
            lift.spin(REVERSE, 100, PERCENT)
        if controller_1.axis2.position() < -95 and (stage == 1 or stage == 2):
            lift_status = "down"
            lift.spin(FORWARD, 80, PERCENT)
        
        if (lift_rotation.position(TURNS) > 1.23 and lift_status == "up" and stage == 0) or (lift_rotation.position(TURNS) <1.23 and lift_status == "down" and stage == 2):
            lift.set_stopping(HOLD)
            lift_status = "stop"
            stage = 1
            lift.stop()
            
        if lift_rotation.position(TURNS) > 4 and lift_status == "up" and stage == 1:
            lift.set_stopping(HOLD)
            lift_status = "stop"
            stage = 2
            lift.stop()
            
        if lift_rotation.position(TURNS) < 1.01 and lift_status == "down" and stage == 1:
            lift_status = "stop"
            lift.set_stopping(COAST)
            lift.stop()
            pto_status = 0
            stage = 0
            pto.set(pto_status)
        '''
 
#auto clamp def
def goal_clamp():
    global clamp_status
    while True:
        if controller_1.buttonL2.pressing():
            clamp_status = not clamp_status
            clamp.set(clamp_status)
            wait_until_release(controller_1.buttonL2, 50)
#intake def            
def intake():
    while True:
        if controller_1.buttonR2.pressing():
            intake1.spin(FORWARD)
            intake2.spin(FORWARD)
            if intake1.torque() > 2:
                intake1.stop()
                wait_until_release(controller_1.buttonR2, 50)
            if intake2.torque() > 2:
                intake2.stop()
                wait_until_release(controller_1.buttonR2, 50)
        elif controller_1.buttonR1.pressing():
            intake1.spin(REVERSE)
            intake2.spin(REVERSE)
            if intake1.torque() > 2:
                intake1.stop()
                wait_until_release(controller_1.buttonR2, 50)
            if intake2.torque() > 2:
                intake2.stop()
                wait_until_release(controller_1.buttonR2, 50)
        else:
            intake1.stop()
            intake2.stop()


# Autonomous def
def autonomous(): #2 share goal side, 1 share ring side
    global ring_sort_status, clamp_status
    intake1.set_velocity(100, PERCENT)
    intake2.set_velocity(90, PERCENT)
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
    intake1.set_velocity(100, PERCENT)
    intake2.set_velocity(90, PERCENT)
    if team_position == "red_1" or team_position == "red_2":
        ring_sort_status = "BLUE"
    elif team_position == "blue_1" or team_position == "blue_2":
        ring_sort_status = "RED"
    elif team_position == "skill":
        ring_sort_status = "BLUE"
        
    Thread(intake)
    Thread(goal_clamp)
    Thread(ladybrown)
    # Process every 20 milliseconds
    while True:
    # Status Update
        pto.set(pto_status)
    # Drive Train(integral)
        ratio = 1.15  # Bigger the number, less sensitive
        integral_decay_rate = 0.000003  # Rate at which integral decays
        forward = 100 * math.sin(((controller_1.axis3.position()**3) / 636620))
        if controller_1.axis3.position() < 0:
            forward = 0.8 * forward
        rotate_dynamic = (100 / ratio) * math.sin((abs((forward**3)) / 636620)) * math.sin(((controller_1.axis1.position()**3) / 636620))
        rotate_linear = 40 * math.sin(((controller_1.axis1.position()**3) / 636620))
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

#choose team
team_position = team_choosing()
imu_1.calibrate()
imu_2.calibrate()
while imu_1.calibrate():
    wait(50, MSEC) 
# Compe tition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)