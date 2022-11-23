from django.test import TestCase
import os, zipfile
from zipmagdata.settings import STATIC_OS_PATH
from tools import *
from get_magdataDB import get_ftp_db
import time


# Create your tests here.

def test1():
    data_format = 'ADD'
    #data_format = 'IAF'
    print('test: get magdata FTP in dt range time_from=[1, 1, 2020], time_to=[31, 12, 2021]')
    station_db, path_db = get_ftp_db(data_format=data_format)
    print(station_db)
    time_range = get_time_range_list(time_from=[1, 1, 2020], time_to=[31, 12, 2021])
    station_list = station_in_dt_range_FTP(time_range, station_db, data_format=data_format)
    print('station_list:', station_list)

    path_list = get_path_station_in_range_FRP(time_range, station_list, path_db, data_format=data_format)

    print('station_list:', station_list)
    print('path list:')
    for path in path_list:
        print(path, end='\n')
    print('DONE!')



def test3():
    print('summary test')
    d_from, m_from, y_from = int(10), int(11), int(2021)
    d_to, m_to, y_to = int(24), int(12), int(2021)
    data_format = str('add').upper()
    #data_format = str('IAF').upper()
    code = str('irt').lower()

    timestamp = int(round(time.time() * 1000))
    time_range = get_time_range_list(time_from=[d_from, m_from, y_from],
                                     time_to=[d_to, m_to, y_to])
    station_db, path_db = get_ftp_db(data_format=data_format)
    # 1
    station_list = station_in_dt_range_FTP(time_range, station_db, data_format=data_format)
    # 2
    path_list = get_path_station_in_range_FRP(time_range, station_list, path_db, data_format=data_format)
    save_zip(path_list, filename='t_test', data_format=data_format)

def test4():
    #data_format = 'IAGA2002'
    data_format = 'IAF'

    station_db, path_db = get_ftp_db(data_format=data_format)
    station_time_intervals = {}

    for station_key in path_db.keys():
        station_time_intervals[station_key] = []
        time_range = []
        for i, station_date in enumerate(path_db[station_key].keys()):
            if data_format =='IAGA2002':
                time_range.append(datetime.datetime(int(station_date[:4]),  #y
                                                int(station_date[4:6]), #m
                                                int(station_date[6:]))) #d
            elif data_format == 'IAF':
                time_range.append(datetime.datetime(int(station_date[:4]),  # y
                                                    int(station_date[4:6]), 1))  # m

        time_intervals = []
        start_int = time_range[0]
        if data_format == 'IAGA2002':
            for i, ct in enumerate(time_range):
                if ct - time_range[i - 1] > datetime.timedelta(days=1):
                    time_intervals.append([start_int, time_range[i - 1]])
                    start_int = ct
        elif data_format == 'IAF':
            for i, ct in enumerate(time_range):
                if ct - time_range[i - 1] > datetime.timedelta(days=32):
                    time_intervals.append([start_int, time_range[i - 1]])
                    start_int = ct
        if len(time_intervals) == 0:
            # append time interval im unix time
            station_time_intervals[station_key].append([int(time_range[0].timestamp()), int(time_range[-1].timestamp())])
    return station_time_intervals

def test5():
    # station_list_answer
    print('station_time_intervals')
    #data_format = 'IAF'
    data_format = 'ADD'

    # загрузка ДБ достпуных данных
    station_db, path_db = get_ftp_db(data_format=data_format)
    station_time_intervals = get_station_time_intervals(path_db, data_format)
    print(station_time_intervals)

def test6():
    # total_time_range_answer
    #data_format = 'IAGA2002'
    #data_format = 'IAF'
    data_format = 'ADD'
    station_code = str('irt').lower()


    # загрузка ДБ достпуных данных
    station_db, path_db = get_ftp_db(data_format=data_format)

    # доступные интервалы времени
    stations_time_intervals = get_station_time_intervals(path_db, data_format)
    cts = stations_time_intervals[station_code]
    from_date = datetime.datetime.utcfromtimestamp(cts[0][0])
    to_date = datetime.datetime.utcfromtimestamp(cts[-1][1])
    time_range = get_time_range_list(time_from=[from_date.day, from_date.month, from_date.year],
                                     time_to=[to_date.day, to_date.month, to_date.year])
    # 1 проверка верно указанной станции
    station_list = station_in_dt_range_FTP(time_range, station_db, data_format=data_format)
    if station_code in station_list:
        station_list = [station_code]
        # 2
        path_list = get_path_station_in_range_FRP(time_range, station_list, path_db, data_format=data_format)
        save_zip(path_list, filename='t2_test', data_format=data_format)
    else:
        pass
        #ERROR



test1()
test3()
test4()

test5()
test6()
