import os, time, sys

class ram():
	
	def __init__(self):
		self.datastorage = {}
		self.aktuell = {}
	def insert(self,array):
		
		for x in array:
			if x != 'room':
				if array['room'] not in self.aktuell:
					self.aktuell[array['room']] = {}
				self.aktuell[array['room']][x] = array[x]
				
				
	
	def call_now(self,room,val):
		if room in self.aktuell:
			if val in self.aktuell[room]:
				#print ('true')
				return (self.aktuell[room][val])
			else:
				return ('empty')
		else:
			return ('empty')



#le = ram()

#le.insert({'room':'here','temp':20,'lux':10})

#print (le.call_now('here','temp'))
#print (le.call_now('here','lux'))
#print (le.call_now('here','temps'))