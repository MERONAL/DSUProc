from StopArea import StopArea


class Station(object):
    def __init__(self, stationName, stationId):
        self.stationId = stationId
        self.stationName = stationName
        self.stopAreas = []