import os, time, sys ,re, numpy

#sys.path.insert(0, './module/')

#from ram import *

class menue_disp ():
	
	def __init__ (self,ram,zeilen,button=''):
		
		print ('init')
		self.speicher = ram
		self.zeilen = zeilen #4
		self.rotate_disp = {}
		self.rotate_num = 0
		self.rotate_mod = 'auto'
		self.button = button #select,ok,light
		self.menue_arr = {'akt':0,'lala':'0','item_sel':0,'info_Count':0}
		self.button_reg = {}
		for x in button:
			print (x)
			self.button_reg[x] = '0'

	def button (dic):
		
		print ('button')

	def info_add(self,dic):
		nu = 1 + len(self.rotate_disp)
		self.rotate_disp[nu] = dic
		self.rotate_num = 1
		self.menue_arr['info_Count'] += 1
	
	def info_rotate(self):
		
		if len(self.rotate_disp) !=0 and self.rotate_mod == 'auto':
			#print (self.rotate_disp[self.rotate_num])
			
			self.rotate_num += 1
			if len(self.rotate_disp) < self.rotate_num:
				self.rotate_num = 1
		else:
			a = 1
			#Später erweitern das er vll. zurück fällt auf auto nach x Sec Minuten
	
	def disp_refresh (self):
		#print (self.button)
		#print (self.speicher.call_now('gpio',self.button['select']))
		if self.button != '':
			if self.speicher.call_now('gpio',self.button['select']) == '1' and self.menue_arr['akt'] == 0:
				self.menue_arr['akt'] = 1
				self.button_reg['select'] = 1
			
		if self.menue_arr['akt'] == 0:
			return (self.info_update())
		else:
			
			return (self.menue_show())
	
	def info_update(self):
		disp_in = {}
		if self.rotate_num != 0:
			for x in self.rotate_disp[self.rotate_num]: 
				if isinstance(x, int):
					disp_in[x] = ''
					c = re.split("({[a-z]*:[a-z0-9]*})", self.rotate_disp[self.rotate_num][x])
					for t in c:
						k = len(t)
						if k > 0:
							if t[0] == '{' and t[(k-1)] == '}':
								new = t.replace('{','')
								new = new.replace('}','')
								
								spl_funk = new.split(':')
								
								if spl_funk[0] == 'uhr':
									disp_in[x] += time.strftime('%d.%m %H:%M:%S')
								else:
									disp_in[x] += self.speicher.call_now(spl_funk[0],spl_funk[1])
								
							else:
								disp_in[x] += t
								
			
		else:
			disp_in = {1:'no Menue'}
		return (disp_in)
		
	def menue_show(self):
		#return('hahah')
		#print (self.button_reg)
		for x in self.button:
			gp = self.speicher.call_now('gpio',self.button[x])
			if x == 'select':
				if gp == '1' and gp != self.button_reg[x]:
					#print ('next')
					self.menue_arr['item_sel'] += 1
					if len(self.rotate_disp) < self.menue_arr['item_sel']:
						self.menue_arr['item_sel'] = 0
					
					
				#if 
			if x == 'ok':
				#print('ok')
				if gp == '1' and gp != self.button_reg[x]:
					if self.menue_arr['item_sel'] == 0:
						self.rotate_num = 1
						self.rotate_mod = 'auto'
					else:
						self.rotate_num = self.menue_arr['item_sel']
						self.rotate_mod = 'non_auto'
					self.menue_arr['akt'] = 0
					ret = self.info_update()
					return(ret)
			
			if x == 'light':
				if gp == '1' and gp != self.button_reg[x]:
					#print('up')
					if self.menue_arr['item_sel'] == 0:
						self.menue_arr['item_sel'] = len(self.rotate_disp)
					else:
						self.menue_arr['item_sel'] -= 1 
				
			self.button_reg[x] = gp 

		
		#self.menue_arr['']
		ret={1:'Menue'}
		
		uz = 2
		
		while (self.zeilen) >= uz:
					
			#print(uz)
			ret[uz] = ''
			uz += 1
			
		#print (ret)	
		menu_item = []
		menu_item.append('Auto')
		
		max_page = int(numpy.ceil((self.menue_arr['info_Count'] + 1) / (self.zeilen - 1))) #das Plus 1 weil das Auto menü nicht mit drin ist
		for x in self.rotate_disp:
			menu_item.append(self.rotate_disp[x][1])
		#print (menu_item)
		akt_page = 1
		c = 1 #Page intern counter
		c_c = 0 #Page signal last showing page 
		c_d = 0 #Ignore all Other pages
		d = 0 #Item Counter
		Page_add = "("+str(akt_page)+'/'+str(max_page)+')'
		for x in menu_item:
			c += 1
			if c > self.zeilen:
				c = 2
				akt_page += 1

				
				if c_c == 1:
					c_d = 1
				else:
					uz = 2
			
					while (self.zeilen) >= uz:
								
						#print(uz)
						ret[uz] = ''
						uz += 1
				
			
			if c_d == 0:
				Page_add = "("+str(akt_page)+'/'+str(max_page)+')'
				if d == self.menue_arr['item_sel']:
					ret[c] = '> '+x
					c_c = 1
				else:
					ret[c] = '  '+x
				
			d += 1
		
		ret[1] = ret[1] + ' ' +Page_add
		#print (ret)
		return(ret)
	
