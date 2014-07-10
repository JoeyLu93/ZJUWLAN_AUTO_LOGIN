# -*- coding:utf-8 -*-
import hashlib
import urllib
from urllib2 import Request, urlopen, URLError, HTTPError
from time import sleep
import subprocess
import urllib

testWebsite = 'http://www.baidu.com'
wlanName = 'ZJUWLAN'

username = 'yourusername' 
password = 'yourpassword'



exit = False
passwordIncorrectTime = 0

def isConnectedToInternet(url):
	req = Request(url)
	try:
		response = urlopen(req, timeout = 10)
		code = response.getcode()
		content = response.read()
	except URLError, e:
		if hasattr(e, 'reason'):
			info = '[Error] Failed to reach the server.\nReason: ' + str(e.reason)

		elif hasattr(e, 'code'):
			info = '[Error] The server couldn\'t fullfill the request.\nError code: ' +str(e.code)
		else:

			info = 'Unknown URLError'
		#print info
		return False
	except Exception:
		import traceback
		#print "Generic exception: " + traceback.format_exc()
		return False
	else:
		if code == 200 and 'net.zju.edu.cn/srun_port1.php' not in content:
			return True
		else:
			return False

def isSpecifiedWlanAvaliable(name):
	p = subprocess.Popen(
		'netsh wlan show networks',
		shell = True,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE)
	stdout, stderr = p.communicate()
	if name in stdout:
		return True
	else:
		return False

def isConnectedToSpecifiedWlan(name):
	p = subprocess.Popen(
		'netsh wlan show interfaces' ,
		shell = True,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE)
	stdout, stderr = p.communicate()
	if name in stdout:
		return True
	else:
		return False

def connectTo(name):
	p = subprocess.Popen(
		'netsh wlan connect {0}' .format(name),
		shell = True,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE)
	stdout, stderr = p.communicate()
	successMsg = u'已成功完成连接请求。'
	#Since encoding rule ranges in different areas. Lenth of msg is used to justify the connection is successful
	if len(stdout) == 22 or 'Connection request was completed successfully' in stdout:
		return True
	else:
		return False 

def login(username, password):
	global passwordIncorrectTime
	global exit
	data = {'action':'login','username':username,'password':password,'ac_id':'3','type':'1','wbaredirect':'http://net.zju.edu.cn',
	'mac':'undefined','user_ip':'','is_ldap':'1','local_auth':'1'}
	data = urllib.urlencode(data)
	try:
		req = Request("https://net.zju.edu.cn/cgi-bin/srun_portal")

		response = urlopen(req,data, timeout = 10)	
		content = response.read()
		if 'help.html' in content:
			passwordIncorrectTime = 0
			return True
		else:
			if len(content) == 27:#wrong password
				print "Username or password is incorrect. Please check them again."
				print "Retry for {0} more times." .format(3 - passwordIncorrectTime)
				passwordIncorrectTime += 1
				if passwordIncorrectTime == 3:
					exit = True
			return False

	except URLError, e:
		if hasattr(e, 'reason'):
			info = '[Error] Failed to reach the server.\nReason: ' + str(e.reason)
		elif hasattr(e, 'code'):
			info = '[Error] The server couldn\'t fullfill the request.\nError code: ' +str(e.code)
		else:
			info = 'Unknown URLError'
		return False

	except Exception:
		import traceback
		print "Generic exception: " + traceback.format_exc()
		return False

def logout(username, password):
	global exit
	global passwordIncorrectTime
	data = {'action':'auto_dm','username':username,'password':password}
	data = urllib.urlencode(data)
	try:
		req = Request("https://net.zju.edu.cn/rad_online.php")

		response = urlopen(req, data, timeout = 10)
		content = response.read()
		if content == 'ok':
			passwordIncorrectTime = 0
			return True
		else:
			if len(content) == 8:#Wrong password
				print "Username or password is incorrect. Please check them again."
				print "Retry for {0} more times." .format(3 - passwordIncorrectTime)
				passwordIncorrectTime += 1
				if passwordIncorrectTime == 3:
					exit = True
			return False 

	except URLError, e:
		if hasattr(e, 'reason'):
			info = '[Error] Failed to reach the server.\nReason: ' + str(e.reason)
		elif hasattr(e, 'code'):
			info = '[Error] The server couldn\'t fullfill the request.\nError code: ' +str(e.code)
		else:
			info = 'Unknown URLError'
		return False

	except Exception:
		import traceback
		print "Generic exception: " + traceback.format_exc()
		return False

def main():
	while exit == False:
		if isConnectedToInternet(testWebsite):
			print "Connected."
			sleep(40)
			continue
		if isSpecifiedWlanAvaliable(wlanName) == False:
			print wlanName + "is not in range"
			sleep(20)
			continue
		#wlan avaliable but can not connect to internet
		if isConnectedToSpecifiedWlan(wlanName) == False:
			print "Connecting to " + wlanName
			status = connectTo(wlanName)
			if status != True:
				print status
				sleep(10)
			continue
		print "Login..."
		print "Username: " + username
		logout(username, password)
		status = login(username, password)
		
		if status != True:
			sleep(5)

if __name__ == '__main__':
	main()
