class StopArea(object):
    def __init__(self, num, stationName, link, n_stopPoint, lineNum, belongToStationId):
        self.num = num  # 停车区域编号
        self.stationName = stationName  # 所属车站名称
        self.link = link  # 所属link
        self.n_stopPoint = n_stopPoint  # 停车点数目
        self.lineNum = lineNum
        self.belongToStationId = belongToStationId
        self.stopPoints = []
