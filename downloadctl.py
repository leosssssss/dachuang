import calendar
from threading import Thread
import os
import cdsapi
from tkinter import messagebox


c = cdsapi.Client()

dic = {
    'product_type': 'reanalysis',
    'format': 'grib',
    'pressure_level': '500',
    'variable': [
        'divergence', 'temperature', 'u_component_of_wind',
        'v_component_of_wind', 'vorticity',
    ],
    'year': '',
    'month': '',
    'day': [],
    'time': [
        '00:00', '01:00', '02:00',
        '03:00', '04:00', '05:00',
        '06:00', '07:00', '08:00',
        '09:00', '10:00', '11:00',
        '12:00', '13:00', '14:00',
        '15:00', '16:00', '17:00',
        '18:00', '19:00', '20:00',
        '21:00', '22:00', '23:00',
    ],
}


def DownLoad(year, month):
    f = open("redownload.txt", 'r')
    existedFiles = [dates.replace('\n', '') for dates in f.readlines()]
    days = calendar.monthrange(year, month)[1]
    dic['year'] = str(year)
    dic['month'] = str(month).zfill(2)
    dic['day'] = [str(i).zfill(2) for i in range(1, days + 1)]
    filename = 'E:\\' + str(year) + str(month).zfill(2) + '.grib'
    if os.path.exists(filename) and filename in existedFiles:
        return None
    c.retrieve('reanalysis-era5-pressure-levels', dic, filename)
    RFT(filename)
    messagebox.showinfo("attention!", f"file {filename[4:10]}has downloaded!")


def DownLoad1():
    for year in range(1949, 1964):
        for month in range(1, 13):
            DownLoad(year, month)


def DownLoad2():
    for year in range(1964, 1978):
        for month in range(1, 13):
            DownLoad(year, month)


def DownLoad3():
    for year in range(1978, 1992):
        for month in range(1, 13):
            DownLoad(year, month)


def DownLoad4():
    for year in range(1992, 2006):
        for month in range(1, 13):
            DownLoad(year, month)


def DownLoad5():
    for year in range(2006, 2020):
        for month in range(1, 13):
            DownLoad(year, month)


def StartDownload():
    t1 = Thread(target=DownLoad1, args=())
    t2 = Thread(target=DownLoad2, args=())
    t3 = Thread(target=DownLoad3, args=())
    t4 = Thread(target=DownLoad4, args=())
    t5 = Thread(target=DownLoad5, args=())
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()


def RFT(filename):
    with open("redownload.txt", 'a') as f:
        f.write(filename+'\n')


StartDownload()

