"""
    Module wich contains the FileMenu class and some functions linked to this menu
"""

import wx
import os
from Panels.Editor import Styled_Editor
from Panels.Device_tree import save_on_card
from Utils.voice_synthese import my_speak


class FileMenu(wx.Menu):
    """Inits a instance of a wx.Menu to create a File menu and his buttons
     (Copy, Paste, Find,...)

    :return: the File menu filled by buttons
    :rtype: wx.Menu see https://wxpython.org/Phoenix/docs/html/wx.Menu.html
    """

    def __init__(self, frame):
        """ Constructor method

        :param frame: main window
        :type frame: MainWindow
        """

        wx.Menu.__init__(self, "File")
        self.frame = frame

        self.Append(wx.ID_NEW, "&New\tCTRL+N")
        self.Append(wx.ID_OPEN, "&Open\tCTRL+O")
        self.Append(wx.ID_SAVE, "&Save\tCTRL+S")
        self.Append(wx.ID_SAVEAS, "&Save as\tCTRL+A")
        self.Append(wx.ID_CLOSE, "&Close\tCTRL+W")
        self.Append(wx.ID_EXIT, "&Exit\tCTRL+Q")

    def OnExit(self, evt):
        """Quit the app

        :param evt: Event to trigger the method
        :type evt: wx.Event
        """

        self.frame.stop_thread_serial()
        self.frame.serial.close()
        self.frame.Destroy()

    def OnSave(self, evt):
        """Save the current page of the notebook

        :param evt: Event to trigger the method
        :type evt: wx.Event
        """

        notebookP = self.frame.notebook
        page = notebookP.GetCurrentPage()
        if page.on_card:
            return save_on_card(self.frame, page)
        if (page.GetValue() != page.last_save):
            page.saved = False
        if (page.saved is False and page.last_save == ""):
            dialog = wx.FileDialog(self.frame, "Choose a file",
                                   page.directory, "", "*",
                                   wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dialog.ShowModal() == wx.ID_OK:
                save_as_file_contents = page.GetValue()
                save_as_name = dialog.GetFilename()
                save_as_directory = dialog.GetDirectory()
                filehandle = open(os.path.join(save_as_directory, save_as_name), 'w')
                filehandle.write(save_as_file_contents)
                filehandle.close()
                notebookP.SetPageText(notebookP.GetSelection(), save_as_name)
                page.filename = save_as_name
                page.directory = save_as_directory
                page.last_save = save_as_file_contents
                page.saved = True
        else:
            save_as_file_contents = page.GetValue()
            filehandle = open(os.path.join(page.directory, page.filename), 'w')
            filehandle.write(save_as_file_contents)
            filehandle.close()
            page.last_save = save_as_file_contents
            page.saved = True
        self.frame.shell.AppendText("Content Saved\n")
        my_speak(self.frame, "Content Saved")

    def OnSaveAs(self, evt):
        """Open a wx.filedialog to Save as a file the text of the current editor

        :param evt: Event to trigger the method
        :type evt: wx.Event
        """

        notebookP = self.frame.notebook
        page = notebookP.GetCurrentPage()
        dialog = wx.FileDialog(self.frame, "Choose a file", page.directory,
                               "", "*.py*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        dialog.CenterOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            save_as_file_contents = page.GetValue()
            save_as_name = dialog.GetFilename()
            save_as_directory = dialog.GetDirectory()
            filehandle = open(os.path.join(
                save_as_directory, save_as_name), 'w')
            filehandle.write(save_as_file_contents)
            filehandle.close()
            notebookP.SetPageText(notebookP.GetSelection(), save_as_name)
            page.filename = save_as_name
            page.directory = save_as_directory
            page.last_save = save_as_file_contents
            page.saved = True
            my_speak("Content Saved")
        dialog.Destroy()

    def OnOpen(self, evt):
        """Open a wx.filedialog to open a file on a editor

        :param evt: Event to trigger the method
        :type evt: wx.Event
        """

        notebookP = self.frame.notebook
        dialog = wx.FileDialog(self.frame,
                               "Choose a File",
                               "",
                               "",
                               "*",
                               style=wx.FD_OPEN)

        dialog.CenterOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetFilename()
            directory = dialog.GetDirectory()
            filehandle = open(os.path.join(directory, filename), 'r')
            notebookP.new_page(filename, directory, filehandle.read(), False)
            page = notebookP.GetCurrentPage()
            page.last_save = page.GetValue()
            page.saved = True
            filehandle.close()
        dialog.Destroy()

    def OnAddPage(self, evt):
        """Add a new page on the notebook

        :param evt: Event to trigger the method
        :type evt: wx.Event
        """

        notebookP = self.frame.notebook
        new_tab = Styled_Editor(notebookP, self.frame, "", False)
        notebookP.AddPage(new_tab, "Tab %s" % new_tab.id, select=True)
        notebookP.tab_num = notebookP.GetPageCount()
        new_tab.SetFocus()

    def OnClosePage(self, evt):
        """Close the current page and update id order

        :param evt: Event to trigger the method
        :type evt: wx.Event
        """

        notebook = self.frame.notebook
        page = notebook.GetCurrentPage()
        if page and not page.saved:
            ok = False
            while not ok:
                with wx.MessageDialog(self.frame,
                                      "File_not_saved ! Save ?",
                                      "File_not_saved ! Save ?",
                                      style=wx.YES_NO) as dlg:
                    result = dlg.ShowModal()
                    dlg.CenterOnParent()
                if result == wx.ID_YES:
                    self.OnSave(None)
                    ok = True
                else:
                    ok = True
        if page:
            notebook.DeletePage(page.id - 1)
            notebook.tab_num = notebook.GetPageCount()

        nb_pg = notebook.tab_num
        i = 1
        while i <= nb_pg:
            page_to_update = notebook.GetPage(i - 1)
            page_to_update.id = i
            i += 1
