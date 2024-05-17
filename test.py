class Coordinate:
    def __init__(self, x: float, y: float):
        self.x = round(x, 2)
        self.y = round(y, 2)

    def valid(self) -> bool:
        if self.x == -200000:
            return False
        return True

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


# Return the straight line distance between two points
def point_to_point_distance(point_one: Coordinate, point_two: Coordinate) -> float:
    return ((point_one.x - point_two.x) ** 2 + (point_one.y - point_two.y) ** 2) ** 0.5


path = [Coordinate(-1469.12, -747.93), Coordinate(-1091.23, -1382.63), Coordinate(820.2, -1400.9), Coordinate(1370.52, -990.07), Coordinate(1396.2, -634.2)]
lastPoint = 0
nextPoint = lastPoint + 1
currentPosition = path[0]
radius = 210

while True:
    # If next point in the search circle
    if point_to_point_distance(currentPosition, path[nextPoint]) <= radius:
        lastPoint += 1
        nextPoint += 1

    if lastPoint == len(path)-1:
        break

    intersection_one, intersection_two = line_circle_intersection(currentPosition, path[lastPoint], path[nextPoint], radius)

    if not intersection_one.valid() and not intersection_two.valid():
        # No intersection
        target = path[nextPoint]
    elif not intersection_one.valid():
        # One intersection (point two)
        target = intersection_two
    elif not intersection_two.valid():
        # One intersection (point one)
        target = intersection_one
    else:
        # Two intersection
        distance_one = point_to_point_distance(path[nextPoint], intersection_one)
        distance_two = point_to_point_distance(path[nextPoint], intersection_two)
        if distance_one < distance_two:
            target = intersection_one
        else:
            target = intersection_two

    if nextPoint == len(path)-1:
        target = path[nextPoint]

    print(f'Current position: {currentPosition}')
    print(f'Target position: {target}')
    print(f'Last point: {path[lastPoint]}')
    print(f'Next point: {path[nextPoint]}')
    print(f'Inter one: {intersection_one}')
    print(f'Inter two: {intersection_two}')
    currentPosition = target
    print('-------------------------------')