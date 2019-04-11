import xlrdimport numpy as npimport jsonfrom flask import Flask, requestfrom StopArea import StopAreafrom Station import Stationfrom StopPoint import StopPointfrom Slope import Slopefrom Point import Pointfrom ChangePoint import ChangePointfrom LimitSection import LimitSectionfrom matplotlib import pyplot as plt# 根据站名初始化各车站、停车区域、停车点信息def init_all_info(startStation, endStation):    # 查找停车区域    # 条件:停车区域站台轨属性需要为1    StartStationStopArea = find_stop_area_by_station_name(startStation)    find_stop_points_by_stop_area(StartStationStopArea)    EndStationStopArea = find_stop_area_by_station_name(endStation)    find_stop_points_by_stop_area(EndStationStopArea)    StartStation = Station(stationName=startStation, stationId=StartStationStopArea[0].belongToStationId)    StartStation.stopAreas = StartStationStopArea    EndStation = Station(stationName=endStation, stationId=EndStationStopArea[0].belongToStationId)    EndStation.stopAreas = EndStationStopArea    return StartStation, EndStation# 根据车站名查找该车站所包括的停车区域def find_stop_area_by_station_name(name):    sheet_stop_area = file.sheet_by_name('停车区域表')    total_line_num = int(sheet_stop_area.col_values(5)[1])    stationNames = sheet_stop_area.col_values(1)[4:total_line_num + 4]  # 第二列内容    _stop_areas = []    for index, stationName in enumerate(stationNames):        if name == stationName:            # 判断停车区域属性是否包括站台轨属性            if int(sheet_stop_area.col_values(4)[index + 4]) & 0x0001:                num_stop_area = int(sheet_stop_area.col_values(0)[index + 4])  # 停车区域编号                num_stop_point = int(sheet_stop_area.col_values(14)[index + 4])  # 停车点数目                # print(sheet.col_values(15)[index + 4])  # 停车点编号                link = int(sheet_stop_area.col_values(3)[index + 4])  # 停车点link                belong_to_station_id = int(sheet_stop_area.col_values(23)[index + 4])  # 停车点所属车站ID                _stop_areas.append(StopArea(num=num_stop_area,                                          stationName=stationName,                                          link=link,                                          n_stopPoint=num_stop_point,                                            lineNum=index + 4,                                            belongToStationId=belong_to_station_id))    return _stop_areas# 根据站名初始化各车站、停车区域、停车点信息def find_stop_points_by_stop_area(_stop_areas):    if len(_stop_areas) == 0:        return None    sheet_stop_area = file.sheet_by_name('停车区域表')    sheet_stop_point = file.sheet_by_name('停车点表')    total_line_num = int(sheet_stop_point.col_values(5)[1])    stopPointNums = list(map(int,sheet_stop_point.col_values(0)[4:total_line_num + 4]))  # 第一列    for stop_area in _stop_areas:        for n in range(stop_area.n_stopPoint):            num_stop_point = int(sheet_stop_area.col_values(15 + n)[stop_area.lineNum])  # 停车点编号            # 匹配停车点类型，必须是运营停车点            for index, stopPoint in enumerate(stopPointNums):                if num_stop_point == stopPoint:                    direction_stop_point = 0xaa if sheet_stop_point.col_values(2)[index + 4] == '0xaa' else 0x55                    link = int(sheet_stop_point.col_values(3)[index + 4])                    offset = int(sheet_stop_point.col_values(4)[index + 4])                    stop_area.stopPoints.append(StopPoint(num=num_stop_point,                                                          direction=direction_stop_point,                                                          link=link,                                                          offset=offset,                                                          lineNum=index))# 根据停车区域查找站台名，站台名可确认上行下行def find_platform_name_by_stop_area(stop_area):    sheet_platform = file.sheet_by_name('站台表')    total_line_num = int(sheet_platform.col_values(5)[1])    stopAreaNums = list(map(int, sheet_platform.col_values(2)[4:total_line_num + 4]))  # 第一列    for index, stopArea in enumerate(stopAreaNums):        if stop_area.num == stopArea:            return sheet_platform.col_values(15)[index + 4]# 根据起始站和终点站找到起点停车点和终点停车点def find_start_and_end_point_by_stations(operation_direction, StartStation, EndStation):    StartStationStopPoint = None    EndStationStopPoint = None    # 查找起始站停车点    if operation_direction == 0xaa:  # 下行方向        for stopArea in StartStation.stopAreas:            platform_name = find_platform_name_by_stop_area(stopArea)            if '下行' in platform_name:                for stopPoint in stopArea.stopPoints:                    if 0xaa == stopPoint.direction:  # 找到了该车站在该方向上的停车点                        StartStationStopPoint = stopPoint                        break    else:        for stopArea in StartStation.stopAreas:  # 上行方向            platform_name = find_platform_name_by_stop_area(stopArea)            if '上行' in platform_name:                for stopPoint in stopArea.stopPoints:                    if 0x55 == stopPoint.direction:  # 找到了该车站在该方向上的停车点                        StartStationStopPoint = stopPoint                        break    # 查找终止站停车点    if operation_direction == 0xaa:  # 下行方向        for stopArea in EndStation.stopAreas:            platform_name = find_platform_name_by_stop_area(stopArea)            if '下行' in platform_name:                for stopPoint in stopArea.stopPoints:                    if 0xaa == stopPoint.direction:  # 找到了该车站在该方向上的停车点                        EndStationStopPoint = stopPoint                        break    else:        for stopArea in EndStation.stopAreas:  # 上行方向            platform_name = find_platform_name_by_stop_area(stopArea)            if '上行' in platform_name:                for stopPoint in stopArea.stopPoints:                    if 0x55 == stopPoint.direction:  # 找到了该车站在该方向上的停车点                        EndStationStopPoint = stopPoint                        break    return StartStationStopPoint, EndStationStopPoint# 根据link编号找到下一个link编号def find_next_link(sheetlink, linkNums, start_link):    for index, link in enumerate(linkNums):        if link == start_link:            return int(sheetlink.col_values(9)[index + 4])# 查找两个位置中间的link编号，包含起点和终点所在linkdef find_links_between_two_points(direction, StartPoint, EndPoint):    # 根据link表设置需要从前往后找    links = []    start_link = StartPoint.link if direction != 0xaa else EndPoint.link    end_link = EndPoint.link if direction != 0xaa else StartPoint.link    links.append(start_link)  # 添加起始link    if start_link == end_link:        return links    sheet_link = file.sheet_by_name('Link表')    total_line_num = int(sheet_link.col_values(5)[1])    linkNums = list(map(int, sheet_link.col_values(0)[4:total_line_num + 4]))  # 第一列    next_link = find_next_link(sheet_link, linkNums, start_link)    links.append(next_link)    while next_link != end_link:        next_link = find_next_link(sheet_link, linkNums, next_link)        links.append(next_link)    if direction == 0xaa:        return list(reversed(links))    else:        return links# 判断一个点是否位于另外两个点之间def isBetweenTwoPoints(StopPoint, StartPoint, EndPoint, direction):    sheet_link = file.sheet_by_name('Link表')    total_line_num = int(sheet_link.col_values(5)[1])    # todo 为什么是0x55    links = find_links_between_two_points(direction, StartPoint, EndPoint)    if len(links) > 1:        for link in links:            if link == StartPoint.link and link == StopPoint.link:                if direction == 0x55:                    if StopPoint.offset >= StartPoint.offset:                        return True                    else:                        continue                else:                    if StopPoint.offset <= StartPoint.offset:                        return True                    else:                        continue            elif link == EndPoint.link and link == StopPoint.link:                if direction == 0x55:                    if StopPoint.offset <= EndPoint.offset:                        return True                    else:                        continue                else:                    if StopPoint.offset >= EndPoint.offset:                        return True                    else:                        continue            elif link != StartPoint.link and link != EndPoint.link and link == StopPoint.link:                return True            else:                continue        return False    else:        if StopPoint.link == links[0]:            if direction == 0x55:                if StartPoint.offset <= StopPoint.offset <= EndPoint.offset:                    return True                else:                    return False            else:                if EndPoint.offset <= StopPoint.offset <= StartPoint.offset:                    return True                else:                    return False        else:            return False# 根据点查找该点所属坡度def find_slope_range(StopPoint):    sheet_slope = file.sheet_by_name('坡度表')    total_line_num = int(sheet_slope.col_values(5)[1])    slopeNums = list(map(int, sheet_slope.col_values(0)[4:total_line_num + 4]))  # 第一列    for index, slopeNum in enumerate(slopeNums):        if isBetweenTwoPoints(StopPoint,                              Point(int(sheet_slope.col_values(1)[index + 4]),                                    int(sheet_slope.col_values(2)[index + 4])),                              Point(int(sheet_slope.col_values(3)[index + 4]),                                    int(sheet_slope.col_values(4)[index + 4])),                              0x55,                           ):            return Slope(slopeNum=slopeNum,                         linkStart=int(sheet_slope.col_values(1)[index + 4]),                         offsetStart=int(sheet_slope.col_values(2)[index + 4]),                         slopeNumStart=int(sheet_slope.col_values(6)[index + 4]),                         linkEnd=int(sheet_slope.col_values(3)[index + 4]),                         offsetEnd=int(sheet_slope.col_values(4)[index + 4]),                         slopeNumEnd=int(sheet_slope.col_values(9)[index + 4]),                         slopeValue=int(sheet_slope.col_values(11)[index + 4]),                         direction=0xaa if sheet_slope.col_values(12)[index + 4] == '0xaa' else 0x55)# 查找link所属的限速区段编号def find_limit_speed_by_link(link):    sheet_limit_speed = file.sheet_by_name('静态限速表')    total_line_num = int(sheet_limit_speed.col_values(5)[1])    limitSpeedNums = list(map(int, sheet_limit_speed.col_values(0)[4:total_line_num + 4]))  # 第一列    limit_sections = []    for index, limitSpeedNum in enumerate(limitSpeedNums):        if link == int(sheet_limit_speed.col_values(1)[index + 4]):            limit_sections.append(LimitSection(sectionNum=limitSpeedNum,                                               lineNum=index,                                               startOffset=int(sheet_limit_speed.col_values(2)[index + 4]),                                               endOffset=int(sheet_limit_speed.col_values(3)[index + 4]),                                               link=link,                                               limitSpeed=int(sheet_limit_speed.col_values(5)[index + 4]))                                  )    if operation_direction == 0xaa:        return list(reversed(limit_sections))    else:        return limit_sections# 查找两点之间的限速变化点def find_limit_speed_change_points_between_two_points(StartPoint, EndPoint):    limit_change_points = []    links = find_links_between_two_points(operation_direction, StartPoint, EndPoint)    for index, link in enumerate(links):        limit_sections = find_limit_speed_by_link(link)        if index == 0:            for limit_section in limit_sections:                if limit_section.startOffset <= StartPoint.offset <= limit_section.endOffset:                    StartPoint.limit_speed = limit_section.limitSpeed                    limit_change_points.append(ChangePoint(link=link,                                                           offset=limit_section.endOffset if operation_direction == 0x55 else limit_section.startOffset,                                                           limit_speed=limit_section.limitSpeed))        elif index == len(links) - 1:            for limit_section in limit_sections:                if limit_section.startOffset <= EndPoint.offset <= limit_section.endOffset:                    EndPoint.limit_speed = limit_section.limitSpeed                    limit_change_points.append(ChangePoint(link=link,                                                           offset=limit_section.startOffset if operation_direction == 0x55 else limit_section.endOffset,                                                           limit_speed=limit_section.limitSpeed))        else:            for limit_section in limit_sections:                limit_change_points.append(ChangePoint(link=link,                                                       offset=limit_section.startOffset if operation_direction == 0x55 else limit_section.endOffset,                                                       limit_speed=limit_section.limitSpeed))                limit_change_points.append(ChangePoint(link=link,                                                       offset=limit_section.endOffset if operation_direction == 0x55 else limit_section.startOffset,                                                       limit_speed=limit_section.limitSpeed))    return limit_change_points# 根据坡度编号获取坡度实例def get_slope_by_slope_num(sheet_slope, slopeNums, slope_num):    for index, slopeNum in enumerate(slopeNums):        if slopeNum == slope_num:            return Slope(slopeNum=slopeNum,                         linkStart=int(sheet_slope.col_values(1)[index + 4]),                         offsetStart=int(sheet_slope.col_values(2)[index + 4]),                         slopeNumStart=int(sheet_slope.col_values(6)[index + 4]),                         linkEnd=int(sheet_slope.col_values(3)[index + 4]),                         offsetEnd=int(sheet_slope.col_values(4)[index + 4]),                         slopeNumEnd=int(sheet_slope.col_values(9)[index + 4]),                         slopeValue=int(sheet_slope.col_values(11)[index + 4]),                         direction=0xaa if sheet_slope.col_values(12)[index + 4] == '0xaa' else 0x55)# 查找两个坡度之间的其他坡度def find_slopes_between_two_slopes(direction, StartSlope, EndSlope):    # 根据link表设置需要从前往后找    slopes = []    start_slope = StartSlope if direction != 0xaa else EndSlope    # start_slope = StartSlope    end_slope = EndSlope if direction != 0xaa else StartSlope    # end_slope = EndSlope    slopes.append(start_slope)  # 添加起始link    if start_slope.slopeNum == end_slope.slopeNum:        return slopes    sheet_slope = file.sheet_by_name('坡度表')    total_line_num = int(sheet_slope.col_values(5)[1])    slopeNums = list(map(int, sheet_slope.col_values(0)[4:total_line_num + 4]))  # 第一列    next_slope = get_slope_by_slope_num(sheet_slope, slopeNums, start_slope.slopeNumEnd)    slopes.append(next_slope)    while next_slope.slopeNum != end_slope.slopeNum:        next_slope = get_slope_by_slope_num(sheet_slope, slopeNums, next_slope.slopeNumEnd)        slopes.append(next_slope)    if direction == 0xaa:        return list(reversed(slopes))    else:        return slopes# 查找两个点之间的坡度变化点def find_slope_change_points_between_two_points(StartPoint, EndPoint):    change_points = []    StartSlope = find_slope_range(StartPoint)    EndSlope = find_slope_range(EndPoint)    StartPoint.slope = StartSlope.slopeValue    StartPoint.slope_direction = StartSlope.direction    EndPoint.slope = EndSlope.slopeValue    EndPoint.slope_direction = EndSlope.direction    slopes = find_slopes_between_two_slopes(operation_direction, StartSlope, EndSlope)    change_points.append(StartPoint)    for index, slope in enumerate(slopes):        if index == 0:            if operation_direction == 0xaa:                # 第一个坡度起点                change_points.append(ChangePoint(link=slope.linkStart,                                                 offset=slope.offsetStart,                                                 slope_value=slope.slopeValue,                                                 slope_direction=slope.direction)                                     )            else:                # 第一个坡度终点                change_points.append(ChangePoint(link=slope.linkEnd,                                                 offset=slope.offsetEnd,                                                 slope_value=slope.slopeValue,                                                 slope_direction=slope.direction)                                     )        elif index == len(slopes) - 1:            if operation_direction == 0xaa:                # 最后一个坡度终点                change_points.append(ChangePoint(link=slope.linkEnd,                                                 offset=slope.offsetEnd,                                                 slope_value=slope.slopeValue,                                                 slope_direction=slope.direction)                                     )            else:                # 最后一个坡度起点                change_points.append(ChangePoint(link=slope.linkStart,                                                 offset=slope.offsetStart,                                                 slope_value=slope.slopeValue,                                                 slope_direction=slope.direction)                                     )        else:            if operation_direction == 0xaa:                change_points.append(ChangePoint(link=slope.linkEnd,                                                 offset=slope.offsetEnd,                                                 slope_value=slope.slopeValue,                                                 slope_direction=slope.direction)                                     )                change_points.append(ChangePoint(link=slope.linkStart,                                                 offset=slope.offsetStart,                                                 slope_value=slope.slopeValue,                                                 slope_direction=slope.direction)                                     )            else:                change_points.append(ChangePoint(link=slope.linkStart,                                                 offset=slope.offsetStart,                                                 slope_value=slope.slopeValue,                                                 slope_direction=slope.direction)                                     )                change_points.append(ChangePoint(link=slope.linkEnd,                                                 offset=slope.offsetEnd,                                                 slope_value=slope.slopeValue,                                                 slope_direction=slope.direction)                                     )    change_points.append(EndPoint)    return change_points# 获取两点间的距离，与运行方向有关def get_dis_between_two_points(start_point, end_point):    distance = 0    # 包括起点和终点    links = find_links_between_two_points(operation_direction, start_point, end_point)    if len(links) == 1:        return abs(start_point.offset - end_point.offset)    sheet_link = file.sheet_by_name('Link表')    total_line_num = int(sheet_link.col_values(5)[1])    linkNums = list(map(int, sheet_link.col_values(0)[4:total_line_num + 4]))  # 第一列    for i, link in enumerate(links):        for j, linkNum in enumerate(linkNums):            if link == linkNum:                if i == 0:                    if operation_direction == 0xaa:                        distance += start_point.offset                    else:                        distance += int(sheet_link.col_values(1)[j + 4]) - start_point.offset                elif i == len(links) - 1:                    if operation_direction == 0x55:                        distance += end_point.offset                    else:                        distance += int(sheet_link.col_values(1)[j + 4]) - end_point.offset                else:                    distance += int(sheet_link.col_values(1)[j + 4])    return distance# 合并坡度变化点和限速变化点def merge_slope_and_limit_speed_change_points(slope_change_points, limit_speed_change_points):    # 将限速变化点插入坡度变化点中    for i in range(0, len(limit_speed_change_points)):        for j in range(0, len(slope_change_points)):            if isBetweenTwoPoints(limit_speed_change_points[i],                                  slope_change_points[j],                                  slope_change_points[j+1],                                  operation_direction                                  ):                slope_change_points.insert(j+1, limit_speed_change_points[i])                break    # 完善各个点的信息    for k in range(0, len(slope_change_points), 2):        if slope_change_points[k].limit_speed is not None and slope_change_points[k+1].limit_speed is None:            slope_change_points[k+1].limit_speed = slope_change_points[k].limit_speed        elif slope_change_points[k].limit_speed is None and slope_change_points[k+1].limit_speed is not None:            slope_change_points[k].limit_speed = slope_change_points[k+1].limit_speed        elif slope_change_points[k].limit_speed is None and slope_change_points[k+1].limit_speed is None:            slope_change_points[k].limit_speed = slope_change_points[k - 1].limit_speed            slope_change_points[k + 1].limit_speed = slope_change_points[k].limit_speed        else:            pass        if slope_change_points[k].slope is not None and slope_change_points[k + 1].slope is None:            slope_change_points[k + 1].slope = slope_change_points[k].slope        elif slope_change_points[k].slope is None and slope_change_points[k + 1].slope is not None:            slope_change_points[k].slope = slope_change_points[k + 1].slope        elif slope_change_points[k].slope is None and slope_change_points[k + 1].slope is None:            slope_change_points[k].slope = slope_change_points[k - 1].slope            slope_change_points[k + 1].slope = slope_change_points[k].slope        else:            pass        if slope_change_points[k].slope_direction is not None and slope_change_points[k + 1].slope_direction is None:            slope_change_points[k + 1].slope_direction = slope_change_points[k].slope_direction        elif slope_change_points[k].slope_direction is None and slope_change_points[k + 1].slope_direction is not None:            slope_change_points[k].slope_direction = slope_change_points[k + 1].slope_direction        elif slope_change_points[k].slope_direction is None and slope_change_points[k + 1].slope_direction is None:            slope_change_points[k].slope_direction = slope_change_points[k - 1].slope_direction            slope_change_points[k + 1].slope_direction = slope_change_points[k].slope_direction        else:            pass    return slope_change_points# 绘制坡度图def figure_slope(change_points):    dis = []    slope = []    limit_speed = []    for i in range(0, len(change_points), 2):        dis.append(get_dis_between_two_points(change_points[i], change_points[i + 1]))        slope.append(change_points[i].slope if operation_direction == change_points[i].slope_direction else 0 - change_points[i].slope)        limit_speed.append(change_points[i].limit_speed)    cur = 0    for j in range(0, len(dis)):        x = np.linspace(cur, cur + dis[j], dis[j])        y1 = np.ones([dis[j], 1]) * slope[j] / 10        y2 = np.ones([dis[j], 1]) * limit_speed[j]        plt.plot(x, y1, 'b')        plt.plot(x, y2, 'r')        cur += dis[j]    plt.show()def get_data_by_stations(start_station, end_station):    StartStation, EndStation = init_all_info(start_station, end_station)    # 判断上下行    operation_direction = 0xaa if station_dict[start_station] - station_dict[end_station] < 0 else 0x55    StartStationStopPoint, EndStationStopPoint = find_start_and_end_point_by_stations(operation_direction, StartStation,                                                                                      EndStation)    slope_change_points = find_slope_change_points_between_two_points(StartStationStopPoint, EndStationStopPoint)    limit_change_points = find_limit_speed_change_points_between_two_points(StartStationStopPoint, EndStationStopPoint)    all_change_points = merge_slope_and_limit_speed_change_points(slope_change_points, limit_change_points)    return all_change_pointsapp = Flask(__name__)@app.route("/DSU/getData", methods=['post'])def get_speed_and_slope_data():    data = request.data    stations = json.loads(data)    start_station = {value: key for key,value in station_dict.items()}[stations['startStation']]    end_station ={value: key for key,value in station_dict.items()}[stations['endStation']]    global operation_direction    operation_direction = 0xaa if station_dict[start_station] - station_dict[end_station] < 0 else 0x55    all_change_points = get_data_by_stations(start_station, end_station)    dis = []    slope = []    limit_speed = []    for i in range(0, len(all_change_points), 2):        dis.append(get_dis_between_two_points(all_change_points[i], all_change_points[i + 1]))        slope.append(all_change_points[i].slope if operation_direction == all_change_points[i].slope_direction else 0 - all_change_points[i].slope)        limit_speed.append(all_change_points[i].limit_speed)    return json.dumps([dis, slope, limit_speed], default=lambda obj: obj.__dict__)if __name__ == "__main__":    file = xlrd.open_workbook(r'C:/Users/hp/Desktop/电子地图数据201808172018_08_17_09_14_282018_08_17_16_17_03.xls')    station_dict = {'成都医学院': 1,                    '石油大学': 2,                    '钟楼': 3,                    '马超西路': 4,                    '团结新区': 5,                    '锦水河': 6,                    '三河场': 7,                    '金华寺东路': 8,                    '植物园': 9,                    '军区总医院': 10,                    '熊猫大道': 11,                    '动物园': 12,                    '昭觉寺南路': 13,                    '驷马桥': 14,                    '李家沱': 15,                    '前锋路': 16,                    '红星桥': 17,                    '市二医院': 18,                    '春熙路': 19,                    '新南门': 20,                    '磨子桥': 21,                    '省体育馆': 22,                    '衣冠庙': 23,                    '高升桥': 24,                    '红牌楼': 25,                    '太平园': 26,                    '川藏立交': 27,                    '武侯立交': 28,                    '武青南路': 29,                    '双凤桥': 30,                    '龙桥路': 31,                    '航都大街': 32,                    '迎春桥': 33,                    '东升': 34,                    '双流广场': 35,                    '三里坝': 36,                    '双流西': 37                    }    app.run(host="0.0.0.0", port=8786)    '''    start_station = '驷马桥'    end_station = '李家沱'    StartStation, EndStation = init_all_info(start_station, end_station)    # 判断上下行    operation_direction = 0xaa if station_dict[start_station] - station_dict[end_station] < 0 else 0x55    StartStationStopPoint, EndStationStopPoint = find_start_and_end_point_by_stations(operation_direction, StartStation, EndStation)    links = find_links_between_two_points(operation_direction, StartStationStopPoint, EndStationStopPoint)    slope_change_points = find_slope_change_points_between_two_points(StartStationStopPoint, EndStationStopPoint)    limit_change_points = find_limit_speed_change_points_between_two_points(StartStationStopPoint, EndStationStopPoint)    all_change_points = merge_slope_and_limit_speed_change_points(slope_change_points, limit_change_points)    figure_slope(all_change_points)    print('start stop point: ' + str(StartStationStopPoint.num))    print('start link: ' + str(StartStationStopPoint.link))    print('start offset: ' + str(StartStationStopPoint.offset))    print('end stop point: ' + str(EndStationStopPoint.num))    print('end link: ' + str(EndStationStopPoint.link))    print('end offset: ' + str(EndStationStopPoint.offset))    print(links)    '''