import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import warnings
import eccodes
import cfgrib
warnings.filterwarnings("ignore")
def PotentialVorticity(vo, t, P=500):
	"""
	:param vo: 输入等压面的位涡
	:param t: 输入等压面的温度
	:param P: 等压面层
	:return: 返回位涡
	"""
	minimum = min(vo.shape[0], vo.shape[1])
	vo = vo[:minimum, :minimum]
	t = t[:minimum, :minimum]	# 保存为方阵便于计算
	R = 8.3144626   #气体常数R
	_rho = R*t/P #500hPa密度的倒数
	theta = t*(1000/P)**0.286    #500hPa上的位温
	C = np.identity(np.shape(t)[1]) - 1/np.shape(t)[1]*np.ones(np.shape(t)[1])    #中心阵
	D_theta = np.dot(np.dot(theta, C), theta.T) #位温的散度
	potentialVorticity = np.dot(np.dot(_rho, vo), D_theta)
	return potentialVorticity


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
	angle.tolist()
	returnList = [maxA, angle]
	return returnList

adressF = 'D:/datas/dachuang/台风预测数据/typhoon(CHINA)/typhoon forecast data.csv'
adressLSM = "D:/datas/dachuang/masks/IMERG_land_sea_mask.nc"
adressERAH = "E:/data/"
adressERAT = ".grib"
adressGeopotential = "D:/datas/dachuang/masks/Geopotential.grib"

adressFL = '/mnt/d/datas/dachuang/台风预测数据/typhoon(CHINA)/typhoon forecast data.csv'
adressLSML = "/mnt/d/datas/dachuang/masks/IMERG_land_sea_mask.nc"
adressERAHL = "/mnt/e/data/"
adressERATL= ".grib"
adressGeopotentialL = "/mnt/d/datas/dachuang/masks/Geopotential.grib"
def Operate(adressForcast, adressLSMData, adressERAHData, adressERATData, adressGeopotentialData):
	'''
	:param adressForcast: 台风预测数据的地址
	:param adressLSMData: 海陆遮罩的数据地址
	:param adressERAHData: ERA5数据所在的文件夹
	:param adressERATData: .grib
	:param adressGeopotentialData: 地势数据所在的地址
	:return:
	'''
	# 完成了！
	Frange = 4.5
	reDataFrame = pd.DataFrame()
	forecastData = pd.read_csv(adressForcast, index_col=0, low_memory=False)
	LSMask = xr.open_dataset(adressLSMData)
	geopotential = xr.open_dataset(adressGeopotentialData, engine='cfgrib')
	newDataFrame = pd.DataFrame()
	for i in range(0, forecastData.shape[0]):
		month = forecastData.loc[i, 'time+0'][0:4]+forecastData.loc[i, 'time+0'][5:7]
		time = forecastData.loc[i, 'time+0']
		lon = forecastData.loc[i, 'lon+0']
		lat = forecastData.loc[i, 'lat+0']
		ERA = xr.open_dataset(adressERAHData + month + adressERATData, mask_and_scale=False, engine='cfgrib')
		print(i)
		d500 = ERA.d.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values #500hPa的散度
		d500M = d500.mean()
		u500 = ERA.u.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values #500hPa的水平风速
		u500M = u500.mean()
		vo500 = ERA.vo.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values   #500hPa的绝对涡度
		t500 = ERA.vo.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values    #500hPa的温度
		pv = PotentialVorticity(vo500, t500)    #500hPa的位涡
		pvM = pv.mean()
		LSM = LSMask.landseamask.loc[lat-Frange:lat+Frange, lon-Frange:lon+Frange].values   #海陆遮罩
		G = geopotential.z.loc[lat+Frange:lat-Frange, lon-Frange:lon+Frange].values #地势
		LSMOW = OneWave(LSM)[0]    #海陆遮罩的一波处理
		GOW = OneWave(G)[0] #地势的一波处理
		line = [u500M, d500M, pvM, LSMOW, GOW]
		cName = ['u500+0', 'd500+0', 'pv+0', 'LSMOW', 'GOW']
		line = pd.DataFrame(line).T
		line.columns = cName
		print(line)
		newDataFrame = pd.concat([newDataFrame, line])
		newDataFrame = newDataFrame.reset_index(drop=True)
	reDataFrame = pd.concat([forecastData, newDataFrame], axis=1)
	reDataFrame.to_csv('/mnt/d/datas/dachuang/台风预测数据/typhoon(CHINA)/typhoon forecast data1.csv')


