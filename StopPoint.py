class StopPoint(object):
    def __init__(self, num, direction, link, offset, lineNum):
        self.num = num  # 停车点编号
        self.direction = direction  # 停车点作用方向
        self.link = link
        self.offset = offset
        self.lineNum = lineNum
        self.isStart = False
