class LimitSection(object):
    def __init__(self, sectionNum, lineNum, startOffset, endOffset, link, limitSpeed):
        self.sectionNum = sectionNum
        self.lineNum = lineNum  # 在表中所处行数
        self.startOffset = startOffset
        self.endOffset = endOffset
        self.link = link
        self.limitSpeed = limitSpeed