def Rolling(forecastData, delta=4):
	"""
	:param forecastData: 处理过后的台风数据（dataframe），接下来用于滑动窗口
	:param delta: 时间间隔，默认为4x6=24h
	:return:
	"""
	# col = ['lon+0', 'lat+0', 'u500+0', 'd500+0', 'pv+0', 'LSMOW+0', 'GOW+0']	#要改的维度
	# forecastData1 = forecastData.groupby('nums')	#为台风分组，方便后续滑动窗口运算
	# TCDataFrame = pd.DataFrame()
	# for nums, data in forecastData1:
	# 	# 将所有数据按台风序号划分
	# 	data['index'] = range(len(data))
	# 	if data.shape[0] <= delta:
	# 		continue
	# 	else:
	# 		reDataFrame = pd.DataFrame()
	# 		for index in range(delta, data.shape[0]):
	# 			# 在每个台风中使用滑动窗口
	# 			line = pd.DataFrame(data.loc[data['index'] == index-1, col])	# 初始化第一行
	# 			line.columns = [c[0:-2] + '-1' for c in col]
	# 			for i in range(delta-1):
	# 				# 将delta区间内的数据逐个添加到原数据上
	# 				l = data.loc[data['index'] == index - i-2, col]
	# 				l.columns = [c[0:-2]+str(-i-2) for c in col]
	# 				l.index = [line.index[0]]
	# 				line = pd.concat([line, l], axis=1)
	# 			line = line.reset_index()
	# 			reDataFrame = pd.concat([reDataFrame, line], )
	# 			reDataFrame = reDataFrame.reset_index(drop=True)
	# 		reDataFrame['index'] = reDataFrame['index']+1
	# 		reDataFrame.set_index(reDataFrame['index'], inplace=True)
	# 		reDataFrame.drop(['index'], axis=1, inplace=True)
	# 		reDataFrame = reDataFrame.rename_axis(None)
	# 		#forecastData = pd.concat([forecastData, reDataFrame], axis=1)
	# 		TCDataFrame = TCDataFrame.append(reDataFrame)
	# forecastData = pd.concat([forecastData, TCDataFrame], axis=1)
	# forecastData = forecastData.dropna(subset=['GOW-4'])

	col = ['lon+0', 'lat+0']	#要改的维度
	forecastData1 = forecastData.groupby('nums')	#为台风分组，方便后续滑动窗口运算
	reDataFrame = pd.DataFrame()
	for nums, data in forecastData1:
		# 将所有数据按台风序号划分
		data['index'] = range(len(data))
		if data.shape[0] <= delta:
			continue
		else:
			for index in range(delta, data.shape[0]):
				# 在每个台风中使用滑动窗口
				line = pd.DataFrame(data.loc[data['index'] == index, col])	# 初始化第一行
				line.index = [line.index[0] - 1]
				line.columns = ['rlon+1', 'rlat+1']
				reDataFrame = pd.concat([reDataFrame, line])
	forecastData = pd.concat([forecastData, reDataFrame], axis=1)
	forecastData = forecastData.dropna(subset=['rlat+1'])
	forecastData = forecastData.reset_index()
	return forecastData


def Autocorrelation(adressForcast, delay=10):
	"""已经完成了求时间序列，后续还剩求自相关系数"""
	#已完成
	forcastData = pd.read_csv(adressForcast, index_col=0, low_memory=False)
	l = 300
	ac = np.zeros((l, 2))   #返回的序列
	temp = np.zeros((l, 2)) #暂时存储
	num = 200901
	t = 0
	cnt = 0 #记录次数
	for i in range(forcastData.shape[0]):
		if num != forcastData.loc[i, 'nums']:
			num = forcastData.loc[i+1, 'nums']
			ac += temp
			temp = np.zeros((l, 2))
			t = 0
			cnt += 1
		else:
			temp[t, 0] = forcastData.loc[i, 'speed+0']
			temp[t, 1] = forcastData.loc[i, 'pressure+0']
			t += 1
	ac /= cnt
	ac = ac[0:30, ...]
	coefSpeed = autocorrelation(ac[...,0], delay)
	coefPressure = autocorrelation(ac[...,1], delay)
	return [coefSpeed, coefPressure]


def autocorrelation(x,lags, n=None):#计算lags阶以内的自相关系数，返回lags个值，将序列均值、标准差视为不变
	#已完成
	n = len(x)
	x =np.array(x)
	variance = x.var()
	x = x-x.mean()
	result = np.correlate(x, x, mode = 'full')[-n+1:-n+lags+1]/\
		(variance*(np.arange(n-1,n-1-lags,-1)))
	return result


def ShowFig():
	#已完成
	plt.plot(Autocorrelation(adressF, 15)[0], c='b', label='original value')
	plt.plot(abs(Autocorrelation(adressF, 15)[0]), c='r', label='absolute value')
	plt.axhline(0, color='k', linestyle='--')
	plt.xlabel("time interval (per 6 hours)")
	plt.ylabel("autocorrection coefficient")
	plt.title("autocorrection of speed")
	plt.legend()
	plt.show()



def Pop(forecastData):
	"""
	统一deltaT为6h
	:param forecastData: 读入的台风预报数据
	:return:
	"""
	#已完成
	forecastData['time+0'] = pd.to_datetime(forecastData['time+0'])
	for i in range(forecastData.shape[0]-1):
		if i+1 >= forecastData.shape[0]:
			return forecastData
		if(forecastData.loc[i+1, 'time+0'] - forecastData.loc[i, 'time+0'] < timedelta(hours=6))and(forecastData.loc[i+1, 'nums'] == forecastData.loc[i, 'nums']):
			print(forecastData.loc[i + 1, 'time+0'] - forecastData.loc[i, 'time+0'], forecastData.loc[i, 'nums'], i)
			forecastData = forecastData.drop(forecastData[(forecastData['nums']==forecastData.loc[i, 'nums']) & (timedelta(hours=0)< forecastData['time+0']-forecastData.loc[i, 'time+0']) & (forecastData['time+0']-forecastData.loc[i, 'time+0']<timedelta(hours=6))].index)
			forecastData = forecastData.reset_index(drop=True)
			print(forecastData.loc[i + 1, 'time+0'] - forecastData.loc[i, 'time+0'], i, forecastData.shape, '\n')
		if i+1 >= forecastData.shape[0]:
			return forecastData
	return forecastData


def TrainTestSplit(forecastData):
	pass

# 别乱动
forecastData = pd.read_csv(adressF, index_col=0, low_memory=False)
# Operate(adressFL, adressLSML, adressERAHL, adressERATL, adressGeopotentialL)
# pd.set_option('display.max_columns', None)
DFSave = Rolling(forecastData, delta=1)
DFSave.to_csv('D:/datas/dachuang/台风预测数据/typhoon(CHINA)/typhoon forecast data2.csv')