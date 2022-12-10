import os, time, sys
class disp_pcf8574():
    
	def __init__(self,i2c_drive,disp_type):
		
		self.i2c_con= i2c_drive
		
		if disp_type == '20x4':
			self.lineadress = {1:0x80,2:0xC0,3:0x94,4:0xD4}
			self.disp_val = {1:'',2:'',3:'',4:''}
			self.new_disp_val = {1:'',2:'',3:'',4:''} #new
		else:
			self.lineadress = {1:0x80,2:0xC0}
			self.disp_val = {1:'',2:''}
			self.new_disp_val = {1:'',2:''} #new
		self.disp_val_change = [] #new
		self.light = 0x00
		self.max_char = 20
		
		# commands
		self.LCD_CLEARDISPLAY = 0x01
		self.LCD_RETURNHOME = 0x02
		self.LCD_ENTRYMODESET = 0x04
		self.LCD_DISPLAYCONTROL = 0x08
		self.LCD_CURSORSHIFT = 0x10
		self.LCD_FUNCTIONSET = 0x20
		self.LCD_SETCGRAMADDR = 0x40
		self.LCD_SETDDRAMADDR = 0x80
		
		# flags for display entry mode
		self.LCD_ENTRYRIGHT = 0x00
		self.LCD_ENTRYLEFT = 0x02
		self.LCD_ENTRYSHIFTINCREMENT = 0x01
		self.LCD_ENTRYSHIFTDECREMENT = 0x00
		
		# flags for display on/off control
		self.LCD_DISPLAYON = 0x04
		self.LCD_DISPLAYOFF = 0x00
		self.LCD_CURSORON = 0x02
		self.LCD_CURSOROFF = 0x00
		self.LCD_BLINKON = 0x01
		self.LCD_BLINKOFF = 0x00
		# flags for display/cursor shift
		self.LCD_DISPLAYMOVE = 0x08
		self.LCD_CURSORMOVE = 0x00
		self.LCD_MOVERIGHT = 0x04
		self.LCD_MOVELEFT = 0x00
		# flags for function set
		self.LCD_8BITMODE = 0x10
		self.LCD_4BITMODE = 0x00
		self.LCD_2LINE = 0x08
		self.LCD_1LINE = 0x00
		self.LCD_5x10DOTS = 0x04
		self.LCD_5x8DOTS = 0x00
		# flags for backlight control
		'''
		LCD_BACKLIGHT = 0x08
		Achtung, hab das backlight standartmässig deaktiverit
		damit es auch beim refresh dunkel bleibt
		'''
		self.LCD_BACKLIGHT = 0x00
		self.LCD_NOBACKLIGHT = 0x00
		self.En = 0b00000100 # Enable bit
		self.Rw = 0b00000010 # Read/Write bit
		self.Rs = 0b00000001 # Register select bit

	def light_onoff(self,value):
    
		if value == 'on':
			self.light = 0x08
		else:
			self.light = 0x00
	    
		self.i2c_con.write('zero',self.light)


	def set_text(self): #text daten setzen
		#print (self.disp_val)
		send_chars = []
		char_c = 0
		char_c_disp = 0
		line_c = 0
		for x in self.disp_val_change: # die einzel Einträge grasen
			#print (hex(c))
			#print(b[c])
			for y in self.new_disp_val[x]: #zeichen für zeichen durch gehen
				if line_c != x:
					line_c = x #counter für eingehenden Line text
					char_c = 0 #Zeichen counter eingabe
					char_c_disp  = self.lineadress[x] #Start Postion auf Display
	               
				if len(self.disp_val[x]) > char_c : # alt-zeichensatz zeile Länger als Aktueller counter
					#print('vorhanden',len(self.disp_val[x]),self.disp_val[x])
					if self.disp_val[x][char_c] != y: #ist neues Zeichen Gleich mit Alt zeichen
						send_chars.append({'value':y,'line':char_c_disp})
				else: # wenn neue Neue ZEile Länger ist als die alte
					send_chars.append({'value':y,'line':char_c_disp})
				
				#print (line_c,char_c_disp,y)
				char_c = char_c + 1 #counter zeichen hoch zählen
				char_c_disp = char_c_disp + 1 # pos Zeichen zählen
	           
			if len(self.disp_val[x]) > char_c: #wenn zeichen im Display noch vorhanden sein sollte aber gelöscht werden müssten
	               
				while len(self.disp_val[x]) > char_c: #Alte nicht mehr benötige zeichen löschen
					send_chars.append({'value':' ','line':char_c_disp})
					char_c = char_c + 1
					char_c_disp = char_c_disp + 1
			self.disp_val[x] = self.new_disp_val[x]
		#print(send_chars)
		if send_chars != []:
			self.set_char(send_chars) # an I2C schnitt stelle senden
			self.new_disp_val = {1:'',2:'',3:'',4:''} #new 
			self.disp_val_change = [] #new
			

	def reset(self):
		#self.i2c_con(1)
		self.formating(0x03)
		self.formating(0x03)
		self.formating(0x03)
		self.formating(0x02)
		self.formating(0x01)
		self.formating(self.LCD_FUNCTIONSET | self.LCD_2LINE | self.LCD_5x8DOTS | self.LCD_4BITMODE)
		self.formating(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
		self.formating(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT)
		#self.i2c_con(1)
    
	def textsend(self,string,line):
		#print ('string:{} line:{}'.format(string,line))
		self.formating(line)
		for char in string:
			self.formating(ord(char), Rs)
			#time.sleep(0.5)
	
	def set_char (self,charlist):
		#self.i2c_con(1)
		for char in charlist:
			#print(dir(char['line']))
			#print('start')
			self.formating(char['line'])
			#print('line')
			self.formating(ord(char['value']), self.Rs)
		
		#self.i2c_con()
	
	def formating(self, data, mode=0): #8 bit in 4 bit teilen.
		self.write(mode | (data & 0xf0)) #obere 4 bit
		self.write((mode | ((data << 4) & 0xf0))) #untere 4 bit
    
	def write(self, data):
		self.i2c_con.write('zero',data | self.light) # Display in bereitschaft setzen
		time.sleep(.0006)
		self.i2c_con.write('zero',(data | self.En | self.light)) #wr bit setzen daten schreiben
		time.sleep(.0010)
		self.i2c_con.write('zero',((data & ~self.En) | self.light)) #daten bestätigen
		time.sleep(0.0006)
	
	def insert_text (self,text):
		
		for x in text:
			self.new_disp_val[x] = text[x]
			if x not in self.disp_val_change:
				self.disp_val_change.append(x)
	
	def get_text (self,line='all'):
		ret = {}
		if line == 'all':
			for x in self.disp_val:
				if x in self.disp_val_change:
					ret[x] = self.new_disp_val[x]
				else:
					ret[x] = self.disp_val[x] 
		else:
			if line in self.disp_val_change:
				ret = self.new_disp_val[line]
			else:
				ret = self.disp_val[line] 
		
		
		return(ret)