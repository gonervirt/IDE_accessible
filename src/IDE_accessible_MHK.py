"""
    Main of the application wich contains the classes to init the app
"""

# FLB => ajout version, release et authors
__version__ = "v 2.0 beta" 
__release_date__ = "2023-06-30" 
__author__ = "My Human Kit in collaboration with Atelier partagé"

import os

# reglage du backend
os.environ["MPLBACKEND"] = "WXAgg"

import sys

import wx
import serial
import threading
import pyttsx3

from Shortcuts import InitShortcuts
from Serial_manager.firmware import FirmwareManager
from Serial_manager.connexion import ManageConnection
from menus import init_top_menu, init_toolbar
from all_panels import create_panels
from Serial_manager.receive_infos import serial_read_data, read_cmd
from Serial_manager.send_infos import Exec_cmd
from Utils.voice_synthese import my_speak


class MainWindow(wx.Frame):
    """classe MainWindow 
    
    MainWindow of the app which will contains all the children classes and
       custom functions
       
       this class contains methods :
       * __init__ : init class constructor 
       * __set_properties__ : 
       * __attach_events : 
       * exec_cmd : to execute command on connected board on a dedicated thread
       * start_thread_serial : 
       * stop_thread_serial :
       * OnKey :
       * thread_listen_port : 
       * actualize_status_bar :
       * OnUpFocus :
       * OnDownFocus : 
       * OnStatus : sets focus on status bar
       * right_click_shortcut :
       * 

    :param wx.Frame: see https://wxpython.org/Phoenix/docs/html/wx.Frame.html
    """

    def __init__(self, name, size):
        """MainWindow constructor

        :param name: name of the window
        :type name: str
        :param size: define dimensions of the window (width, height)
        :type size: tuple(int, int)
        """
        # FLB => ajout methode super 
        super().__init__()
        
        wx.Frame.__init__(self, None, 1, title=name, size=size)
        dir_icon = os.path.dirname("./img/Icone.png")
        print("DIR icon : ", dir_icon) 
        self.SetIcon(wx.Icon("./img/Icone.png"))
        
        print("Creation de la fenetre de l'application au centre de l'ecran") 
        #cree la fenetre au centre de l'ecran
        self.Centre()
        self.FromDIP(size)
        self.__set_properties__()
        
        # create panel
        print("create panel") 
        create_panels(self)
        
        # init tool bar 
        print("init tool bar") 
        init_toolbar(self)
        
        # init short cuts
        print("init short cuts") 
        InitShortcuts(self)
        self.__attach_events()

    def __set_properties__(self):
        """ Set attributs of the class instancied
        """
        self.serial = serial.Serial()
        self.serial.timeout = 0.5
        self.time_to_send = 0.1
        self.thread_serial = None
        self.alive = threading.Event()
        #####
        self.on_key = True
        self.keypressmsg = ""
        self.result = ""
        self.show_cmd = True
        self.connected = False
        self.shell_text = ""
        self.cmd_return = ""
        self.last_cmd_red = ""
        self.last_enter = False
        self.open_file = False
        self.open_file_txt = ""
        #####
        self.who_is_focus = 0
        self.theme = 'Dark Theme'
        #####
        self.top_menu = init_top_menu(self)
        self.serial_manager = ManageConnection(self)
        self.voice_on = pyttsx3.init()
        self.firmware_manager = FirmwareManager()
        self.speak_on = True
        self.speak_thread = None

    def __attach_events(self):
        """ Link events to methods
        """
        self.shell.Bind(wx.EVT_CHAR, self.OnKey)
        self.Bind(wx.EVT_CLOSE, self.top_menu.MenuFile.OnExit)

    def exec_cmd(self, cmd):
        """Execute a command on the device and get the command back
        
        command execution id performed in a dedicated Thread 

        :param cmd: command to execute
        :type cmd: str
        :return: command back
        :rtype: str
        """
        print("Exec cmd ==>", cmd)
        self.read_thread = Exec_cmd(cmd, self)
        self.read_thread.start()
        self.read_thread.join()
        read_cmd(self, cmd[:-2])
        self.shell_text = ""
        self.last_cmd_red = ""
        print("Result Commande ==>", self.result)
        return self.result

    def start_thread_serial(self):
        """Start the receiver thread
        
        """
        self.thread_serial = threading.Thread(target=self.thread_listen_port)
        self.alive.set()
        self.thread_serial.start()
        self.serial.rts = True
        self.serial.dtr = True
        self.read_thread = None

    def stop_thread_serial(self):
        """Stop the receiver thread, wait until it's finished.
        
        """
        if self.thread_serial is not None:
            self.alive.clear()          # clear alive event for thread
            self.thread_serial.join()   # wait until thread has finished
            self.thread_serial = None

    def OnKey(self, evt):
        """
        Key event handler. 
        
        If the key is in the ASCII range, write it to the
        serial port of the micropython board. 
        
        this method manages key pressed in text control console
           * Newline handling is also done here.
           * left arrow
           * right arrow
           * Backspace key 
           
        """
        code = evt.GetUnicodeKey()
        if code < 256:
            code = evt.GetKeyCode()
        if code == 13:  # is it a newline?
            self.serial.write(b'\n') # send new line ton serial port 
            self.on_key = False   # send LF
        # if code == 314: # left key 
        if code == wx.WXK_LEFT:
            self.keypressmsg = "\x1b\x5b\x44" # touche  fleche gauche 
            self.serial.write(b'\x1b\x5b\x44') # touche  fleche gauche 
            return
        if code == wx.WXK_RIGHT:
            self.keypressmsg = "\x1b\x5b\x43" # touche flèche droite 
            self.serial.write(b'\x1b\x5b\x43') # touche flèche droite 
            return
        if code == 8:
            self.keypressmsg = "\x08"   # touche Backspace  
            self.serial.write(b'\x08') # touche Backspace  
            return
        else:
            self.keypressmsg = "else"
        char = chr(code)
        self.serial.write(char.encode('UTF-8', 'ignore'))
        self.serial.flush()

    def thread_listen_port(self):
        """
        Thread that handles the incoming traffic. 
        Does the basic input
        transformation (newlines) and call an serial_read_data
        """
        while self.alive.is_set():
            try:
                b = self.serial.read(self.serial.in_waiting)
                self.is_data = False
            except Exception as e:
                my_speak(self, "Device Disconnected")
                print("ERROR : Device disconnected.") 
                print("Error: ", e)
                self.alive.clear()
                self.top_menu.MenuTools.OnDisconnect(None)
            if b:
                self.is_data = True
                b = b.replace(b'\r\n', b'\n')
                if not self.open_file:
                    serial_read_data(self, b)
                else:
                    print("self.open_file_txt : serial.in_waiting ??? ") 
                    self.open_file_txt += b.decode('utf-8', "ignore")

    def actualize_status_bar(self):
        """Actualize the Status Bar

        :param evt: Event binded to trigger the function
        :type evt: wx.Event https://wxpython.org/Phoenix/docs/html/wx.Event.html
        """
        if self.connected:
            text = "Status: %s %s %s" % (
                "Connected",
                self.serial_manager.card,
                self.serial_manager.version)
            self.statusbar.SetStatusText(text, 1)
        else:
            self.statusbar.SetStatusText("Status: %s" % "Not Connected", 1)

    def OnUpFocus(self, evt):
        """Allow to navigate in the differents region of the Frame after an event

        :param evt: Event binded to trigger the function
        :type evt: wx.Event https://wxpython.org/Phoenix/docs/html/wx.Event.html
        """
        widgets = [self.device_tree, self.shell, self.notebook.GetCurrentPage()]
        if self.who_is_focus == 2 and not widgets[self.who_is_focus]:
            self.who_is_focus = 0
            widgets[self.who_is_focus].SetFocus()
            return
        widgets[self.who_is_focus].SetFocus()
        if self.who_is_focus == 2:
            self.who_is_focus = 0
        else:
            self.who_is_focus += 1

    def OnDownFocus(self, evt):
        """Allow to navigate in the differents region of the Frame after an event

        :param evt: Event binded to trigger the function
        :type evt: wx.Event https://wxpython.org/Phoenix/docs/html/wx.Event.html
        """
        widgets = [self.device_tree, self.shell, self.notebook.GetCurrentPage()]
        if self.who_is_focus == 2 and not widgets[self.who_is_focus]:
            self.who_is_focus -= 1
            widgets[self.who_is_focus].SetFocus()
            return
        widgets[self.who_is_focus].SetFocus()
        if self.who_is_focus == 0:
            self.who_is_focus = 2
        else:
            self.who_is_focus -= 1

    def OnStatus(self, evt):
        """Set the Focus on the Status Bar

        :param evt: Event binded to trigger the function
        :type evt: wx.Event https://wxpython.org/Phoenix/docs/html/wx.Event.html
        """
        page = self.notebook.GetCurrentPage()
        if page and page.HasFocus:
            page.DocumentEnd()
            return
        self.statusbar.SetFocus()
        self.speak_on = self.statusbar.GetStatusText(1)

    def right_click_shortcut(self, evt):
        """ Link right click evt with a shortcut
        """
        if self.device_tree.HasFocus():
            self.device_tree.OnClipboardMenu(None)

    # FLB => ajout short cut alt + F4 (?) 

class MyApp(wx.App):
    """Minimal class to launch the app

    :param wx.App: https://wxpython.org/Phoenix/docs/html/wx.App.html
    """

    def OnInit(self):
        """Special constructor (do not modify) which affect the Mainwindow to the App

        :return: a boolean to stop or continue the
        :rtype: Bool
            --if False exit or error
            --if True the app works
        """

        # FLB => ajout methode super 
        # super().__init__()
        
        wx.InitAllImageHandlers()
        # get screen siez
        window_factor = 0.75
        display = wx.Display()
        display_size = display.GetGeometry().GetSize()
        width = int(window_factor*display_size[0])
        height = int(window_factor * display_size[1]) 
        
        # init window size 
        # window_size=(800, 600)
        window_size=(width, height)
        
        # fenetre principale de l'application 
        window = MainWindow("IDE Accessible MHK " + __version__, window_size)
        self.SetTopWindow(window)
        window.Show()
        return True


if __name__ == "__main__":
    # réorientation de la sortie 
    sys.stdout = sys.__stdout__
    app = MyApp()
    app.MainLoop()
    print("Exit App")
