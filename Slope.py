class Slope(object):
    def __init__(self, slopeNum, linkStart, offsetStart, slopeNumStart, linkNumStart, linkEnd, offsetEnd, slopeNumEnd, linkNumEnd, slopeValue, direction):
        self.slopeNum = slopeNum
        self.linkStart = linkStart  # 坡度起始link
        self.offsetStart = offsetStart  # 坡度起始偏移量
        self.slopeNumStart = slopeNumStart  # 坡度起始点正线坡度
        self.linkNumStart = linkNumStart  # 坡度起始点正线link
        self.linkEnd = linkEnd
        self.offsetEnd = offsetEnd
        self.slopeNumEnd = slopeNumEnd
        self.linkNumEnd = linkNumEnd
        self.slopeValue = slopeValue
        self.direction = direction
