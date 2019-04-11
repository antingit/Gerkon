import serial
import os
import time
import datetime
import requests
import json
from ConfigParser import SafeConfigParser
import urllib2
import ssl

config = SafeConfigParser()
config.read("gerkon.cfg")
n1 = config.get("SMS_numbers","n1")
mprt = config.get("PORT_CONFIG_MODEM", "port")
mbrate = config.get("PORT_CONFIG_MODEM" , "baudrate")
prt = config.get("PORT_CONFIG", "port")
brate = config.get("PORT_CONFIG" , "baudrate")
door_id = config.get("DOOR_CONFIG","id")
door_id_nr=config.get("DOOR_CONFIG","door_id_nr")
door_status_url=config.get("DOOR_CONFIG","door_status_url")
odt = config.get("DOOR_CONFIG","open_time")
sms_url = config.get("DOOR_CONFIG","sms_url")

try:
  ser0 = serial.Serial(  #serial port for sms modem
    port = mprt,
    baudrate = int(mbrate)
  )

  ser0.write("AT+CMGF=1\r")
  time.sleep(3)
  ser0.close()
except:
  mesage="modem port not found POST servis active"+"\n"
  print mesage
  pass

def status_send(status_id,door_id_nr):
  url = door_status_url
  info = [{"status":status_id,"doorId":door_id_nr}]
  
  try:
    requests.post(url,data=json.dumps(info)) 
  except:
    send_status="door status url connection error"+"\n"
    print send_status
    logwriter(send_status)
    pass
   
def smswriter(mesage):
  try:
    a = '"'
    b = '"'

    ser0.open()
    ser0.write("AT+CMGS="+a+n1+b+"\r")
    time.sleep(2)
    ser0.write(mesage+chr(26))
    time.sleep(2)
    ser0.close()
    sms_log_mesage="(modem servis):sms send to number: "+n1+"\n"
    print sms_log_mesage
    logwriter(sms_log_mesage)
  except:
    pass
  
  mesage=mesage.replace(" ","_")
  try:
    url=sms_url+"&text="+mesage
    urllib2.urlopen(url,context=ssl._create_unverified_context(),timeout=5)
    sms_log_mesage="(post servis):sms send to number: "+n1+"\n"
    print sms_log_mesage
    logwriter(sms_log_mesage)
  except:
    sms_log_mesage="(post servis):sms url connection error"+"\n"
    print sms_log_mesage
    logwriter(sms_log_mesage)
    pass

def logwriter(mesage):
  mesagetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  mesage=mesagetime+" "+mesage

  file=open("door.log","a")
  file.write(mesage)
  file.close()

def gerkon_1():
  msg = 0  #mesage counter
  odc = 0  #open door counter
  odc1 = 0 #open door counter time for log
  dca = 0  #door clouse after sms counter

  data = "1111111111"  

  ser1 = serial.Serial(
      port = prt,
      baudrate = int(brate),
      timeout = 0.1
  ) 
  ser1.close()

  while True:
    ser1.open()
    ser1.write(data)
    time.sleep(0.1)
    readerdata = ser1.read(10)
    ser1.close()

    if readerdata == str(data) and msg != 1 :
      mesage = door_id+" door close"+"\n"
      print mesage
      logwriter(mesage)
      status_id = 0
      status_send(status_id,door_id_nr)
      msg = 1
      odc = 0

    elif readerdata == "" and msg != 2 : 
      mesage = door_id+" door open"+"\n"
      print mesage
      logwriter(mesage)
      status_id = 1
      status_send(status_id,door_id_nr)
      msg = 2
    else:
      pass

    if msg == 2:
      odc = odc + 1
      odc1 = odc
      print odc  #time from open door
    elif msg == 1 and dca == 1:
      mesage = door_id+" door close after "+str(odc1)+" sec"+"\n"
      logwriter(mesage)
      smswriter(mesage)
      dca = 0
      odc1 = 0
    else:
      pass

    if odc == int(odt):
      mesage = door_id+" door open for "+str(odc)+" sec"+"\n"
      logwriter(mesage)
      smswriter(mesage)
      dca = 1  
    else:
      pass
   
    time.sleep(1)

logwriter(mesage)
mesage="gerkon service started"+"\n"
print mesage
logwriter(mesage)
gerkon_1()

#end


