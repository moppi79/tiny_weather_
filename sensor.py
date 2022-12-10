import os, time, sys, json,datetime, struct, array, io, fcntl, daemon, random, socket, socketserver,threading
from multiprocessing import Process, Queue

#from smbus2 import SMBus

#import var
sys.path.insert(0, './module/')
from send_data import *
from bmp280 import *
from htu21 import *
from gy30 import *
from ram import *
from gpio import *
from i2c import *
from multiplex_tca9548 import *
from disp_pcf8574 import *
#from disp_new_pcf8574 import *

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



def ausfuhren (sen):
	
	#test = i2c_treiber(0x70,I2C_BUS,)
	#test.write('zero',mult)
	#test.close()

	#i2c_treiber(0x40,3) htu21

	#print (ret)
	ret = {}
	for x in sen:
		ret[x] = sen[x].call()


	return(ret)



def loop_funk ():
	I2C_SLAVE=0x0703
	I2C_BUS=3
			
	loop = 'true'
	sen_c = 0
	
	set_multiplex_channel = multiplex_tca9548(i2c_treiber(0x70,I2C_BUS,I2C_SLAVE))
	sen_arr = {}
	text = {}
	disp_arr = {}
	
	disp_arr[0] = {'name':'main','multiplex':0x02}
	disp_arr[1] = {'name':'sec','multiplex':0x04}
	disp_arr[0]['disp'] = disp_pcf8574(i2c_treiber(0x27,I2C_BUS,I2C_SLAVE),'20x4')
	disp_arr[1]['disp'] = disp_pcf8574(i2c_treiber(0x27,I2C_BUS,I2C_SLAVE),'16x2')
	
	for x in disp_arr:
		set_multiplex_channel.set_channel(disp_arr[x]['multiplex'])
		disp_arr[x]['disp'].reset()
	
	#server = server_call()
	Pace_script = 'auto'
	speicher = ram()
	
	server_io = send_data('192.168.1.35',5051)
	
	sensoren = {} #Multiplex 0x01
	sensoren[0] = bmp280('innen',i2c_treiber(0x76,I2C_BUS,I2C_SLAVE))
	sensoren[1] = htu21('innen',i2c_treiber(0x40,I2C_BUS,I2C_SLAVE))
	sensoren[2] = gy30('innen',i2c_treiber(0x23,I2C_BUS,I2C_SLAVE))
	
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
					l_o_f = 'on'
				else:
					
					l_o_f = 'off'
					
				for x in disp_arr:
					set_multiplex_channel.set_channel(disp_arr[x]['multiplex'])
					disp_arr[x]['disp'].light_onoff(l_o_f)
		
		
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
			set_multiplex_channel.set_channel(0x01)
			sen_c = 2
			
			data = ausfuhren(sensoren)
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
			disp_arr[0]['disp'].insert_text(text)
			time_display = (timer_get(5))
			#dis_test.set_text(text_put())
		time_txt = ''+time.strftime('%d.%m %H:%M:%S')
		disp_arr[0]['disp'].insert_text({4:time_txt})
		disp_arr[1]['disp'].insert_text({1:time_txt})

		for x in disp_arr:
			set_multiplex_channel.set_channel(disp_arr[x]['multiplex'])
			disp_arr[x]['disp'].set_text()
		
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
			
			text1= {}
			text1[1] = '<<<< ENDE >>>>'
			text1[2] = '<<< Bye bye >>>'

			
			disp_arr[0]['disp'].insert_text(text)
			disp_arr[1]['disp'].insert_text(text1)
			
			
			#set_multiplex_channel.set_channel(0x02)	
			#dis_test.set_text(text)
			for x in disp_arr:
				set_multiplex_channel.set_channel(disp_arr[x]['multiplex'])
				disp_arr[x]['disp'].set_text()
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
