import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import ast
import datetime
import numpy as np


def GetInfo(url, time, nums, country='中国'):
    '''
    time: 需要搜索的台风年份
    nums: 需要搜索的台风序号
    :param url: 需要传入的网址
    :return: 返回解析完成的内容
    '''
    if nums < 10:
        nums = '0' + str(nums)
    else:
        nums = str(nums)
        # 如果不够10则在前面补0
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/115.0.0.0 Safari/537.36"}  # 反爬用的识别号，根据自己电脑浏览器的型号自行更改
    response = requests.get(url + str(time) + nums, headers=headers)
    response.encoding = 'utf-8'
    reText = response.text
    if reText == '':
        return
    saveData = open(f'./typhoon/{str(time)}/data{str(time)}{str(nums)}.txt', 'a+', encoding='utf-8')
    rsp = BeautifulSoup(reText, 'html.parser')
    rsp.prettify()
    # 获取包含预测数据的json文件
    responseDict = json.loads(rsp.text)
    points = responseDict['points']
    for point in points:
        forecasts = []
        if len(point['forecast']) != 0:
            forecasts = point['forecast']
            forecast = forecasts[0]
        forecastList = []  # 用列表接预测的数据
        for forecast in forecasts:
            if forecast['tm'] == country:
                forecastList.append(forecast['forecastpoints'])
            else:
                continue
        if len(forecastList) != 0:
            saveData.write(str(forecastList[0]) + "\n")
        else:
            continue
        forecastList = forecastList[0]
    saveData.close()
    response.close()
    return saveData


def DataArrange(year=2009, endYear=datetime.datetime.today().year):
    names = ['time', 'lon', 'lat', "strong", "power", "speed", "pressure"]
    pdData = pd.read_csv('D:\datas\python\dachuang\\typhoon(CHINA)\\typhoon forecast data3.csv',
                           names=['nums', 'time+0', 'lon+0', 'lat+0', "strong+0", "power+0", "speed+0", "pressure+0"])
    index = 0
    for year in range(year, endYear):
        folderPath = f'D:\datas\python\dachuang\\typhoon(CHINA)\\{str(year)}'
        for nums in range(len(os.listdir(folderPath))):
            nums = nums + 1
            if nums < 10:
                nums = '0' + str(nums)
            else:
                nums = str(nums)
            filename = folderPath + f'\data{str(year)}{nums}.txt'
            if os.path.exists(filename) == False:
                continue
            typhoonForecast = open(filename, "r", encoding='utf-8')
            for line in typhoonForecast:
                points = line[1:-2]
                points = ast.literal_eval(points)
                for i in range(len(points)):
                    point = points[i]
                    pdData.loc[index, 'nums'] = str(year) + str(nums)
                    pdData.loc[index, "time+" + str(i)] = point['time']
                    pdData.loc[index, "lon+" + str(i)] = point['lng']
                    pdData.loc[index, "lat+" + str(i)] = point['lat']
                    pdData.loc[index, "strong+" + str(i)] = point['strong']
                    pdData.loc[index, "power+" + str(i)] = point['power']
                    pdData.loc[index, "speed+" + str(i)] = point['speed']
                    pdData.loc[index, "pressure+" + str(i)] = point['pressure']
                index += 1
    pdData.to_csv('D:\datas\python\dachuang\\typhoon(CHINA)\\typhoon forecast data3.csv')
    return 'yes'


url = 'https://typhoon.slt.zj.gov.cn/Api/TyphoonInfo/'  # 台风路径的发布网站


def GetData(startTime=2009, endTime=datetime.datetime.today().year, country='中国'):
    '''
    :param startTime: 数据的开始时间
    :param endTime: 数据的结束时间
    :param country: 选择整理的区域
    :return: 成功则返回0
    '''
    for time in range(startTime, endTime):
        os.makedirs(f'./typhoon/{str(time)}')
        for num in range(50):
            GetInfo(url, time, num, country)
        print(str(time) + 'done')
    print('done')
    return 0


