import calendar
import os
import warnings
from threading import Thread

import cdsapi
import metpy.calc as mpcalc
import numpy as np
import xarray as xr
from metpy.units import units

warnings.filterwarnings("ignore")
def IO( ):
    print("welcome to use this module! more information can be found at README.md")
    '''
    控制输入输出命令的函数，通过读取控制文件以获得关于台风数据、降水数据、ERA数据的地址、时间等信息
    '''
    returnDict = {}
    fileName = str(input("please input the file name of control file: "))
    if fileName[-4:] != '.txt':
        raise [NameError('the control file name must end with".txt"')]
    try:
        f = open(fileName, 'r')
    except IOError:
        raise [NameError('the control file does not exist')]
    files = f.readlines()
    for line in files:
        line = line.split(" ")
        if line[0] == 'dataset':    #本行为数据集的情况
            if line[1] == 'typhoon':     #读取台风数据的地址
                typhoon = line[2]
                returnDict['typhoon'] = typhoon
            elif line[1] == 'precipitation':    #读取降水数据的地址
                precipitation = line[2]
                returnDict['precipitation'] = precipitation
            elif line[1] == 'ERA':  #读取ERA数据的地址
                ERA = line[2]
                returnDict['ERA'] = ERA
            else:
                raise [NameError('the dataset must be typhoon, precipitation or ERA')]
        if line[0] == 'timeset':    #本行为时间的情况
            if len(line) != 3:
                raise [NameError('the timeset must have 2 elements: start and end time')]
            startTime = line[1]
            returnDict['startTime'] = startTime
            endTime = line[2]
            returnDict['endTime'] = endTime
    '''
    未来可能存在其他接口函数，目前留空
    '''
    return returnDict


def ToQ(num):
    '''
    :param num: 待传入的数值
    :return: 返回四分后的传入数据
    '''
    if (num % 1 < 2):
        num = int(num)
    elif (num % 1 < 5) and (num % 1 >= 2):
        num = int(num) + 0.25
    elif (num % 1 < 8) and (num % 1 >= 5):
        num = int(num) + 0.5
    else:
        num = int(num) + 1
    return num


def ToO(num):
    '''
    :param num: 待传入的数值
    :return: 返回八分后的传入数据
    '''
    decimal = int((num % 1) / 0.125)
    if decimal == 0 or decimal == 1:
        num = int(num) + 0.125
    elif decimal == 2 or decimal == 3:
        num = int(num) + 0.375
    elif decimal == 4 or decimal == 5:
        num = int(num) + 0.625
    elif decimal == 6 or decimal == 7:
        num = int(num) + 0.875
    else:
        num = int(num) + 1
    return num


def MeanCurl(f, lat, lon):
    """
    :param f: 传入的xarray文件
    :param lat: 台风的纬度坐标
    :param lon: 台风的经度坐标
    :return: 返回传入数据的旋度
    """
    r = 500 * units.km
    deltaLat = ToQ(r / (111 * units.km))
    deltaLon = ToQ(r / (111 * np.cos(lat * np.pi / 180) * units.km))
    latStart = lat + deltaLat
    latEnd = lat - deltaLat
    lonStart = lon - deltaLon
    lonEnd = lon + deltaLon
    latitude = slice(latStart, latEnd)
    longitude = slice(lonStart, lonEnd)
    du = f.u.sel(latitude=latitude, longitude=longitude,isobaricInhPa=500).values * units.m * units.s ** -1
    dv = f.v.sel(latitude=latitude, longitude=longitude,isobaricInhPa=500).values * units.m * units.s ** -1
    dx0 = np.arange(lat - deltaLat, lat + deltaLat, 0.25)
    dy0 = np.arange(lon - deltaLon, lon + deltaLon, 0.25)
    dx, dy = mpcalc.lat_lon_grid_deltas(longitude=dy0, latitude=dx0)
    curl = mpcalc.vorticity(u=du, v=dv, dx=dx, dy=dy)
    curlMean = np.mean(curl.m)  # .m方法可以去除符号
    return curlMean


def DimReduMean(dataset):
    """
    :param dataset: 输入的数据
    :return: 按行平均降重后的数据
    """
    dr = []
    for data in np.nditer(dataset):
        reduced = np.mean(data)
        dr.append(reduced)
    return dr


def OneWave(data):
    """
    :param data: 传入的数据
    :return: 返回取得一波非对称信息后的数据
    """
    fr = np.fft.fft(data)
    fr1 = fr[1]
    A = np.sqrt(fr1.imag ** 2 + fr1.real ** 2)
    maxI = fr1[A == max(A)]
    maxA = max(A)
    angle = np.angle(maxI)
    returnList = [maxA, angle]
    return returnList


