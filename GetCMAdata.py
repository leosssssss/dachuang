import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
def GetInfo(url, time, nums):
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
        #如果不够10则在前面补0
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
    #获取包含预测数据的json文件
    responseDict = json.loads(rsp.text)
    points = responseDict['points']
    for point in points:
        forecasts = []
        if len(point['forecast']) != 0:
            forecasts = point['forecast']
        forecastList = []   #用列表接预测的数据
        for forecast in forecasts:
            if forecast['tm'] == '中国':
                forecastList.append(forecast['forecastpoints'])
        if len(forecastList) != 0:
            saveData.write(str(forecastList) + "\n")
        else:
            continue
        forecastList = forecastList[0]
    response.close()
    return saveData


url = 'https://typhoon.slt.zj.gov.cn/Api/TyphoonInfo/'   #台风路径的发布网站
startTime = 2009
for time in range(startTime, 2024):
    os.makedirs(f'./typhoon/{str(time)}')
    for num in range(50):
        GetInfo(url, time, num)
    print(str(time) + 'done')
print('done')









