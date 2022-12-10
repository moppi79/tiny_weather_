import gpiod, time, threading,json, socket
from collections import defaultdict
from multiprocessing import Process, Queue, Event

#>>> import gpiod
#>>> help (gpiod)



class send_data():
	
	def __init__(self,host,port):
		self.HOST = host
		self.PORT = port
		self.pipe_out = {}
		c = 0
		while c < 10:
			#print ('aaaa')
			self.pipe_out[c] = Queue()
			#print (self.pipe_out[c])
			c += 1
		#print (self.pipe_out)
		self.pipe_in = Queue()
		self.event = Event()
		print (dir(self.event))
		self.thread_holder = Process(name='tcp_client_sensor',target=self.thread_walker,args=(self.pipe_out,self.pipe_in,self.event))
		self.thread_holder.start()

		

	def thread_walker (self,p_in,p_out,event):
		gp_in = []
		gp_out = []
		save = {}
		new_save = {}
		gpio_set_in = 0
		gpio_set_out = 0
		end = 0
		loop = 0
		
		#chip = gpiod.chip('gpiochip0') ### Variable noch erstellen
		#chip1 = gpiod.chip('gpiochip0') ### Variable noch erstellen
		while True:
			#time.sleep(0.1)
			e = event.wait()
			d = [0,1,2,3,4,5,6,7,8,9]
			#e = event.wait(5.1)
			print('befor')
			
			#print (e)
			print('after')
			if e:
				print ("!!!!event!!!!!")
				if loop > 3:
					event.clear()
					loop = 0
			
			loop += 1	
			for c in d:
			
				#print ('c='+str(c))
				#print (p_in)
				if p_in[c].empty() == False:
					var = p_in[c].get()
					print('channel:'+(str(c)))
					loop = 0
					#break
				else:
					var = {}
					var['funk'] = ''
				c += 1
				#var = p_in.get()
				if var['funk'] == 'get':
					print (var)
					p_out.put(self.client(var['room'],var['typ']))
					loop = 0
					
					
				if var['funk'] == 'update':
					print (var)
					self.client_send_only(var['dic'])
					loop = 0
					#time.sleep(0.2)
				if var['funk'] == 'insert1':
					print (var)
				if var['funk'] == 'insert':
					print (var)
				if var['funk'] == 'end': ## neues break warscheinlich
					end = 1
					p_out.put('end')
					break
			if end == 1:
				break
    
	def install (self,gpio,typ):
		
		b = 0
		while b < 10:
			send={}
			if self.pipe_out[b].empty() == True:
				send = {'funk':'insert','gpio':gpio,'typ':typ}
				self.pipe_out[b].put(send)
				self.event.set()
				break
			b += 1
		

	def update (self,var): # Ein wert oder list in beiden Variablen
		print('update')
		
		b = 0
		while b < 10:
			send={}
			if self.pipe_out[b].empty() == True:
				send = {'funk':'update','dic':var}
				self.pipe_out[b].put(send)
				self.event.set()
				break
			b += 1

  
	def call (self,room,typ=''):
		
		print (room,typ)
		b = 0
		while b < 10:
			send={}
			if self.pipe_out[b].empty() == True:
				send = {'funk':'get','room':room,'typ':typ}
				self.pipe_out[b].put(send)
				self.event.set()	
				break
			b += 1
		#self.event.clear()


	def call_get (self):
		#self.event.set()
		
		if self.pipe_in.empty() == False:
			print ('data in')
			return(self.pipe_in.get())
		else:
			
			return('empty')
		#self.event.clear()
	
	def close (self):
		
		print('update')
		b = 0
		self.event.set()
		while b < 10:
			send={}
			if self.pipe_out[b].empty() == True:
				send = {'funk':'end'}
				self.pipe_out[b].put(send)
				break
			b += 1
		print ('closer First')
		self.event.set()
		while True:
			time.sleep(0.2)
			if self.pipe_in.empty() == False:
				data = self.pipe_in.get()
				print (data)
				if data == 'end':
					print ('closer')
					break
				

		
		
	def client_send_only(self, in_dic):
		in_dic['insert'] = ''
		message = json.dumps(in_dic)
		print (message)
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			try:
				sock.connect((self.HOST , self.PORT))
			except :
				print ('error verbindung')

			else:
				#sock.connect((self.HOST, self.PORT))
				#### SEND DATA #####
				length = len(message)
				sock.sendall(bytes(str(length), 'utf8'))
				response = str(sock.recv(10), 'utf8')
				if response == 'ok':
					print ('ja')
			sock.sendall(bytes(message, 'utf8'))
			#### SEND DATA #####
			###Bekome data #####
			count = str(sock.recv(10).strip(), 'utf8')
			print("Received count: {}".format(count))
			sock.sendall(bytes('ok', 'utf8'))
			
			response = str(sock.recv(int(count)), 'utf8')
			print("Received count: {}".format(response))
			###Bekome data #####
			sock.shutdown(2)
			sock.close()
	
	        
	def client(self, room,typ):
		in_dic = {}
		in_dic['call'] = ''
		in_dic['room'] = room
		in_dic['val'] = typ
		message = json.dumps(in_dic)
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			try:
				sock.connect((self.HOST , self.PORT))
			except :
				print ('error verbindung')
				return('error')

			else:
				 #### SEND DATA #####
				length = len(message)
				sock.sendall(bytes(str(length), 'utf8'))
				response = str(sock.recv(10), 'utf8')
				if response == 'ok':
					print ('ja')
				sock.sendall(bytes(message, 'utf8'))
				#### SEND DATA #####
		        
				###Bekome data #####
				count = str(sock.recv(10).strip(), 'utf8')
				print("Received count: {}".format(count))
				sock.sendall(bytes('ok', 'utf8'))
		        
				response = str(sock.recv(int(count)), 'utf8')
				print("Received count: {}".format(response))
				##Bekome data #####
				sock.close()
				return(response)
	
def get_time ():
	ret = {}
	
	time_str = str(time.monotonic()).split('.')
	ret['akt_sec'] = int(time_str[0][len(time_str[0])-2:len(time_str[0])])
	ret['akt_ms'] = int(time_str[1][0:3])
	ret['wait'] = (1000 - ret['akt_ms'])/1000
	
	return(ret)	
	
	
def tester():

	t1 = get_time()
	print (t1['akt_ms'])
	print ('Start Script')
	c = 0
    
	test = send_data('192.168.1.35',5051)
	#time.sleep(2.1)
	#test.install(26,'out')
	#time.sleep(1.1)
	#test.install(21,'in')
	#time.sleep(1.1)
	#test.install(19,'in')
	a = 1
	send = {'lux':'1236','room':'Test_room'}
	print(send)
	#test.close()
	while True:
		#break
		t1 = get_time()
		print (t1['akt_ms'])
		print (c)
		print (test.call_get())

		#test.update(send)  
		#var = test.call('Test_room','lux')
		if c == 15:
			var2 = test.call('Test_room')
			a = 0
		if c == 3:
			var2 = test.update(send)
			send = {'hkp':'986','room':'Test_room'}
			var2 = test.update(send)
			send = {'temp':'12.36','room':'Test_room'}
			var2 = test.update(send)
			send = {'hmp':'24.9','room':'Test_room'}
			var2 = test.update(send)
			
			a = 0
		c += 1
		time.sleep(0.1)
		print (c)
		#break
		if c > 30:
			test.close()
			break
        
        
#tester()