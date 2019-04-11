from Point import Point

class ChangePoint(Point):
    def __init__(self, link, offset, slope_value=None, limit_speed=None, slope_direction=None):
        Point.__init__(self, link, offset)
        self.slope = slope_value
        self.limit_speed = limit_speed
        self.slope_direction = slope_direction