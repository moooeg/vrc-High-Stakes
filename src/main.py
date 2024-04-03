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

# Motors (A front, C back)
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)
right_motor_a = Motor(Ports.PORT2, GearSetting.RATIO_6_1, False)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

# Drivetrain
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 299.24, 260, 230, MM, 0.6)

# Sensor & Pneumatics

# Variables initialisation
left_drive_smart_stopped = 0
right_drive_smart_stopped = 0
left_drive_smart_speed = 0
right_drive_smart_speed = 0

# team and side choosing
def team_choosing():
    team = ""
    position = ""
    while True:
        if controller_1.buttonL1.pressing():
            brain.screen.draw_image_from_file( "red_offence_confirmed.png", 0, 4)
            while controller_1.buttonL1.pressing():
                wait(5, MSEC)
            return "red_offence"
        elif controller_1.buttonL2.pressing():
            brain.screen.draw_image_from_file( "red_defence_confirmed.png", 0, 4)
            while controller_1.buttonL2.pressing():
                wait(5, MSEC)
            return "red_defence"
        elif controller_1.buttonR1.pressing():
            brain.screen.draw_image_from_file( "blue_offence_confirmed.png", 0, 4)
            while controller_1.buttonR1.pressing():
                wait(5, MSEC)
            return "blue_offence"
        elif controller_1.buttonR2.pressing():
            brain.screen.draw_image_from_file( "blue_defence_confirmed.png", 0, 4)
            while controller_1.buttonR2.pressing():
                wait(5, MSEC)
            return "blue_defence"
        if brain.screen.pressing() and 8 <= brain.screen.y_position() <= 26:
            # Team choosing
            if 139 <= brain.screen.x_position() <= 240:
                # Red
                team = "red"
                brain.screen.draw_image_from_file( "red_begin.png", 0, 4)
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
                    # Red offence
                    brain.screen.draw_image_from_file( "red_offence.png", 0, 4)
                elif team == "blue":
                    # Blue offence
                    brain.screen.draw_image_from_file( "blue_offence.png", 0, 0)
                elif team == "skill":
                    # Skill confirm
                    brain.screen.draw_image_from_file( "skill_confirmed.png", 0, 0)
                    return "skill"
                position = "offence"
            elif brain.screen.pressing() and 85 <= brain.screen.y_position() <= 107 and not team == "":
                if team == "red":
                    # Red defence
                    brain.screen.draw_image_from_file( "red_defence.png", 0, 4)
                elif team == "blue":
                    # Blue defence
                    brain.screen.draw_image_from_file( "blue_defence.png", 0, 0)
                position = "defence"
            elif brain.screen.pressing() and 120 <= brain.screen.y_position() <= 142 and not team == "":
                if team == "red":
                    # Red confirm
                    if position == "offence":
                        # Red offence confirm
                        brain.screen.draw_image_from_file( "red_offence_confirmed.png", 0, 4)
                    elif position == "defence":
                        # Red defence confirm
                        brain.screen.draw_image_from_file( "red_defence_confirmed.png", 0, 4)
                elif team == "blue":
                    # Blue confirm
                    if position == "offence":
                        # Blue offence confirm
                        brain.screen.draw_image_from_file( "blue_offence_confirmed.png", 0, 0)
                    elif position == "defence":
                        # Blue defence confirm
                        brain.screen.draw_image_from_file( "blue_defence_confirmed.png", 0, 0)
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

# Autonomous def
def autonomous():
    pass

#  Driver Control def
def driver_control():
    global left_drive_smart_stopped, right_drive_smart_stopped
    drivetrain.set_stopping(COAST)
    # Process every 20 milliseconds
    while True:
    # Drive Train
        max_speed = 70
        rotate = max_speed*math.sin(((controller_1.axis4.position()**3)/636620))
            
        left_drive_smart_speed = forward + rotate
        right_drive_smart_speed = forward - rotate

        if left_drive_smart_speed < 3 and left_drive_smart_speed > -3:
            if left_drive_smart_stopped:
                left_drive_smart.stop()
                left_drive_smart_stopped = 0
        else:
            left_drive_smart_stopped = 1
        if right_drive_smart_speed < 3 and right_drive_smart_speed > -3:
            if right_drive_smart_stopped:
                right_drive_smart.stop()
                right_drive_smart_stopped = 0
        else:
            right_drive_smart_stopped = 1

        if left_drive_smart_stopped:
            left_drive_smart.set_velocity(left_drive_smart_speed, PERCENT)
            left_drive_smart.spin(FORWARD)
        if right_drive_smart_stopped:
            right_drive_smart.set_velocity(right_drive_smart_speed, PERCENT)
            right_drive_smart.spin(FORWARD)

#choose team
team_position = team_choosing() 
# Competition functions for the driver control & autonomous tasks
competition = Competition(driver_control, autonomous)
