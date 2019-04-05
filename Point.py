class Point(object):
    def __init__(self, link, offset):
        self.link = link
        self.offset = offset
        self.slope = None
        self.slope_direction = None
        self.limit_speed = None
