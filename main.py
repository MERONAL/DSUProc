import xlrd
from StopArea import StopArea
from Station import Station
from StopPoint import StopPoint
from Slope import Slope
from Point import Point

'''根据站名初始化各车站、停车区域、停车点信息'''
def init_all_info(startStation, endStation):
    # 查找停车区域
    # 条件:停车区域站台轨属性需要为1
    StartStationStopArea = find_stop_area_by_station_name(startStation)
    find_stop_points_by_stop_area(StartStationStopArea)

    EndStationStopArea = find_stop_area_by_station_name(endStation)
    find_stop_points_by_stop_area(EndStationStopArea)

    StartStation = Station(stationName=startStation, stationId=StartStationStopArea[0].belongToStationId)
    StartStation.stopAreas = StartStationStopArea

    EndStation = Station(stationName=endStation, stationId=EndStationStopArea[0].belongToStationId)
    EndStation.stopAreas = EndStationStopArea
    return StartStation, EndStation


def find_stop_area_by_station_name(name):
    sheet_stop_area = file.sheet_by_name('停车区域表')
    total_line_num = int(sheet_stop_area.col_values(5)[1])
    stationNames = sheet_stop_area.col_values(1)[4:total_line_num + 4]  # 第二列内容
    _stop_areas = []
    for index, stationName in enumerate(stationNames):
        if name == stationName:
            # 判断停车区域属性是否包括站台轨属性
            if int(sheet_stop_area.col_values(4)[index + 4]) & 0x0001:
                num_stop_area = int(sheet_stop_area.col_values(0)[index + 4])  # 停车区域编号
                num_stop_point = int(sheet_stop_area.col_values(14)[index + 4])  # 停车点数目
                # print(sheet.col_values(15)[index + 4])  # 停车点编号
                link = int(sheet_stop_area.col_values(3)[index + 4])  # 停车点link
                belong_to_station_id = int(sheet_stop_area.col_values(23)[index + 4])  # 停车点所属车站ID
                _stop_areas.append(StopArea(num=num_stop_area,
                                          stationName=stationName,
                                          link=link,
                                          n_stopPoint=num_stop_point,
                                            lineNum=index + 4,
                                            belongToStationId=belong_to_station_id))
    return _stop_areas

def find_stop_points_by_stop_area(_stop_areas):
    if len(_stop_areas) == 0:
        return None
    sheet_stop_area = file.sheet_by_name('停车区域表')
    sheet_stop_point = file.sheet_by_name('停车点表')
    total_line_num = int(sheet_stop_point.col_values(5)[1])
    stopPointNums = list(map(int,sheet_stop_point.col_values(0)[4:total_line_num + 4]))  # 第一列
    for stop_area in _stop_areas:
        for n in range(stop_area.n_stopPoint):
            num_stop_point = int(sheet_stop_area.col_values(15 + n)[stop_area.lineNum])  # 停车点编号
            # 匹配停车点类型，必须是运营停车点
            for index, stopPoint in enumerate(stopPointNums):
                if num_stop_point == stopPoint:
                    direction_stop_point = 0xaa if sheet_stop_point.col_values(2)[index + 4] == '0xaa' else 0x55
                    link = int(sheet_stop_point.col_values(3)[index + 4])
                    offset = int(sheet_stop_point.col_values(4)[index + 4])
                    stop_area.stopPoints.append(StopPoint(num=num_stop_point,
                                                          direction=direction_stop_point,
                                                          link=link,
                                                          offset=offset,
                                                          lineNum=index))


def find_platform_name_by_stop_area(stop_area):
    sheet_platform = file.sheet_by_name('站台表')
    total_line_num = int(sheet_platform.col_values(5)[1])
    stopAreaNums = list(map(int, sheet_platform.col_values(2)[4:total_line_num + 4]))  # 第一列
    for index, stopArea in enumerate(stopAreaNums):
        if stop_area.num == stopArea:
            return sheet_platform.col_values(15)[index + 4]


def find_start_and_end_point_by_stations(operation_direction, StartStation, EndStation):
    StartStationStopPoint = None
    EndStationStopPoint = None
    # 查找起始站停车点
    if operation_direction == 0xaa:  # 下行方向
        for stopArea in StartStation.stopAreas:
            platform_name = find_platform_name_by_stop_area(stopArea)
            if '下行' in platform_name:
                for stopPoint in stopArea.stopPoints:
                    if 0xaa == stopPoint.direction:  # 找到了该车站在该方向上的停车点
                        StartStationStopPoint = stopPoint
                        break
    else:
        for stopArea in StartStation.stopAreas:  # 上行方向
            platform_name = find_platform_name_by_stop_area(stopArea)
            if '上行' in platform_name:
                for stopPoint in stopArea.stopPoints:
                    if 0x55 == stopPoint.direction:  # 找到了该车站在该方向上的停车点
                        StartStationStopPoint = stopPoint
                        break
    # 查找终止站停车点
    if operation_direction == 0xaa:  # 下行方向
        for stopArea in EndStation.stopAreas:
            platform_name = find_platform_name_by_stop_area(stopArea)
            if '下行' in platform_name:
                for stopPoint in stopArea.stopPoints:
                    if 0xaa == stopPoint.direction:  # 找到了该车站在该方向上的停车点
                        EndStationStopPoint = stopPoint
                        break
    else:
        for stopArea in EndStation.stopAreas:  # 上行方向
            platform_name = find_platform_name_by_stop_area(stopArea)
            if '上行' in platform_name:
                for stopPoint in stopArea.stopPoints:
                    if 0x55 == stopPoint.direction:  # 找到了该车站在该方向上的停车点
                        EndStationStopPoint = stopPoint
                        break
    return StartStationStopPoint, EndStationStopPoint

