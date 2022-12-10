import os, sys,io,fcntl, array
class i2c_treiber():
	
	def __init__ (self, adresse,bus,i2c_slave):#adresse vom Slave baustein // REchte für /dev/i2c-x muss 666 sein 
		#bus = int(3) #bus selekt
		path = "/dev/i2c-%d" % (bus,) #pfad vom controller
		print(path)
		self.wr = io.open(path, "wb", buffering=0)#zuschreibender io
		self.rd = io.open(path, "rb", buffering=0)#lesender io
		fcntl.ioctl(self.wr, i2c_slave, adresse)#Bus verbindung herstelen
		fcntl.ioctl(self.rd, i2c_slave, adresse)#Bus verbindung herstellen
	
	def write (self, bank, werte): #schreiben Slave, Slave Register, Zu seztender wert 'zero' wert bei sensoren die ohne bank ansprechbar sind.
		if bank == 'zero':
			#ausgabe = bytearray([werte])
			#test = werte.to_bytes(1,byteorder='big')
			#print ('unformatiert: {} sollwert: {} ist wert: {} anderes: {} test {}'.format(werte,hex(ausgabe[0]),bin(werte),bytearray([werte]),test))
			#print (bytearray([werte]))
			#self.wr.write(bytearray([werte]))
			try:
				self.wr.write(bytearray([werte]))#in bus schreiben
			except :
				print('Fehler in i2c_treiber/write')
				#print('aa')
			
		else:
			try:
				self.wr.write(bytearray([bank,werte]))#in bus schreiben
			except :
				print('Fehler in i2c_treiber/write')
	
	def read (self, bank):#lesen Slave, slave register
		self.wr.write(bytearray([bank]))#in den bus schreiben
		try:
			ausgabe = self.rd.read(2)#rück gabe aus dem bus
		except:
			print('Fehler in i2c_treiber/read')
		else:	
			return array.array('B', ausgabe) #rücke als array
		
	def readswitch (self,offset):#lesen Slave, slave register
	
		try:
			ausgabe = self.rd.read(offset)#rück gabe aus dem bus
		except :
			print('Fehler in i2c_treiber/readswitch')
			return [0,99]
		else:
			return array.array('B', ausgabe) #rücke als array
		
	def close(self):
		
		self.wr.close()
		self.rd.close
		
