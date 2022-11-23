import datetime
import os
import zipfile
from zipmagdata.settings import STATIC_OS_PATH, EMAIL_TXT_PATH

def save_zip(path_list, filename, data_format='IAGA2002'):
    filepath = os.path.join(os.path.join(STATIC_OS_PATH, 'zip'), '%s.zip' % filename)
    with zipfile.ZipFile(filepath, 'w') as zf:
        if data_format != 'ADD':
            for p in path_list:
                p_dirname = os.path.dirname(p)
                p_filename = os.path.basename(p)
                os.chdir(p_dirname)
                zf.write(p_filename)
        else:
            for stat_directory_paths in path_list:
                stat_folder = os.path.basename(os.path.dirname(stat_directory_paths[0]))
                year_folder = os.path.basename(os.path.dirname(os.path.dirname(
                                                stat_directory_paths[0])))
                zip_folder = stat_folder+year_folder
                for p_filename in stat_directory_paths:
                    zf.write(p_filename, os.path.join(zip_folder, os.path.basename(p_filename)))
                    pass

def save_emails(email, ip, station_code, time, data_format):
    with open(os.path.join(EMAIL_TXT_PATH), 'a') as f:
        f.write('%s %s %s %s %s\n' % (email, ip, station_code, time, data_format))

def get_time_range_list(time_from, time_to):
    """
    :param time_from: [dd, mm, YY] int
    :param time_to: [dd, mm, YY] int
    :return: [[YY, mm, dd], [same]] int
    """


    def date_range_list(start_date, end_date):
        # Return list of datetime.date objects between start_date and end_date (inclusive).
        date_list = []
        curr_date = start_date
        while curr_date <= end_date:
            date_list.append(curr_date)
            curr_date += datetime.timedelta(days=1)
        return date_list

    start_date = datetime.datetime(time_from[2], time_from[1], time_from[0])
    stop_date = datetime.datetime(time_to[2], time_to[1], time_to[0])
    date_list = date_range_list(start_date, stop_date)
    date_list = [dt.strftime('%Y-%m-%d').split('-') for dt in date_list]
    return date_list



def get_station_time_intervals(path_db, data_format='IAGA2002'):
    """
    :param path_db: DB of paths of stations
    :param data_format:
    :return: {'khb': [[unix_time_start, unix_time_stop]],
              'mgd': [[unix_time_start, unix_time_stop]], ...}
    """

    station_time_intervals = {}

    for station_key in path_db.keys():
        station_time_intervals[station_key] = []
        time_range = []
        if data_format == 'ADD':
            station_key = station_key.upper()
        for i, station_date in enumerate(path_db[station_key].keys()):
            if data_format == 'IAGA2002':
                time_range.append(datetime.datetime(int(station_date[:4]),  # y
                                                    int(station_date[4:6]),  # m
                                                    int(station_date[6:])))  # d
            elif data_format == 'IAF':
                time_range.append(datetime.datetime(int(station_date[:4]),  # y
                                                    int(station_date[4:6]), 1))  # m
            elif data_format == 'ADD':
                time_range.append(datetime.datetime(int(station_date[:4]),  # y
                                                 1, 1))  # m
        time_intervals = []
        start_int = time_range[0]
        if data_format == 'IAGA2002':
            for i, ct in enumerate(time_range):
                if ct - time_range[i - 1] > datetime.timedelta(days=1):
                    #print([start_int, time_range[i - 1]])
                    time_intervals.append([start_int, time_range[i - 1]])
                    start_int = ct
        elif data_format == 'IAF':
            for i, ct in enumerate(time_range):
                if ct - time_range[i - 1] > datetime.timedelta(days=32):
                    time_intervals.append([start_int, time_range[i - 1]])
                    start_int = ct
        elif data_format == 'ADD':
            for i, ct in enumerate(time_range):
                if ct - time_range[i - 1] > datetime.timedelta(days=366):
                    time_intervals.append([start_int, time_range[i - 1]])
                    start_int = ct
        print(time_intervals, 'INTERVALS TOTAL')
        if len(time_intervals) == 0:
            # append time interval im unix time
            station_time_intervals[station_key].append(
                [int((time_range[0]+datetime.timedelta(hours=23)).timestamp()),
                 int((time_range[-1]+datetime.timedelta(hours=23)).timestamp())])
    return station_time_intervals


def station_in_dt_range_FTP(time_range, station_db, data_format='IAGA2002'):

    station_list = []
    for (YY, mm, dd) in time_range:
        if data_format == 'IAGA2002':
            stations = station_db[YY][mm][dd]
        elif data_format == 'IAF':
            stations = station_db[YY][mm]
        elif data_format == 'ADD':
            stations = station_db[YY]
        for station in stations:
            if station not in station_list:
                station_list.append(station)
    return station_list

def get_path_station_in_range_FRP(time_range, station_list, path_db, data_format='IAGA2002'):
    path_list = []
    if data_format == 'IAGA2002':
        for (YY, mm, dd) in time_range:
            for station in station_list:
                try:
                    path = path_db[station][YY + mm + dd]
                    path_list.append(path)
                except:
                    pass
    elif data_format == 'IAF':
        for i, (YY, mm, dd) in enumerate(time_range):
            if i!=0 and time_range[i-1][0] == YY and time_range[i-1][1] == mm:
                continue
            else:
                for station in station_list:
                    try:
                        path = path_db[station][YY + mm]
                        path_list.append(path)
                    except:
                        pass
    elif data_format == 'ADD':
        for i, (YY, mm, dd) in enumerate(time_range):
            if i!=0 and time_range[i - 1][0] == YY:
                continue
            else:
                for station in station_list:
                    try:
                        path = path_db[station][YY]
                        path_list.append(path)
                    except:
                        pass
    return path_list

