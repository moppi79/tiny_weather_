import os, time, sys, json,datetime, struct, array, io, fcntl, daemon, random, socket, socketserver,threading
from multiprocessing import Process, Queue

#from smbus2 import SMBus

#import var
from send_data import *
from bmp280 import *
from htu21 import *
from gy30 import *
from ram import *
from gpio import *



I2C_SLAVE=0x0703
I2C_BUS=3

#Bitte in der Server_call die __init__ anpassen das der Var Server stimmt


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
			self.i2c = i2c_treiber(0x70,self.IC) #Multiplexer
			self.i2c.write('zero',0x02) #Port
			self.i2c.close()
			self.i2c = i2c_treiber(self.adress,self.IC)
			self.i2c.write('zero',0x01)
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

	def set_text(self,value): #text daten setzen
		#print (self.disp_val)
		send_chars = []
		char_c = 0
		char_c_disp = 0
		line_c = 0
		for x in value: # die einzel Einträge grasen
			#print (hex(c))
			#print(b[c])
			for y in value[x]: #zeichen für zeichen durch gehen
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
			self.disp_val[x] = value[x]
		#print(send_chars)
		self.set_char(send_chars) # an I2C schnitt stelle senden

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



###################### Hilfs Funktionen #####################

def get_time ():
	ret = {}
	
	time_str = str(time.monotonic()).split('.')
	ret['akt_sec'] = int(time_str[0][len(time_str[0])-2:len(time_str[0])])
	ret['akt_ms'] = int(time_str[1][0:3])
	ret['wait'] = (1000 - ret['akt_ms'])/1000
	
	return(ret)

def timer_get (sec):
	
	time_str = str(time.monotonic()).split('.')
	aktuelle_sec = int(time_str[0][len(time_str[0])-2:len(time_str[0])])
	ret = aktuelle_sec + sec
	
	if len(str(ret)) == 3:
		ret = ret - 100
	
	return(int(ret)) 
	

def print_var(name,var):
	print('####'+name+'####')
	print('####'+var+'####')
	print('####'+name+'####')

###################### Hilfs Funktionen #####################



def ausfuhren (sen,mult):
	
	test = i2c_treiber(0x70,I2C_BUS)
	test.write('zero',mult)
	test.close()

	#i2c_treiber(0x40,3) htu21

	#print (ret)
	ret = {}
	for x in sen:
		ret[x] = sen[x].call()


	return(ret)



def loop_funk ():
		
	loop = 'true'
	sen_c = 0
	dis_test = display()
	dis_test.reset()
	
	sen_arr = {}
	text = {}

	#server = server_call()
	Pace_script = 'auto'
	speicher = ram()
	
	server_io = send_data('192.168.1.35',5051)
	
	sensoren = {} #Multiplex 0x01
	sensoren[0] = bmp280('innen',i2c_treiber(0x76,I2C_BUS))
	sensoren[1] = htu21('innen',i2c_treiber(0x40,I2C_BUS))
	sensoren[2] = gy30('innen',i2c_treiber(0x23,I2C_BUS))
	
	gp_list = gpio_io()
	
	gp_list.install(26,'out')
	gp_list.install(21,'in')
	gp_list.install(19,'in')
	
	
	time_sensor = (timer_get(1))
	
	time_display = (timer_get(3))
	
	on_blink = (timer_get(4))
	ms_int_timer_blink = False
	while loop == 'true':
		time_now = get_time()
		#print (aktuelle_sec)
		#LCD_BACKLIGHT = 0x08
		LCD_BACKLIGHT = 0x00
		#print_var('on_blink',str(on_blink))
		
		gp_new = gp_list.get()
		
		if gp_new != 'empty':
			print_var('on_blink','')
			print(gp_new)
			print('############')
			if 19 in gp_new:
				if gp_new[19] == 1:
					dis_test.light_onoff('on')
				else:
					dis_test.light_onoff('off')
		
		
		if on_blink == time_now['akt_sec']:
			print('here BLINK !!!!')
			now_ms_blink = get_time()
			print (on_blink)
			print (get_time())
			print (ms_int_timer_blink)
			print (now_ms_blink)
			Pace_script = 0.1
			if ms_int_timer_blink == False:
				print('here BLINK 222 !!!!')
				
				ms_int_timer_blink = now_ms_blink['akt_ms'] 
				print (ms_int_timer_blink)
				gp_list.update([26],[1])
				
			else:
				print('wait')
				if (ms_int_timer_blink + 100) < now_ms_blink['akt_ms']:
					print ('stop')
					test = 0
					Pace_script = 'auto'
					ms_int_timer_blink = False
					on_blink = (timer_get(5))
					gp_list.update([26],[0])
		
		print('yes')
		#loop='false'
		opfile = open('on_off.txt','r')

		a = opfile.read()
		print(a)

#####################################
		print (type(time_sensor))
		print (type(time_now['akt_sec']))
		if time_sensor == time_now['akt_sec']:
			
			sen_c = 2
			
			data = ausfuhren(sensoren,0x01)
			print (data)
			for u in data:
				speicher.insert(data[u])
				#data[u]['insert'] = '' 
				#print(data[u])
				server_io.update(data[u])
			time_sensor = (timer_get(5))
		
		if time_display == time_now['akt_sec']:	
			text[1] = 'temp:'+str(speicher.call_now('innen','temp'))+' hum:'+str(speicher.call_now('innen','hum'))
			text[2] = 'lux:'+str(speicher.call_now('innen','lux'))
			text[3] = 'HkP:'+str(speicher.call_now('innen','hkp'))
			#text[4] = ''+time.strftime('%d.%m %H:%M:%S'
			#print (speicher.call_now('innen','temp'))
			#dis_test.set_text(text)
			time_display = (timer_get(5))
			#dis_test.set_text(text_put())
			
		text[4] = ''+time.strftime('%d.%m %H:%M:%S')
		dis_test.set_text(text)
#####################################
		sen_c = sen_c - 1
		
		#######Timer #######
		
		if Pace_script == 'auto':
			time_now = get_time()
			time.sleep(time_now['wait'])
		else:
			time.sleep(Pace_script)
		#######Timer #######
		if a == '0':
			
			text[1] = '###########'
			text[2] = '#  Moppi  #'
			text[3] = '#  temp   #'
			text[4] = '###########'
				
			dis_test.set_text(text)
			gp_list.close()
			server_io.close()
			print('loop ende')
			loop='false'



valuein = sys.argv[1]

if valuein == "start":
	
	print ('start')
	opfile = open('on_off.txt','w')
	opfile.write('1')
	opfile.close()

	context = daemon.DaemonContext(
	working_directory='/net/python',
	umask=0o002)

	with context:
		loop_funk()


if valuein == "stop":
	opfile = open('on_off.txt','w')
	opfile.write('0')
	opfile.close()

if valuein == "loop":
	loop_funk()
	
if valuein == "text":
	text_put()
	







################################################################################



#lcd = lcddriver.lcd()

#lcd.lcd_clear()
#'''
#lcd.lcd_backlight("off")
#'''
#ausgebe = strftime("%H:%M     %d.%m.%Y", localtime())

#lcd.lcd_display_string(ausgebe, 1)
#lcd.lcd_display_string("Innen|Aussen|hPa", 2)
#lcd.lcd_display_string(innen_temp+'C|'+aussen_temp+'C| '+druck+'', 3)
#lcd.lcd_display_string(innen_feucht+'%|'+aussen_feucht+'%', 4)