def ReadLsm(file, lat, lon):
    """
    :param file: 待读取的数据
    :param lat: 中心纬度
    :param lon: 中心经度
    :return: 返回以传入经纬度500km范围内的所有海陆遮罩数据
    """
    r = 500 * units.km
    deltaLat = ToQ(r / (111 * units.km))
    deltaLon = ToQ(r / (111 * np.cos(lat * np.pi / 180) * units.km))
    latStart = lat + deltaLat
    latEnd = lat - deltaLat
    lonStart = lon - deltaLon
    lonEnd = lon + deltaLon
    latitude = slice(latStart, latEnd)
    longitude = slice(lonStart, lonEnd)
    lsm = file.lsm.sel(latitude=latitude, longitude=longitude,).values
    return lsm


def MeanV(file, lat, lon):
    """
    :param file: 待读取的数据
    :param lat: 中心纬度
    :param lon: 中心经度
    :return: 返回以传入经纬度500km范围内的平均水平风数据
    """
    r = 500 * units.km
    deltaLat = ToQ(r / (111 * units.km))
    deltaLon = ToQ(r / (111 * np.cos(lat * np.pi / 180) * units.km))
    latStart = lat + deltaLat
    latEnd = lat - deltaLat
    lonStart = lon - deltaLon
    lonEnd = lon + deltaLon
    latitude = slice(latStart, latEnd)
    longitude = slice(lonStart, lonEnd)
    v = file.v.sel(latitude=latitude, longitude=longitude, isobaricInhPa=500).values
    vMean = np.mean(v)
    return vMean


def ReadPreci(file, lat, lon):
    """
    :param file: 待读取的数据
    :param lat: 中心纬度
    :param lon: 中心经度
    :return: 返回以传入经纬度500km范围内的所有降水数据
    """
    lat = lat
    lon = lon
    r = 500 * units.km
    deltaLat = ToQ(r / (111 * units.km))
    deltaLon = ToQ(r / (111 * np.cos(lat * np.pi / 180) * units.km))
    latStart = ToO(lat - deltaLat)
    latEnd = ToO(lat + deltaLat)
    lonStart = ToO(lon - deltaLon)
    lonEnd = ToO(lon + deltaLon)
    p = file.precipitation.sel(lat=slice(latStart, latEnd),
                               lon=slice(lonStart, lonEnd)).values
    return p


'''
接下来是启用多线程下载的部分
'''


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
'''
以上是从ERA5中下载数据的request格式
'''


def DownLoad(year, month):
    '''
    :param year: 下载的年份
    :param month: 下载的月份
    :return: 无返回值
    '''
    days = calendar.monthrange(year, month)[1]
    dic['year'] = str(year)
    dic['month'] = str(month).zfill(2)
    dic['day'] = [str(i).zfill(2) for i in range(1, days + 1)]
    filename = 'E:\\' + str(year) + str(month).zfill(2) + '.grib'
    if os.path.exists(filename):
        return None
    else:
        c.retrieve('reanalysis-era5-pressure-levels', dic, filename)
    return None

def StartDownload(start, end, threadNum=5):
    '''
    :param start: 下载的起始年份
    :param end: 下载的中止年份
    :param threadNum: 下载时启动的线程数，默认为5
    :return: 无返回值
    '''
    width = (end - start)/threadNum
    threads = []
    for num in range(threadNum):
        thread = Thread(target=DownLoad, args=(start+num*width, start+(num+1)*width))
        threads.append(thread)
    for thread in threads:
        thread.start()
    return None


def DownloadInitERA(start, end):
    '''
    开始下载时系统初始化的函数
    :return:
    '''
    print("please input thread number, the default is 5")
    try:
        threadNum = int(input())
    except ValueError:
        print('detected there something wrong with input, it has been reset to 5')
        threadNum = 5
    StartDownload(start=start, end=end, threadNum=threadNum)


def Init():
    """
    初始化系统的函数
    :return:
    """
    requestDict = IO()
    if input('Do you want to download ERA5 data? (y/n) ') == 'y':
        DownloadInitERA(requestDict['startTime'], requestDict['endTime'])
    else:
        print('we are not going to download ERA5 data')
    if input("Do you want to download TRMM data? (y/n) ") == 'y':
        pass
    else:
        print('we are not going to download TRMM data')


file = xr.open_dataset("E:\\ERA5\\2014\\e5_2014010100.grib", engine="cfgrib")
precipitation = xr.open_dataset("D:\\datas\\dachuang\\precipitation\\3B42RT.2000030100.7R2.nc4", engine="netcdf4")
lat = 23.16
lon = 113.23
print(ReadPreci(precipitation, lat, lon))
