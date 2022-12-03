import os, time, sys
class gy30():

	def __init__(self,name,con):
		self.name = name
		self.clas_con = con
	
	def call (self):
		
		self.clas_con.write('zero',0x10)

		lux = self.clas_con.readswitch(2)

		lu1 = str(round((lux[1]+ (256*lux[0]))/1.4,1))
		
		print (lu1)
		return({'lux':lu1,'room':self.name})