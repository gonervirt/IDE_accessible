""" Module wich contain classes related to the Shell Panel

this module is used to generate the micropython console included the global GUI
"""

import wx
import json


class ShellPanel(wx.TextCtrl):
    """ Constructor method

        :param parent: in this case :class:wx.SplittedWindow
        :param frame: Main of the app :class:MainWindow
    """

    def __init__(self, parent, frame):
        """ Constructor method
         """

        # create text console
        text_console = wx.TextCtrl.__init__(self, parent=parent,
                             style=wx.TE_MULTILINE |
                             wx.TE_READONLY | wx.TE_RICH)
        self.__set_properties__(frame)
        
        # initialisation du texte dans la console à l'ouverture
        # text_console.SetValue("Micropython console") 
        
        # création d'un buffer d'historique de commandes
        self.command_history = []
        self.current_command_index = -1

    def __set_properties__(self, frame):
        """ Method to define new attributes and set style
         """

        self.frame = frame
        self.SetName("Python Shell")
        self.theme_choice = frame.notebook.theme_choice
        self.custom_shell(self.theme_choice)

    def custom_shell(self, theme_choice):
        """Custom the Shell panel with the given theme_choice

        :param theme_choice: The theme selected
        :type theme_choice: str
        """

        try:
            file = open("./customize.json")
            theme = json.load(file)
            file.close()
            theme = theme[theme_choice]
            self.font = wx.Font(14, wx.MODERN, wx.NORMAL,
                                wx.NORMAL, 0, "Arial")
            self.SetBackgroundColour(theme['Panels Colors']['Shell background'])
            self.SetFont(self.font)
            self.SetDefaultStyle(wx.TextAttr(
                theme['Panels Colors']['Text foreground'],
                theme['Panels Colors']['Shell background'],
                font=self.font))
            txt = self.GetValue()
            self.Clear()
            self.AppendText(txt)
        except Exception as e:
            text = "Can't customize shell Error: %s" % e
            print(text)
            self.AppendText(text)

    def move_key_left(self):
        """ Move the cursor on the previous character
        """

        print("cursor : move key left.")  
        cursor = self.GetInsertionPoint()
        self.SetInsertionPoint(cursor - 1)

    def move_key_right(self):
        """ Move the cursor on the next character
        """

        print("cursor : move key right.") 
        cursor = self.GetInsertionPoint()
        self.SetInsertionPoint(cursor + 1)

    def remove_char(self):
        """ Remove the previous character
        """
        print ("remove previous char ")
        cursor = self.GetInsertionPoint()
        self.Remove(cursor - 1, cursor)
    
    def move_key_up(self):
        """ Move the cursor on the next character
        """
        print ("move key up.")
        
    def move_key_down(self):
        """ Move the cursor on the next character
        """
        print ("move key down")
        
    def on_key_down(self, event):
        print ("on key down")
        keycode = event.GetKeyCode()
        print("key code : ", keycode) 

        if keycode == wx.WXK_RETURN:
            command = self.text_ctrl.GetValue()
            self.command_history.append(command)
            self.current_command_index = -1  # Reset command index

            # Execute the command (you can implement your own command execution logic)
            self.execute_command(command)

            self.text_ctrl.SetValue('')  # Clear the input field

        elif keycode == wx.WXK_UP:
            if self.current_command_index < len(self.command_history) - 1:
                self.current_command_index += 1
                self.text_ctrl.SetValue(self.command_history[self.current_command_index])

        elif keycode == wx.WXK_DOWN:
            if self.current_command_index >= 0:
                self.current_command_index -= 1
                if self.current_command_index == -1:
                    self.text_ctrl.SetValue('')
                else:
                    self.text_ctrl.SetValue(self.command_history[self.current_command_index])

        event.Skip()

    