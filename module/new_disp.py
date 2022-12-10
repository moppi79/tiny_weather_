import os, time, sys, json,datetime, struct, array, io, fcntl, daemon
#from smbus2 import SMBus

import var

I2C_SLAVE=0x0703

class i2c_treiber():
	
	def __init__ (self, adresse,bus):#adresse vom Slave baustein // REchte für /dev/i2c-x muss 666 sein 
		#bus = int(3) #bus selekt
		path = "/dev/i2c-%d" % (bus,) #pfad vom controller
		print(path)
		self.wr = io.open(path, "wb", buffering=0)#zuschreibender io
		self.rd = io.open(path, "rb", buffering=0)#lesender io
		fcntl.ioctl(self.wr, I2C_SLAVE, adresse)#Bus verbindung herstelen
		fcntl.ioctl(self.rd, I2C_SLAVE, adresse)#Bus verbindung herstellen
	
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
		
	def readswitch (self):#lesen Slave, slave register
	
		try:
			ausgabe = self.rd.read(3)#rück gabe aus dem bus
		except :
			print('Fehler in i2c_treiber/readswitch')
			return [0,99]
		else:
			return array.array('B', ausgabe) #rücke als array
		
	def close(self):
		
		self.wr.close()
		self.rd.close
		

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00
# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00
# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00
# flags for backlight control
'''
LCD_BACKLIGHT = 0x08
Achtung, hab das backlight standartmässig deaktiverit
damit es auch beim refresh dunkel bleibt
'''
LCD_BACKLIGHT = 0x00
LCD_NOBACKLIGHT = 0x00
En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class display():
    
	def __init__(self):
		self.lineadress = {1:0x80,2:0xC0,3:0x94,4:0xD4}
		self.adress = 0x27
		self.IC = 3
		self.disp_val = {1:'',2:'',3:'',4:''}
		self.light = 0x00
		self.max_char = 20
		
	def i2c_con(self,on_off=0):
		if on_off == 1:
			self.i2c = i2c_treiber(self.adress,self.IC)
		else:
			self.i2c.close()
	
	def light_onoff(self,value):
    
		if value == 'on':
			self.light = 0x08
		else:
			self.light = 0x00
	    
		self.i2c_con(1)
		#self.reset()
		self.i2c.write('zero',self.light)
		self.i2c_con()

	def call(self,value): 
		#print (self.here)
		send_chars = []
		char_c = 0
		char_c_disp = 0
		line_c = 0
		for x in value:
			#print (hex(c))
			#print(b[c])
			for y in value[x]:
				if line_c != x:
					line_c = x
					char_c = 0
					char_c_disp  = self.lineadress[x]
	               
				if len(self.disp_val[x]) > char_c :
					print('vorhanden',len(self.disp_val[x]),self.disp_val[x])
					if self.disp_val[x][char_c] != y:
						send_chars.append({'value':y,'line':char_c_disp})
				else:
					send_chars.append({'value':y,'line':char_c_disp})
				print (line_c,char_c_disp,y)
				char_c = char_c + 1
				char_c_disp = char_c_disp + 1
	           
				if len(self.disp_val[x]) > char_c:
	               
					while len(self.disp_val[x]) > char_c: #Alte nicht mehr benötige zeichen löschen
						send_chars.append({'value':' ','line':char_c_disp})
						char_c = char_c + 1
						char_c_disp = char_c_disp + 1
			self.disp_val[x] = value[x]
		print(send_chars)
		self.set_char(send_chars)
		
    
    	
	def set_text (self,text):
		#print ('jo')
		lineadress = {1:0x80,2:0xC0,3:0x94,4:0xD4}
		self.i2c = i2c_treiber(0x27,3)
		self.reset()
		self.i2c.write('zero',self.light)
		self.formating(0x01) ##clear Display	
		self.i2c.write('zero',self.light)
		time.sleep(.01)
		for x in text:
			print (x)
			print (text[x])
			self.textsend(text[x],lineadress[x])
        
		time.sleep(.01)
		#self.textsend('test',lineadress[2])
		time.sleep(.01)
		self.i2c.close()
		
	def reset(self):
		self.i2c_con(1)
		self.formating(0x03)
		self.formating(0x03)
		self.formating(0x03)
		self.formating(0x02)
		self.formating(0x01)
		self.formating(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
		self.formating(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
		self.formating(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
		self.i2c_con(1)
    
	def textsend(self,string,line):
		#print ('string:{} line:{}'.format(string,line))
		self.formating(line)
		for char in string:
			self.formating(ord(char), Rs)
			#time.sleep(0.5)
	
	def set_char (self,charlist):
		self.i2c_con(1)
		for char in charlist:
			#print(dir(char['line']))
			#print('start')
			self.formating(char['line'])
			#print('line')
			self.formating(ord(char['value']), Rs)
		
		self.i2c_con()
	
	def formating(self, data, mode=0): #8 bit in 4 bit teilen.
		self.write(mode | (data & 0xf0)) #obere 4 bit
		self.write((mode | ((data << 4) & 0xf0))) #untere 4 bit
    
	def write(self, data):
		self.i2c.write('zero',data | self.light) # Display in bereitschaft setzen
		time.sleep(.0006)
		self.i2c.write('zero',(data | En | self.light)) #wr bit setzen daten schreiben
		time.sleep(.0010)
		self.i2c.write('zero',((data & ~En) | self.light)) #daten bestätigen
		time.sleep(0.0006)



#test1 = i2c_treiber(0x40,3)

#test1.close()

def ausfuhren ():
	
	test = i2c_treiber(0x70,3)
	test.write('zero',0x02)
	test.close()

	dis_test = display()
	dis_test.reset()
	text = {}

	text[1] = '122'
	text[2] = '2'
	text[3] = '32 s df'
	text[4] = '42  sdvsd f'

	dis_test.call(text)
	
	send_chars = []
	send_chars.append({'value':'b','line':0x90})
	send_chars.append({'value':'a','line':0x91})
	print(send_chars)
	dis_test.set_char(send_chars)
	
	x = 0
	
	while x < 10:
		if x % 2 == 0:
			dis_test.light_onoff('on')
		else:
			dis_test.light_onoff('off')
			
		text = {}

		text[1] = str(x)
		text[2] = str(x)
		text[3] = str(x)
		text[4] = str(x)

		dis_test.call(text)
		print (x)
		x = x + 1
		time.sleep(.5)

ausfuhren()


def text_put():
	a = ['auto','tanja','raphtalia','kirito','asuna','a','brum','gluekskatze','rennwagen','musik','Vogel','hund','Gernrode','Offenbach','Rei','Asuka','Milim','Misaka','zeichen','geld','Huehnerstall','Bild','katze','bücherrei','verwaltung']

	
	text = {}
	text[1] = a[random.randrange(len(a))]
	text[2] = a[random.randrange(len(a))]
	text[3] = a[random.randrange(len(a))]
	text[4] = a[random.randrange(len(a))]
	
	print(text)
	return(text)