"""
Module which has functions and classes to manage the connection
and communication with the card
"""

import os
import time
from Serial_manager.send_infos import put_cmd
from Panels.Device_tree import treeModel


class ManageConnection():
    """
    Class with useful methods to manage Connection related with the frame
    
    this class contains folowing methods : 
    * get_card_infos : to get information related to connected board (type, version, release, machine, etc) 
    * upload_and_run : upload and run script from editor panel to connected device.
    * upload : upload script from editor panel to connected device. 
    * write_in_file : write file from the computer to the connected device 
    * ConnectSerial : connect device to the computer via serial link 
    * _check_extension_file : check file name extension 
    
    """

    def __init__(self, frame):
        """Constructor for ManageConnection class

        :param frame: The MainWindow to get some properties
        :type frame: MainWindow class
        """

        self.frame = frame
        self.last_cmd = ""
        self.card = None
        self.nodename = None
        self.release = None
        self.version = None
        self.machine = None

    def get_card_infos(self, msg_cmd):
        """Get the name, the version of the firmware and the type of the
         connected device
         
         this method returns :
         * self.card (name of the connected board)
         * self.nodename 
         * self.version (micropython version and release date)
         * self.machine (board type) 

        :param msg_cmd: Result of a command
        :type msg_cmd: string
        """
        try:
            count = 0
            msg_cmd = msg_cmd.split('(')[1]
            msg_cmd = msg_cmd.split(')')[0]
            res = tuple(map(str, msg_cmd.split(', ')))
            list_res = []

            for i in res:
                i = i.split('=')
                i = i[1][1:-1]
                list_res.append(i)
                count += 1

            self.card = list_res[0]
            self.nodename = list_res[1]
            self.release = list_res[2]
            self.version = list_res[3]
            self.machine = list_res[4]
        except Exception as e:
            print("Error get infos device: \n", e)
        if self.card == "pyboard":
            self.frame.time_to_send = 0.1

    # FLB => add method to detect presence of micro SD card  
    def detect_SD_card(self, nodename):
        """Detects presence of a micro SD card on the device
        
           param : nodename of the connected device 
           type : str example 'pyboard'
        """
        
        self.nodename=nodename
        
        if self.nodename == 'pyboard': 
            # import needed modules 
            cmd = "import pyb" 
            self.frame.exec_cmd(cmd) 
            cmd = "sd = pyb.SDCard()" 
            self.frame.exec_cmd(cmd)         
            cmd = "sd.present()" 
            res = self.frame.exec_cmd(cmd)         
            print("SD card detected on ", self.nodename, " : " , res) 
        else: 
            # import needed modules 
            cmd = "from machine import SDCard" 
            self.frame.exec_cmd(cmd) 
            cmd = "sd=sdcard()" 
            self.frame.exec_cmd(cmd)         
            cmd = "sd.present()" 
            res = self.frame.exec_cmd(cmd)         
            print("SD card detected : ", res) 
        if res == True:
            return True
        else:
            return False 

    def upload_and_run(self, filename):
        """Execute the file gived in params on the MicroPython card

        :param filename: the path of the file to execute
        :type filename: str
        """

        time.sleep(1)
        put_cmd(self.frame, '\x03')
        put_cmd(self.frame, "exec(open(\'%s\').read(),globals())\r\n"
                % str(filename))
        self.frame.shell.SetFocus()


    def upload(self, filepath, filename):
        """ Download a file on the card

        :param filepath: path of the file to upload
        :type filepath: str
        :param filename: name of the file to upload
        :type filename: str
        :return: success flag
        :rtype: boolean
        """

        filepath = filepath.replace("\\", "/")
        file_to_open = _check_extension_file(filename, ".py")

        if not file_to_open:
            self.frame.shell.WriteText("Error extension file isn't .py\n")
            return False
        try:
            fileHandle = open(filepath, 'rbU')
            print("SIZE_open=", os.path.getsize(filepath))
        except Exception as e:
            print("Error file : %s" % (e))
            self.frame.shell.WriteText("Error on during file upload\n...")

        put_cmd(self.frame, '\x03')
        self.frame.show_cmd = False
        self.frame.shell.Clear()
        self.frame.shell.WriteText("Ready to upload this file...!\n")
        self.write_in_file(fileHandle, file_to_open)
        treeModel(self.frame)

    def write_in_file(self, fileHandle, file_to_open):
        """Write bytes of a computer file on a file on the device

        :param fileHandle: fileHandle to read
        :type fileHandle: file handled see :function: open()
        :param file_to_open: device file
        :type file_to_open: str
        """

        try:
            if self.card == "pyboard":
                done = 0
                cmd = "myfile=open(\'%s\',\'w\')\r\n" % str(file_to_open)
                put_cmd(self.frame, cmd)
                while not done:
                    aline = fileHandle.read(128)
                    if(str(aline) != "b''"):
                        try:
                            aline = aline.decode()
                            aline = "myfile.write(%s)\r\n" % repr(aline)
                        except Exception as e:
                            aline = "myfile.write(%s)\r\n" % repr(aline)
                            print(e)
                        for i in aline:
                            put_cmd(self.frame, i)
                        self.frame.shell.AppendText("Wait...\n")
                        self.frame.shell.AppendText("Wait..\n")
                        self.frame.shell.AppendText("Wait.\n")
                    else:
                        done = 1
                fileHandle.close()
                put_cmd(self.frame, "myfile.close()\r")
                for i in range(10):
                    self.frame.exec_cmd("\r\n")
                time.sleep(0.01)
            else:
                cmd = "myfile=open('%s','w')\r\n" % str(file_to_open)
                self.frame.exec_cmd(cmd)
                line = fileHandle.read().decode()
                cmd = "myfile.write(%s)\r\n" % repr(line)
                self.frame.exec_cmd(cmd)
                self.frame.exec_cmd("myfile.close()\r\n")
                self.frame.exec_cmd("\r\n")
        except Exception as e:
            print(e)


