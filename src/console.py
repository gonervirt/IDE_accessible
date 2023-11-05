import wx

class ConsoleFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.command_history = []
        self.current_command_index = -1

        self.Show()

    def on_key_down(self, event):
        keycode = event.GetKeyCode()

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

    def execute_command(self, command):
        # Implement your own command execution logic here
        # For example, you can print the command to the console
        print(f"Executing command: {command}")

"""
app = wx.App()
ConsoleFrame(None, 'Python Console')
app.MainLoop()
"""