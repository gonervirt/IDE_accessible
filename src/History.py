class History:
 
    # default constructor
    def __init__(self):
        self.current =[]
        self.current_index = 0
        self.history = [[],self.current]
        self.history_index = 1
        print('History  history')
 
    # a method to add a char
    def char(self,character):
        print(f'char -  index={self.history_index}  value={self.history[self.history_index]}') 
        if character == 13:
            return
        self.current.append(character)
        self.current_index += 1
        
        
    def enter(self):
        current_com=self.history[self.history_index]
        if len(self.current) > 1:
            self.current =[]
            self.current_index = 0
            self.history.append(self.current)
        self.history_index = len (self.history)-1
        print(f'History  enter --> {current_com}')
        return current_com

    
    def up(self,dialog):
        print('History  up')
        #remove_current = ['-']*len(self.current)
        #nb_char=len(self.current)
        self.remove_char( dialog, len(self.history[self.history_index]))
        if self.history_index > 0:
            self.history_index -= 1
        print(f'up - index={self.history_index}  value={self.history[self.history_index]}')    
        #return str([b'0x2d']*nb_char+self.history[self.history_index])
        return self.history[self.history_index]
    
    def down(self, dialog):
        print('History  down')
        #remove_current = ['-']*len(self.current)
        #nb_char=len(self.current)
        self.remove_char( dialog, len(self.history[self.history_index]))
        if self.history_index < (len(self.history)-1):
                self.history_index += 1
        print(f'up - index={self.history_index}  value={self.history[self.history_index]}')
        #return  str([b'0x2d']*nb_char+self.history[self.history_index])
        return self.history[self.history_index]
    
    def removechar(self):
        self.history.pop()
    
    def remove_char(self, dialog, nb):
        print (f'--------- removing char {nb}   ----')
        #for i in range(0, nb):
        #    dialog.serial.write(b'\x08')
        #dialog.serial.flush()
        for i in range(0, nb):
            dialog.shell.remove_char()
        return