def ConnectSerial(self):
    """Try to connect the device and the software

    :return: success flag
    :rtype: boolean
    """

    print("serial  manager - connexion.py") 
    print(" ConnectSerial method ") 
    self.shell.Clear()
    self.serial.write('\x03'.encode())

    startdata = ""
    startTime = time.time()
    while True:
        n = self.serial.inWaiting()
        if n > 0:
            startdata += (self.serial.read(n)).decode(encoding='utf-8', errors='ignore')
            print("start data : [%s]" % startdata)
            if startdata.find('>>> '):
                print("start data : OK")
                break
        time.sleep(0.1)
        endTime = time.time()
        if endTime-startTime > 10:
            self.serial.close()
            if not self.serial.isOpen():
                print("UPDATE FIRMWARE")
                return False
            return False
    senddata = "import sys\r\n"
    # FLB => modification parametre et ajout du print
    print("put_cmd : ", senddata) 
    put_cmd(self, senddata)
    # FLB => remove sending char by char 
    # for i in senddata:
    #     self.serial.write(i.encode())
    startdata = ""
    startTime = time.time()
    while True:
        n = self.serial.inWaiting()
        if n > 0:
            startdata += (self.serial.read(n)).decode('utf-8', 'ignore')
            if startdata.find('>>> ') >= 0:
                # FLB => ajout du prompt dans la fenetre shell 
                # FLB => modify initial shell information
                print("add >>> to shell console") 
                # FLB => ajout texte "connectect dans la console de shell
                #   MARCHE PAS et POURQUOI ????
                self.shell.AppendText("Connected to device. \r\n") 
                self.shell.AppendText(">>> ")
                break
        time.sleep(0.1)
        endTime = time.time()
        if endTime-startTime > 10:
            print(startdata)
            self.serial.close()
            self.shell.AppendText("connect serial timeout: Retry or update firmware")
            return False
    time.time()
    senddata = "sys.platform\r\n"
    for i in senddata:
        self.serial.write(i.encode())
    startdata = ""
    startTime = time.time()
    while True:
        n = self.serial.inWaiting()
        if n > 0:
            startdata += (self.serial.read(n)).decode('utf-8')
            if startdata.find('>>> ') >= 0:
                break
        time.sleep(0.1)
        endTime = time.time()
        if endTime-startTime > 2:
            self.serial.close()
            self.shell.AppendText("connect serial timeout: retry or update firmware")
            return False
    return True


def _check_extension_file(filename, extension):
    """Check the extension file correspond to the extension asked

    :param filename: file to chek
    :type filename: str
    :param extension: extensions to find
    :type extension: [type]
    :return: finalname or None
    :rtype: [type]
    """

    finalname = ""
    if str(filename).find(extension) >= 0:
        if str(filename).find(":") < 0:
            finalname = str(filename)
            return finalname
        else:
            print("error path",)
            return None
    else:
        print("error extension")
        return None
