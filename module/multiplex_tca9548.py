class multiplex_tca9548 ():
	def __init__(self,i2c_drive):
		self.clas_con = i2c_drive
	
	def set_channel(self,channel):
		self.clas_con.write('zero',channel) #Port
		