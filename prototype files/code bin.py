import vlc
import time
import threading

x = [0,1,2,3,4,5]

con = False

def start():
    p = vlc.MediaPlayer("alarm.mp3")
    p.play()
    time.sleep(1.95)
    p.stop()
    start()

#start()


def play2():            
    try:                
        while True:                    
            p = vlc.MediaPlayer("alarm.mp3")
            p.play() 
            time.sleep(1.95)
            p.stop()                  
            if stop_thread:
                break
    except:
        print("exception")
        pass

stop_thread = False
t1 = threading.Thread(target = play2)
t1.start()


def play():            
            try:                
                while True:                    
                    p = vlc.MediaPlayer("alarm.mp3")
                    p.play() 
                    sleep(1.98)
                    p.stop()                    
                    if self.stop_thread:
                        break
            except:
                print("exception")
                pass

        self.stop_thread = False
        play()

        print("test8")
        self.data = str("On 2022/12/12 12:12:12, Responder TUPC-19-0147, DURAN ROGIE, of BET-COET, responded to LACERATION on HAND")
        print("test5")
        reply = QMessageBox.warning(self, 'Emergency Recieved',self.data,
                                     QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            print("confirm")
            try:
                self.stop_thread = True
                print("thread killed")
            except:
                print("asdasdasd")
        else:
            print("???")


self.data = str("On " + date_time + ", Responder " + r_id + " " + rname + " of " + rcourse + ", responded to " + injury + " on " + bodypart)


    def msgbox(self):
    
        print("test1")
        def play():
            print("test2")
            #self.x.join()           
            try:                
                while True:
                    print("test3")  
                                      
                    p = vlc.MediaPlayer("alarm.mp3")
                    p.play() 
                    sleep(1.98)
                    p.stop()                    
                    if self.stop_thread:
                        break
            except:
                print("exception")
                #t1.join()
                pass

        self.stop_thread = False
        t1 = threading.Thread(target = play)
        t1.start()

        
        self.data2 = str("On 2022/12/12 12:12:12, Responder TUPC-19-0147, DURAN ROGIE, of BET-COET, responded to LACERATION on HAND")
        
        self.reply = QMessageBox.warning(self, 'Emergency Received',self.data2,
                                     QMessageBox.Ok)
        if self.reply == QMessageBox.Ok:
            print("confirm")
            try:
                self.stop_thread = True
                t1.join()
                global flag
                flag = False
                print("thread killed")
            except:
                print("asdasdasd")
        else:
            print("???")