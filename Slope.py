class Slope(object):
    def __init__(self, slopeNum, linkStart, offsetStart, slopeNumStart, linkEnd, offsetEnd, slopeNumEnd, slopeValue, direction):
        self.slopeNum = slopeNum
        self.linkStart = linkStart  # 坡度起始link
        self.offsetStart = offsetStart  # 坡度起始偏移量
        self.slopeNumStart = slopeNumStart  # 坡度起始点正线坡度
        self.linkEnd = linkEnd
        self.offsetEnd = offsetEnd
        self.slopeNumEnd = slopeNumEnd
        self.slopeValue = slopeValue
        self.direction = direction
