#!/usr/bin/python
from poloniex import Poloniex
from bittrex import bittrex
from binance.enums import *
from binance.client import Client
from time import sleep
import Tkinter as tk
import threading
import math
import datetime
import json
import string

"""
Arbitrage bot for Poloniex, Bittrex and Binance
Built for Python 2.7

Requirements:
Download https://github.com/ndri/python-bittrex to folder
pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.6.zip
pip install python-binance
apt-get install python-tk
"""

class CursorAnimation(threading.Thread):
	def __init__(self, timeframe):
		self.flag = True
		self.timeframe = timeframe
		threading.Thread.__init__(self)

	def run(self):
		timer = self.timeframe
		while self.flag:
			print "[Time Left: " + str(math.ceil(timer)) + " sec]",
			print "\r",
			sleep(0.01)
			timer -= 0.01

	def stop(self):
		self.flag = False

def alert(message):	
	root = tk.Tk()
	root.title("Arbitrage Opportunity!")
	label = tk.Label(root, text="Check this " + str(message))
	label.pack(side="top", fill="both", expand=True, padx=20, pady=20)
	button = tk.Button(root, text="OK", command=lambda: root.destroy())
	button.pack(side="bottom", fill="none", expand=True)
	root.mainloop()
	

def detect_difference(diff, timeframe):
	spin = CursorAnimation(timeframe)
	spin.start()
	alert_list = []
	polo = Poloniex()
	btrx = bittrex('key', 'secret')
	bince = Client('key', 'secret')

	polotick = polo.returnTicker()
	btrxtick = btrx.getmarketsummaries() #use bittrex for a list of all coins coz it has the most
	bintick = bince.get_all_tickers()

	for pmarket,v1 in polotick.iteritems():
		plast = float(v1['last'])
		for bit in btrxtick:
			bitmarket = normalize_market_name(bit['MarketName'])
			bitlast = float(bit['Last'])
			if (pmarket == bitmarket):
				if ((abs(plast - bitlast) / bitlast) >= diff):
					alert(str('Poloniex/Bittrex: ' + pmarket))

		for bince in bintick:
			binmarket = normalize_market_name(bince['symbol'])
			binlast = float(bince['price'])			
			if (pmarket == binmarket):
				if ((abs(plast - binlast) / binlast) >= diff):
					alert(str('Poloniex/Binance: ' + pmarket))

	sleep(timeframe)

	if (len(alert_list) > 0):
		alert(alert_list)
		print "----------------------------------------------------------------------------------------------------"
		print "[" + str(datetime.datetime.now()) + "] " + str(alert_list)
	
	spin.stop()

def normalize_market_name(market): #convert all market names to polo format
	if '-' in market: #Bittrex format
		return string.replace(market, '-', '_')
	if '-' not in market: #Binance format
		if len(market) == 7:
			return market[3:] + '_' + market[:4]
		else:
			return market[3:] + '_' + market[:3]


if __name__ == "__main__":
	diff = 0.05
	timeframe = 1 * 60 #minutes
	
	try:
		print "[+] Starting Arbitrage Scanner..."	
		print "[+] Time frame: " + str(timeframe / 60) + " min"
		print "[+] Drop: " + str(diff * 100) + "%"	
		while(True):
			detect_difference(diff, timeframe)
	except Exception, e:
		print "[-] Error: " + str(e.message)