def find_start_link(sheetlink, linkNums, start_link):
    for index, link in enumerate(linkNums):
        if link == start_link:
            return int(sheetlink.col_values(9)[index + 4])

def find_links_between_two_points(direction, StartPoint, EndPoint):
    # 根据link表设置需要从前往后找
    links = []
    start_link = StartPoint.link if direction != 0xaa else EndPoint.link
    end_link = EndPoint.link if direction != 0xaa else StartPoint.link
    links.append(start_link)  # 添加起始link
    if start_link == end_link:
        return links
    sheet_link = file.sheet_by_name('Link表')
    total_line_num = int(sheet_link.col_values(5)[1])
    linkNums = list(map(int, sheet_link.col_values(0)[4:total_line_num + 4]))  # 第一列
    next_link = find_start_link(sheet_link, linkNums, start_link)
    links.append(next_link)
    while next_link != end_link:
        next_link = find_start_link(sheet_link, linkNums, next_link)
        links.append(next_link)
    return links


def isBetweenTwoPoints(StopPoint, StartPoint, EndPoint):
    sheet_link = file.sheet_by_name('Link表')
    total_line_num = int(sheet_link.col_values(5)[1])
    links = find_links_between_two_points(0x55, StartPoint, EndPoint)
    for link in links:
        if link == StartPoint.link and link == StopPoint.link:
            if StopPoint.offset >= StartPoint.offset:
                return True
            else:
                continue
        elif link == EndPoint.link and link == StopPoint.link:
            if StopPoint.offset <= EndPoint.offset:
                return True
            else:
                continue
        elif link != StartPoint.link and link != StopPoint.link and link == StopPoint.link:
            return True
        else:
            continue
    return False


def find_slope_range(StopPoint):
    sheet_slope = file.sheet_by_name('坡度表')
    total_line_num = int(sheet_slope.col_values(5)[1])
    slopeNums = list(map(int, sheet_slope.col_values(0)[4:total_line_num + 4]))  # 第一列
    for index, slopeNum in enumerate(slopeNums):
        if isBetweenTwoPoints(StopPoint,
                           Point(int(sheet_slope.col_values(1)[index + 4]),
                                 int(sheet_slope.col_values(2)[index + 4])),
                           Point(int(sheet_slope.col_values(3)[index + 4]),
                                 int(sheet_slope.col_values(4)[index + 4]))
                           ):
            return Slope(slopeNum=slopeNum,
                         linkStart=int(sheet_slope.col_values(1)[index + 4]),
                         offsetStart=int(sheet_slope.col_values(2)[index + 4]),
                         slopeNumStart=int(sheet_slope.col_values(6)[index + 4]),
                         linkNumStart=int(sheet_slope.col_values(5)[index + 4]),
                         linkEnd=int(sheet_slope.col_values(3)[index + 4]),
                         offsetEnd=int(sheet_slope.col_values(4)[index + 4]),
                         slopeNumEnd=int(sheet_slope.col_values(9)[index + 4]),
                         linkNumEnd=int(sheet_slope.col_values(8)[index + 4]),
                         slopeValue=int(sheet_slope.col_values(11)[index + 4]),
                         direction=0xaa if sheet_slope.col_values(12)[index + 4] == '0xaa' else 0x55)

if __name__ == "__main__":
    file = xlrd.open_workbook(r'C:/Users/a8047/Desktop/电子地图/excel/电子地图数据201808172018_08_17_09_14_282018_08_17_16_17_03.xls')
    station_dict = {'成都医学院': 1,
                    '石油大学': 2,
                    '钟楼': 3,
                    '马超西路': 4,
                    '团结新区': 5,
                    '锦水河': 6,
                    '三河场': 7,
                    '金华寺东路': 8,
                    '植物园': 9,
                    '军区总医院': 10,
                    '熊猫大道': 11,
                    '动物园': 12,
                    '昭觉寺南路': 13,
                    '驷马桥': 14,
                    '李家沱': 15,
                    '前锋路': 16,
                    '红星桥': 17,
                    '市二医院': 18,
                    '春熙路': 19,
                    '新南门': 20,
                    '磨子桥': 21,
                    '省体育馆': 22,
                    '衣冠庙': 23,
                    '高升桥': 24,
                    '红牌楼': 25,
                    '太平园': 26,
                    '川藏立交': 27,
                    '武侯立交': 28,
                    '武青南路': 29,
                    '双凤桥': 30,
                    '龙桥路': 31,
                    '航都大街': 32,
                    '迎春桥': 33,
                    '东升': 34,
                    '双流广场': 35,
                    '三里坝': 36,
                    '双流西': 37
                    }

    start_station = '驷马桥'
    end_station = '市二医院'
    StartStation, EndStation = init_all_info(start_station, end_station)
    # 判断上下行
    operation_direction = 0xaa if station_dict[start_station] - station_dict[end_station] < 0 else 0x55
    StartStationStopPoint, EndStationStopPoint = find_start_and_end_point_by_stations(operation_direction, StartStation, EndStation)
    links = find_links_between_two_points(operation_direction, StartStationStopPoint, EndStationStopPoint)
    StartSlope = find_slope_range(StartStationStopPoint)
    print('start stop point: ' + str(StartStationStopPoint.num))
    print('start link: ' + str(StartStationStopPoint.link))
    print('start offset: ' + str(StartStationStopPoint.offset))
    print('end stop point: ' + str(EndStationStopPoint.num))
    print('end link: ' + str(EndStationStopPoint.link))
    print('end offset: ' + str(EndStationStopPoint.offset))
    print(links)
