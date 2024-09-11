import RoutePlanner as rp
plan = rp.get_move_plan([rp.Coordinate(0, 0), rp.Coordinate(2, -10), rp.Coordinate(5, -4)], 3)
print(plan)