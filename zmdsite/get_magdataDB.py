from zipmagdata.settings import FTP_DIR, FTP1_DIR
import os


def get_ftp_db(data_format='IAGA2002'):
    """
    true irt 2021 12 24
    # false khb 2021 06 20


    print(MAGDATA_DT_DICT['2021']['12']['24'])
    print(MAGDATA_DT_DICT['2021']['12']['24'])

    print(MAGDATA_STATIONS_PATH['irt']['20211224'])

    """
    if data_format == 'iaga2002':
        dir_path = os.path.join(FTP_DIR, 'IAGA2002')
    elif data_format == 'iaf':
        dir_path = os.path.join(FTP_DIR, 'IAF')
    elif data_format == 'add':
        dir_path = FTP1_DIR

    FTP1_EXCEPTION_DIR = ['Soft', 'tmp']

    MAGDATA_DT_DICT = {}    # возвращает доступные станции по DICT['2021']['12']['24']
    MAGDATA_STATIONS_PATH = {}  # возвращает путь к файлу через station_path['irt']['20211224']

    for year in os.listdir(dir_path):
        if data_format == 'IAGA2002' or data_format == 'IAF':
            MAGDATA_DT_DICT[year] = {}  # добавляем года в папке
            for mount in os.listdir(os.path.join(dir_path, year)):
                if data_format == 'IAGA2002':
                    MAGDATA_DT_DICT[year][mount] = {}  # добавляем месяца
                    mouth_path = os.path.join(os.path.join(dir_path, year), mount)
                    for filename in os.listdir(mouth_path):
                        station = filename[:3]
                        s_year, s_mount, s_day = filename[3:7], filename[7:9], filename[9:11]
                        if s_day not in MAGDATA_DT_DICT[year][mount]:
                            MAGDATA_DT_DICT[year][mount][s_day] = []
                        MAGDATA_DT_DICT[year][mount][s_day].append(station)  # станции в текущую дату
                        if station not in MAGDATA_STATIONS_PATH:
                            MAGDATA_STATIONS_PATH[station] = {}
                        MAGDATA_STATIONS_PATH[station][s_year + s_mount + s_day] = os.path.join(mouth_path,
                                                                                                filename)
                elif data_format == 'IAF':
                    mouth_path = os.path.join(os.path.join(dir_path, year), mount)
                    MAGDATA_DT_DICT[year][mount] = []
                    for filename in os.listdir(mouth_path):
                        station = str(filename[:3]).lower()
                        MAGDATA_DT_DICT[year][mount].append(station)  # станции в текущий месяц
                        if station not in MAGDATA_STATIONS_PATH:
                            MAGDATA_STATIONS_PATH[station] = {}
                        MAGDATA_STATIONS_PATH[station][year + mount] = os.path.join(mouth_path,
                                                                                    filename)
        else:   # if ADD
            if year not in FTP1_EXCEPTION_DIR:
                MAGDATA_DT_DICT[year] = []  # добавляем года в папке
                for station in os.listdir(os.path.join(FTP1_DIR, year)):
                    station = station.lower()
                    MAGDATA_DT_DICT[year].append(station)
                    if station not in MAGDATA_STATIONS_PATH:
                        MAGDATA_STATIONS_PATH[station] = {}
                    if year not in MAGDATA_STATIONS_PATH[station]:
                        MAGDATA_STATIONS_PATH[station][year] = []
                    year_dir = os.path.join(os.path.join(FTP1_DIR, year), station)
                    for filename in os.listdir(year_dir):
                        MAGDATA_STATIONS_PATH[station][year].append(os.path.join(year_dir, filename))

    return MAGDATA_DT_DICT, MAGDATA_STATIONS_PATH

