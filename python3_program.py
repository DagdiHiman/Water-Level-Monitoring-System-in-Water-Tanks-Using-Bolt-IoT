import requests, time, math, json
from boltiot import Bolt
import conf2 as conf	#my Configuration File

data = [] 	#Empty list for storing sensor values...
mybolt = Bolt(conf.bolt_api_key, conf.device_id) #My Bolt
mybolt.digitalWrite(0,"LOW")

#Function:Get Sensor Value
def get_sv(pin):
	try:
		response = mybolt.analogRead(pin)
		data = json.loads(response)
		if data["success"]!=1:
			print("Rquest Failed")
			print("Response:",data)
			return -999
		sensor_value = int(data["value"])
		return sensor_value
	except Exception as e:
		print("Something went wrong")
		print(e)
		return -999

#Function:Send Telegram Message
def send_tm(message):
	url = "https://api.telegram.org/"+conf.telegram_bot_id+"/sendMessage"
	data = {
		"chat_id":conf.telegram_chat_id,
		"text":message
	}
	try:
		response=requests.request(
			"POST",
			url,
			params = data
		)
		print("This is the telegram response=>")
		print(response.text)
		telegram_data = json.loads(response.text)
		return telegram_data["ok"]
	except Exception as e:
		print("Errror Occurred in sending the alert message")
		print(e)
		return False


#MAIN:->
while True:
	sensor_value = get_sv("A0")
	print("Sensor value is = ",sensor_value)

	if sensor_value == -999:
		print("Request unsuccessful.Skipping...")
		time.sleep(10)
		continue

	if(sensor_value >= conf.threshold):
		print("Alert:Water Level exceeded the threshold value")
		message = "Alert(Type 1)!Water Level exceeded.Time to Stop filling the tank"+
			".The current sensor value is:"+str(sensor_value)
		telegram_status = send_tm(message)
		print("This is the telegram status:",telegram_status)
		mybolt.digitalwrite(0,"HIGH")
		time.sleep(60)
		mybolt.digitalWrite(0,"LOW")
	else:
		mybolt.digitalwrite(0,"LOW")

	data.append(sensor_value)
	time.sleep(10)

#END