'''
speicher = ram()

speicher.insert({'room':'dach','temp':'20,12'})
speicher.insert({'room':'dach','hum':'56,1'})
speicher.insert({'room':'dach','hkp':'1023'})

speicher.insert({'room':'keller','temp':'12,12'})
speicher.insert({'room':'keller','hum':'89,1'})
speicher.insert({'room':'keller','hkp':'1011'})


speicher.insert({'room':'gpio','19':'0'})
speicher.insert({'room':'gpio','20':'0'})
speicher.insert({'room':'gpio','21':'0'})

speicher.insert({'room':'system','pace_script':'auto'})
speicher.insert({'room':'system','disp_write':'0'})

but = {'select':'19','ok':'20','light':'21'}

menue1 = menue_disp(speicher,4,but)
	

print(speicher.call_now('system','disp_write'))

men1 = {}
men1[1] = 'dach geschoss'
men1[2] = 'temp: {gpio:21} hum: {dach:hum}'
men1[3] = 'hkp: {dach:hkp}'
men1[4] = '{uhr:hhmmss}'
menue1.info_add(men1)

men1 = {}
men1[1] = 'keller geschoss'
men1[2] = 'temp: {keller:temp} hum: {keller:hum}'
men1[3] = 'hkp: {keller:hkp}'
men1[4] = '{uhr:nan}'
menue1.info_add(men1)

men1 = {}
men1[1] = 't1'
men1[2] = ''
men1[3] = ''
men1[4] = ''
#menue1.info_add(men1)

men1 = {}
men1[1] = 't2'
men1[2] = ''
men1[3] = ''
men1[4] = ''
#menue1.info_add(men1)

men1 = {}
men1[1] = 't3'
men1[2] = ''
men1[3] = ''
men1[4] = ''
#menue1.info_add(men1)

men1 = {}
men1[1] = 't4'
men1[2] = ''
men1[3] = ''
men1[4] = ''
#menue1.info_add(men1)

men1 = {}
men1[1] = 't5'
men1[2] = ''
men1[3] = ''
men1[4] = ''
#menue1.info_add(men1)

men1 = {}
men1[1] = 't6'
men1[2] = ''
men1[3] = ''
men1[4] = ''
#menue1.info_add(men1)


c = 0
#speicher.insert({'room':'gpio','19':'1'})
#but = {'select':'19','ok':'20','light':'21'}

while c < 10:
	menue1.info_rotate()
	print (menue1.disp_refresh())
	
	
	if c == 10:
		speicher.insert({'room':'gpio','19':'1'})
	
	if c == 1:
		speicher.insert({'room':'gpio','19':'0'})
	if c == 2:
		speicher.insert({'room':'gpio','19':'1'})
	if c == 3:
		speicher.insert({'room':'gpio','19':'0'})
	if c == 4:
		speicher.insert({'room':'gpio','20':'1'})
	if c == 5:
		speicher.insert({'room':'gpio','20':'0'})
	if c == 6:
		speicher.insert({'room':'gpio','020':'1'})
	if c == 7:
		speicher.insert({'room':'gpio','020':'1'})
	if c == 8:
		speicher.insert({'room':'gpio','020':'1'})
	if c == 9:
		speicher.insert({'room':'gpio','020':'1'})

	if c % 2 == 0:
		speicher.insert({'room':'gpio','21':'1'})
	else:
		speicher.insert({'room':'gpio','21':'0'})
		#speicher.insert({'room':'gpio','19':'0'})
	c += 1

'''