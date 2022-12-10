import gpiod,time, threading
from collections import defaultdict
from multiprocessing import Process, Queue

#>>> import gpiod
#>>> help (gpiod)



class gpio_io():
	
    def __init__(self):
        self.allow_gpio = [4,17,27,22,5,6,13,19,26,18,23,24,25,12,16,20,21]
        self.pipe_in = Queue()
        self.pipe_out = Queue()
        self.thread_holder = Process(target=self.thread_walker,args=(self.pipe_out,self.pipe_in))
        self.thread_holder.start()

    def thread_walker (self,p_in,p_out):
        gp_in = []
        gp_out = []
        save = {}
        new_save = {}
        gpio_set_in = 0
        gpio_set_out = 0
        #chip = gpiod.chip('gpiochip0') ### Variable noch erstellen
        #chip1 = gpiod.chip('gpiochip0') ### Variable noch erstellen
        while True:
            time.sleep(0.1)
            
            if gpio_set_in == 1:
                #print ("yes")
                val_new = in_line.get_values()
                c = 0
                #print (val_new)
                put_in = {}
                for x in gp_in:
                    if val_new[c] != save[x]:
                        new_save[x] = val_new[c]
                        put_in[x] = val_new[c]
                    c += 1
                
                if put_in != {}:
                    while True:
                        time.sleep(0.1)
                        if p_out.empty() == True:
                            #print ('put in')
                            p_out.put(put_in)
                            save = new_save
                            break

                
            if gpio_set_out == 7:
                #print ("yes")
                in_var = out_line.get_values()
                #print (in_var)
                if in_var[0] == 1:
                    out_line.set_values([0])
                else:
                    out_line.set_values([1])
            else:
                 print ("no")
            
            
            if p_in.empty() == False:
                var = p_in.get()
                
                if var['funk'] == 'get':
                    new = 'asd'
                    p_out.put(new)
                    
                if var['funk'] == 'update':
                    #print (var)
                    
                    in_var = out_line.get_values()
                    c = 0 
                    m_c = {}
                    for x in gp_out:
                        m_c[x] = in_var[c]
                        c += 1
                    c = 0   
                    for x in var['gpio']:
                        m_c[x] = var['var'][c]
                        c += 1
                        
                    insert = []    
                    for x in gp_out:
                        insert.append(m_c[x])
                    
                    #print (insert)
                    
                    out_line.set_values(insert)
                    
                if var['funk'] == 'insert1':
                    print (var)
                    
                if var['funk'] == 'insert':
                    if var['gpio'] in self.allow_gpio:
                        if var['typ'] == 'in':
                            gp_in.append(var['gpio'])
                        else:
                            gp_out.append(var['gpio'])
                        
                        save[var['gpio']] = '0'
                        new_save[var['gpio']] = '0'
                        print (gp_in,gp_out)
                        #chip = gpiod.chip('gpiochip0')
                        if len(gp_out) != 0:
                            chip1 = gpiod.chip('gpiochip0') ### Variable noch erstellen
                            out_line = chip1.get_lines(gp_out)
                            config_out = gpiod.line_request()
                            config_out.consumer = "Out"
                            config_out.request_type = gpiod.line_request.DIRECTION_OUTPUT 
                            out_line.request(config_out)
                            gpio_set_out = 1
                        if len(gp_in) != 0:
                            chip = gpiod.chip('gpiochip0') ### Variable noch erstellen
                            print(dir(chip))
                            in_line = chip.get_lines(gp_in)
                            print(dir(in_line))
                            config_in = gpiod.line_request()
                            config_in.consumer = "Button"
                            config_in.request_type = gpiod.line_request.DIRECTION_INPUT 
                            in_line.request(config_in)
                            gpio_set_in = 1
                    
                if var['funk'] == 'end':
                    del chip
                    del chip1
                    break
    
    def install (self,gpio,typ):
        c = 0
        while True:
            
            if self.pipe_out.empty() == True:
                send = {'funk':'insert','gpio':gpio,'typ':typ}
                self.pipe_out.put(send)
                break
            else:
                time.sleep(0.1)
                #var = self.pipe_out.get()
                #print (var)
                #print('here 2')
                c += 1
                if c == 10:
                    break
            
    def update (self,gpio,var): # Ein wert oder list in beiden Variablen
        c = 0
        while True:
            
            if self.pipe_out.empty() == True:
                send = {'funk':'update','gpio':gpio,'var':var}
                self.pipe_out.put(send)
                break
            else:
                time.sleep(0.1)
                #var = self.pipe_out.get()
                #print (var)
                #print('here 2')
                c += 1
                if c == 10:
                    break
        
        
        
        
    def get (self):
        
        if self.pipe_in.empty() == False:
            #print ('data in')
            return(self.pipe_in.get())
        
        else:
            
            return('empty')
        
        
            
    def close (self):
        send = {'funk':'end'}
        self.pipe_out.put(send)
