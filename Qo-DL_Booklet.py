#!/usr/bin/env python3

# standard:
import os
import re
import sys
import json
import time
import platform

# third party:
import requests
from pySmartDL import SmartDL

def getOs():
	osPlatform = platform.system()
	if osPlatform == 'Windows':
		return True
	else:
		return False

def osCommands(x):
	if x == "p":
		if getOs():
			os.system('pause')
		else:
			os.system("read -rsp $\"\"")
	elif x == "c":
		if getOs():
			os.system('cls')
		else:
			os.system("clear")
	else:
		if getOs():
			os.system('title Qo Booklet-DL R1 (by Sorrow446)')
		else:
			sys.stdout.write('\x1b]2;Qo Booklet-DL R1 (by Sorrow446)\x07')
		
def apiCall(albumId, appId, cur, total):
	metaGetReq = requests.get('https://www.qobuz.com/api.json/0.2/album/get?',
		params={
			"app_id": appId,
			"album_id": albumId
		}
	)
	if metaGetReq.status_code == 400:
		print("Bad App ID. Fetching a new one...\n")
		fetchAppId()
		return
	elif metaGetReq.status_code == 200:
		metaGetReqJ = json.loads(metaGetReq.text)
		try:
			if metaGetReqJ['goodies'][0]['file_format_id'] == 21:
				print(f"Downloading booklet {cur} of {total}: {metaGetReqJ['goodies'][0]['description']}")
				fetchBooklet(metaGetReqJ['goodies'][0]['url'], stripFname(f"{metaGetReqJ['goodies'][0]['description']} [{metaGetReqJ['goodies'][0]['id']}]"))
			else:
				print("Album has no booklet.\n")
				return
		except KeyError:
			print("Album has no booklet.\n")
			return
	else:
		print(f"Failed to fetch album metadata. Response from API: {response.text}")
	
def fetchBooklet(url, finalFname):
	SmartDL(url, f'{os.path.dirname(sys.argv[0])}/Qo-DL Booklet Downloads/{finalFname}', threads=1).start()

def fetchAppId():
	bundleUrlMatch = re.search(r'<script src="(/resources/\d+\.\d+\.\d+-[a-z]\d{3}/bundle\.js)"></script>', requests.get("https://play.qobuz.com/login").text)
	bundle = requests.get(f"https://play.qobuz.com{bundleUrlMatch.group(1)}").text
	idSecretMatch = re.search(r'{app_id:"(?P<app_id>\d{9})",app_secret:"(?P<secret>\w{32})",base_port:"80",base_url:"https://www\.qobuz\.com",base_method:"/api\.json/0\.2/"},n\.base_url="https://play\.qobuz\.com"', bundle)			
	with open('config.json', 'w') as f:
		json.dump({"appId": idSecretMatch.group("app_id")}, f, indent=4)
	print("Wrote new app ID to config file.\n")

def readConfig():
	with open("config.json") as f:
		return json.load(f)

def dirSetup():
	if not os.path.isdir('Qo-DL Booklet Downloads'):
		os.mkdir('Qo-DL Booklet Downloads')

def stripFname(fname):
	if getOs():
		fname = re.sub(r'[\\/:*?"><|]', '-', fname)
	else:
		fname = re.sub('/', '-', fname)
	return f"{fname}.pdf"
		
def main():
	try:
		txtFname = sys.argv[1]
		if not txtFname.endswith('.txt'):
			return
		total = 0
		cur = 0
		with open(txtFname) as f:
			for line in f:
				total += 1
		with open(txtFname) as f:
			for line in f:
				url = line.strip()
				try:
					if len(url.split('/')[-1]) != 13:
						print("Invalid URL.")
					else:
						cur += 1
						dirSetup()
						apiCall(url.split('/')[-1], readConfig()['appId'], cur, total)
				except IndexError:
					print("Invalid URL.")
		sys.argv.pop(1)
		print("Returning to URL input screen...")
		time.sleep(1)
		osCommands('c')
		return
	except IndexError:
		url = input("Input Qobuz Player or Qobuz store URL:").split('/')[-1]
	try:
		if not url.strip():
			osCommands('c')
			return
		elif len(url.split('/')[-1]) != 13:
			print("Invalid URL.")
			time.sleep(1)
			osCommands('c')
		else:
			osCommands('c')
			dirSetup()
			apiCall(url.split('/')[-1], readConfig()['appId'], 1, 1)
			print("Returning to URL input screen...")
			time.sleep(1)
			osCommands('c')
	except IndexError:
		print("Invalid URL.")
		time.sleep(1)
		osCommands('c')

if __name__ == '__main__':
	osCommands('t')
	if not readConfig()['appId']:
		fetchAppId()
	while True:
		main()