import os, time, sys
class htu21():

	def __init__(self,name,con):
		self.name = name
		self.clas_con = con
	
	def call (self):
			
		self.clas_con.write('zero',0xe3)
	
		temp = self.clas_con.readswitch(3)
	
		self.clas_con.write('zero',0xe5)
	
		hum = self.clas_con.readswitch(3)
	
	
		temp2 = float((temp[0] * 256) - temp[1])
	
		temp_return = str(round((-46.85 + (175.72 * (temp2 / 65536.0))),1)) 
	
		hum2 = float((hum[0] * 256) - hum[1])#daten in 16bit umwandeln
	
		hum_return = str(round((-6.0 + (125.0 * (hum2 / 65536.0))),1))#ausgabe umrechnen
	
	
		ret = {'temp':temp_return,'hum':hum_return,'room':self.name}
		
		print (ret)
		
		return(ret)