def PreAnalysis():
    '''
    本函数用于优化数据，添加了真实数据用于对比
    :return: 成功则返回0
    '''
    adress = './/typhoon(CHINA)//typhoon forecast data.csv'
    forecastData = pd.read_csv(adress, low_memory=False, encoding='GBK')
    forecastData = forecastData.drop_duplicates()
    cnt = 0
    for i in range(forecastData.shape[0]):
        i -= cnt
        index = forecastData[(forecastData['time+0']==forecastData.iloc[i, 8])&(forecastData['nums']==forecastData.iloc[i, 0])].index.to_list()
        if index == []:
            forecastData.drop(index=[i], axis=0, inplace=True)
            forecastData = forecastData.reset_index(drop=True)
            cnt += 1
        else:
            index = index[0]
            forecastData.loc[i, 'forecastLon'] = forecastData.loc[index, 'lon+0']
            forecastData.loc[i, 'forecastLat'] = forecastData.loc[index, 'lat+0']
            forecastData.loc[i, 'forecastPower'] = forecastData.loc[index, 'power+0']
            forecastData.loc[i, 'forecastPressure'] = forecastData.loc[index, 'pressure+0']
            forecastData.loc[i, 'forecastSpeed'] = forecastData.loc[index, 'speed+0']
    adressNew = './/typhoon(CHINA)//typhoon forecast data3.csv'
    forecastData.to_csv(adressNew, index=False)
    return 0


def Adjust():
    '''
    :return:用于修正台风预测值（四舍五入）
    '''
    address = "D:\datas\python\dachuang\\typhoon(CHINA)\台风预测值与真实值对照数据（12小时版）（原版） - 副本 - 副本.csv"
    forecastData = pd.read_csv(address, low_memory=False)
    for i in range(forecastData.shape[0]):
        if np.isnan(forecastData.loc[i, 'speed+1']):
            pass
        elif 0 <= forecastData.loc[i, 'speed+1']%10 < 2.5:
            forecastData.loc[i, 'speed+1'] = int(forecastData.loc[i, 'speed+1']/10)*10
        elif 2.5 <= forecastData.loc[i, 'speed+1']%10 < 5:
            forecastData.loc[i, 'speed+1'] = int(forecastData.loc[i, 'speed+1']/10)*10 + 2.5
        elif 5 <= forecastData.loc[i, 'speed+1']%10 < 7.5:
            forecastData.loc[i, 'speed+1'] = int(forecastData.loc[i, 'speed+1']/10)*10 + 5
        else:
            forecastData.loc[i, 'speed+1'] = int(forecastData.loc[i, 'speed+1']/10)*10 + 7.5

        if np.isnan(forecastData.loc[i, 'pressure+1']):
            pass
        elif 0 <= forecastData.loc[i, 'pressure+1']%10 < 2.5:
            forecastData.loc[i, 'pressure+1'] = int(forecastData.loc[i, 'pressure+1']/10)*10
        elif 5 <= forecastData.loc[i, 'pressure+1']%10 < 7.5:
            forecastData.loc[i, 'pressure+1'] = int(forecastData.loc[i, 'pressure+1']/10)*10 + 5

        if np.isnan(forecastData.loc[i, 'forecastPressure']):
            pass
        elif 0 <= forecastData.loc[i, 'forecastPressure']%10 < 2.5:
            forecastData.loc[i, 'forecastPressure'] = int(forecastData.loc[i, 'forecastPressure']/10)*10
        elif 5 <= forecastData.loc[i, 'forecastPressure']%10 < 7.5:
            forecastData.loc[i, 'forecastPressure'] = int(forecastData.loc[i, 'forecastPressure']/10)*10 + 5

        if np.isnan(forecastData.loc[i, 'forecastSpeed']):
            pass
        if 0 <= forecastData.loc[i, 'forecastSpeed']%10 < 2.5:
            forecastData.loc[i, 'forecastSpeed'] = int(forecastData.loc[i, 'forecastSpeed']/10)*10
        elif 2.5 <= forecastData.loc[i, 'forecastSpeed']%10 < 5:
            forecastData.loc[i, 'forecastSpeed'] = int(forecastData.loc[i, 'forecastSpeed']/10)*10 + 2.5
        elif 5 <= forecastData.loc[i, 'forecastSpeed']%10 < 7.5:
            forecastData.loc[i, 'forecastSpeed'] = int(forecastData.loc[i, 'forecastSpeed']/10)*10 + 5
        else:
            forecastData.loc[i, 'forecastSpeed'] = int(forecastData.loc[i, 'forecastSpeed']/10)*10 + 7.5
    forecastData.to_csv(address, index=False)


Adjust()
'''
使用顺序：
1. GetInfo()
2. DataArrange()
3. PreAnalysis()
4. Adjust()
'''
