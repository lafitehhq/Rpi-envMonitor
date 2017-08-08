#!/usr/bin/python3
#-*- coding:utf-8 -*-

import sqlite3
import time
import sys 
import datetime
from MyRpiState import RpiNetWork
from MyRpiState import RpiSystem
from MyAirQuality import AirQuality
from MyGpioDev import DHT11
from MyGpioDev import BackLight
from MyI2cDev import PCF8591

class sysState:
	def __init__(self):
		self.sys =  RpiSystem()		# 系统信息类
		self.net = RpiNetWork()		# 网络信息类
		self.cpu_t = 0     			# CPU温度
		self.loading = 0			# CPU loading
		self.mem = ""				# 内存信息
		self.disk = ""				# 磁盘使用率
		self.uptime = ""			# 开机时间
		self.ip = "192.168.0.1"		# IP地址
		self.ping = 0				# ping google

class sensorState:
	def __init__(self):
		self.air = AirQuality(18)		# 空气质量检测传感器类
		self.dht11 = DHT11(24,25)		# 温湿度传感器类
		self.bl = BackLight(26)		# 背光类
		self.pcf = PCF8591(4)		# 数模转换、光照传感器类
		self.temperature = 0		# 温度
		self.humidity = 0			# 湿度
		self.pm25 = 0				# PM2.5
		self.pm10 = 0				# PM10
		self.light = 0				# 光照强度
		

# 全局变量，定义状态变量
sys = sysState()
sen = sensorState()
mode = 2	# 0-静止状态（什么都不做），1-激活状态，2-日常状态

def normal_loop(info):
	while mode > 0:
		sys.uptime = sys.sys.uptime()
		sys.ip = sys.net.public_ip()
		print("开机时间：%s， IP地址:%s" %(sys.uptime,sys.ip))
		info.uptime['text'] = "开机时间：%s" %sys.uptime
		info.ip['text'] = "IP地址: %s" %sys.ip
		time.sleep(3000) #30min
	print("normal loop stopped")
	
	
def special_loop(info):
	while mode > 0:
		print('mode=%d' %mode)
		# power on devices
		sen.air.powerOn()
		sen.dht11.powerOn()
		sen.pcf.powerOn()
		
		# get info
		(sen.pm25, sen.pm10) = sen.air.getData()
		(sen.humidity, sen.temperature) = sen.dht11.get()
		sys.disk = sys.sys.disk_stat()
		print("天气： %d℃，湿度%d%%, 空气质量PM2.5=%d, PM10=%d" %(sen.temperature,sen.humidity,sen.pm25,sen.pm10))
		print("磁盘使用：%s" %sys.disk)
		# UI更新部分信息
		info.temperature['text'] = "温度：%d℃" %sen.temperature
		info.humidity['text'] = "湿度：%d%%" %sen.humidity
		info.pm25['text'] = "PM2.5: %d" %sen.pm25
		info.pm10['text'] = "PM10: %d" %sen.pm10
		#info.light['text'] = "光照条件：%s" 			# 光照强度
		info.disk['text'] = "磁盘使用：%s" %sys.disk
		
		if mode==1:		# 激活状态
			(_, _, sys.mem)=sys.sys.memory_stat()
			sys.cpu_t = sys.sys.cpu_temp()
			sys.loading = sys.sys.cpu_load()
			sys.ping = sys.net.ping()
			print("系统： CPU温度%.1f'C，占用率%.1f%%，内存使用 %d%%, ping回应：%.2fms" %(sys.cpu_t, sys.loading, sys.mem, sys.ping))
			info.sys['text'] = "CPU温度%.1f℃，占用率%.1f%%，内存使用 %d%%, ping回应：%.2fms" %(sys.cpu_t, sys.loading, sys.mem, sys.ping)
			
		else:
			print("!!!!! get here!!!!")
			info.sys['text'] = "日常模式，点击按钮切换到实时监控模式"
			# power off devices
			sen.air.powerOff()
			sen.dht11.powerOff()
			sen.pcf.powerOff()
			
		#休眠
		for i in range(600): #10min
			time.sleep(1)
			#print('test,mode=%d' %mode)
			if mode!=2: # active mode or need stop 
				break

	# loop stop	
	print("special loop stopped")


def setMode(new):
	global mode
	mode = new
	print('set , mode=%d' %mode)
	return mode
	
def getMode():
	return mode
