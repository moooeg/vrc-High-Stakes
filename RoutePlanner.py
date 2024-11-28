"""
Refer to https://wiki.purduesigbots.com/software/control-algorithms/basic-pure-pursuit

How to use:
import RoutePlanner as rp

path = [rp.Coordinate(100, 200), rp.Coordinate(72, -103)] // a list of Coordinate object
radius = 210 // look out distance

plan = rp.get_move_plan(path, radius) // plan is a list of dict
print(plan)
>> [[turning angle][distance]]
"""

from math import atan2, degrees


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


if __name__ == "__main__":
    class Inertial:
        def __init__(self, degrees):
            self.degrees = degrees
            
        def heading(self):
            return self.degrees
        
    class Drivetrain:
        def __init__(self):
            pass
        
        def turn(self, dir):
            self.dir = dir
            print(f"Dirve train dir set to {dir}")
            
        def set_turn_velocity(self, per):
            self.vel = per
            print(f"Drive train vel set to {per}")
        
        @staticmethod
        def stop():
            print("Stop")
            
    inertial = Inertial(0)
    drivetrain = Drivetrain()
            
    def inertial_turnto(target_angle: float):
        #change kp, ki, kd, accoding to the robot
        kp = 0.8
        ki = 0
        kd = 0
        previous_error = 0
        integral = 0
        false_condition_start_time = None
        false_condition_duration = 0
        current_angle = inertial.heading()
        right_off = (target_angle-current_angle+360)%360
        left_off = 360-right_off
        
        if right_off < left_off:
            drivetrain.turn(1) 
        else:
            drivetrain.turn(-1)
            
        while True:
            current_angle = inertial.heading()
            right_off = (target_angle - current_angle+360)%360
            left_off = 360-right_off
            if right_off > left_off:
                error = left_off
            else:
                error = - right_off
            integral += error
            integral = max(min(integral, 30), -30)
            derivative = error - previous_error
            pid_output = (kp * error) + (ki * integral) + (kd * derivative)
            previous_error = error
            pid_output = max(min(pid_output, 100), -100)
            drivetrain.set_turn_velocity(pid_output)
            if not (target_angle - 0.3 < current_angle < target_angle+0.3):
                # Reset the timer if the condition is false
                false_condition_start_time = None
            else:
                break
                # Start tracking time if the condition has just become false
                if false_condition_start_time is None:
                    false_condition_start_time = brain.timer.time(MSEC)
                else:
                    false_condition_duration = brain.timer.time(MSEC) - false_condition_start_time
            # Break the loop if the condition has been false for more than 0.5 seconds
            if false_condition_duration >= 50:
                break
            
            # temp
            inertial.degrees = (inertial.degrees + drivetrain.dir * drivetrain.vel * 0.5) % 360
            print(f"inertial degrees set to {inertial.degrees}")
            print("---------------------------------------")
            input()
            
        drivetrain.stop()
        
    inertial_turnto(181)
