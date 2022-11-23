#from django.shortcuts import render
import io
import os.path
import time
from zmdsite.tools import *
from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from .get_magdataDB import get_ftp_db
import json, zipfile
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def index(request):
    return HttpResponse("MAIN PAGE")



def check_station(request):
    db = get_ftp_db()
    station_dict = db[0]     # возвращает доступные станции по DICT['2021']['12']['24']
    path_dict = db[1]    # возвращает путь к файлу через station_path['irt']['20211224']

    dd, mm, YY = '24', '12', '2021'
    return HttpResponse("Доступные станции %s/%s/%s\n\n%s" % (dd, mm, YY,
                                                             station_dict[YY][mm][dd]))

def check_station_ftp1(request):
    db = get_ftp_db(data_format='ADD')
    station_dict = db[0]  # возвращает доступные станции по DICT['2021']
    path_dict = db[1]  # возвращает доступные станции по DICT['KHB']['2020']

    year_2020 = '2020 : %s' % station_dict['2020']
    year_2021 = '2021 : %s' % station_dict['2021']
    KHB_path = path_dict['KHB']['2020']
    return HttpResponse(str(year_2020 + ' ' + year_2021 + ' '+KHB_path))

@csrf_exempt
def send_zip(request):
    """if request.is_ajax():
        if request.method == 'POST':
            print( 'Raw Data: "%s"' % request.raw_post_data)
        return HttpResponse('OK')
    """
    data = json.loads(request.body)
    d_from, m_from, y_from = int(data['day1']), int(data['mon1']), int(data['year1'])
    d_to, m_to, y_to = int(data['day2']), int(data['mon2']), int(data['year2'])
    data_format = str(data['format']).upper()

    timestamp = int(round(time.time() * 1000))
    time_range = get_time_range_list(time_from=[d_from, m_from, y_from],
                                     time_to=[d_to, m_to, y_to])
    station_db, path_db = get_ftp_db(data_format=data_format)

    #1
    station_list = station_in_dt_range_FTP(time_range, station_db, data_format=data_format)

    #2
    path_list = get_path_station_in_range_FRP(time_range, station_list, path_db, data_format=data_format)

    save_zip(path_list, filename='%s'%timestamp, data_format=data_format)

    file_location = os.path.join(os.path.join(STATIC_OS_PATH, 'zip'), '%s.zip' % timestamp)
    if os.path.exists(file_location):
        with open(file_location, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/zip")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_location)
            return response
    raise Http404



@csrf_exempt
def station_list_answer(request):
    # post 1
    data = json.loads(request.body)
    data_format = str(data['format']).upper()
    #print(data)
    # загрузка ДБ достпуных данных
    station_db, path_db = get_ftp_db(data_format=data_format)
    #print(path_db)
    station_time_intervals = get_station_time_intervals(path_db, data_format)
    #print(station_time_intervals, 'OUT JSON')
    return JsonResponse(station_time_intervals, safe=False)

@csrf_exempt
def station_data_answer(request):
    timestamp = int(round(time.time() * 1000))

    data = json.loads(request.body)
    data_format = str(data['format']).upper()
    station_code = str(data['code']).lower()
    time_format = str(data['time']).lower()     # total or certain
    email = str(data['email']).lower()     # total or certain
    ip = request.META.get('REMOTE_ADDR')

    # загрузка ДБ достпуных данных
    station_db, path_db = get_ftp_db(data_format=data_format)

    # доступные интервалы времени
    if time_format == 'total':
        stations_time_intervals = get_station_time_intervals(path_db, data_format)
        cts = stations_time_intervals[station_code]
        from_date = datetime.datetime.utcfromtimestamp(cts[0][0])
        to_date = datetime.datetime.utcfromtimestamp(cts[-1][1])
        d_from, m_from, y_from = from_date.day, from_date.month, from_date.year
        d_to, m_to, y_to = to_date.day, to_date.month, to_date.year
    else:  # time_format == 'certain'
        d_from, m_from, y_from = int(data['day1']), int(data['mon1']), int(data['year1'])
        d_to, m_to, y_to = int(data['day2']), int(data['mon2']), int(data['year2'])

    save_emails(email, ip, station_code.upper(), '%s/%s/%s %s/%s/%s' % (d_from, m_from, y_from, d_to, m_to, y_to),
                data_format)

    time_range = get_time_range_list(time_from=[d_from, m_from, y_from],
                                     time_to=[d_to, m_to, y_to])
    # 1 проверка верно указанной станции
    #station_list = station_in_dt_range_FTP(time_range, station_db, data_format=data_format)
    station_list = [station_code]
    # 2
    path_list = get_path_station_in_range_FRP(time_range, station_list, path_db, data_format=data_format)
    save_zip(path_list, filename='%s' % timestamp, data_format=data_format)
    file_location = os.path.join(os.path.join(STATIC_OS_PATH, 'zip'), '%s.zip' % timestamp)
    if os.path.exists(file_location):
        with open(file_location, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/zip")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_location)
            return response
    raise Http404




