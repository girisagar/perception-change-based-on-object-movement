#!/bin/env python
#----------------------------------------------------------------------------
# Name:         settings.py
# Author:       Subodh Dahal
# Created:      2013/08/03
# Copyright:
#----------------------------------------------------------------------------

import json
import os
import wx
from wx.lib.pubsub import Publisher
from settings_wdr import *


# WDR: classes

class MainFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        kwargs[
            'style'] = wx.MINIMIZE_BOX | wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.WANTS_CHARS

        super(MainFrame, self).__init__(*args, **kwargs)

        self.__properties()
        self.__layout()

        # WDR: handler declarations for MainFrame
        wx.EVT_MENU(self, wx.ID_ABOUT, self.on_about)
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnQuit)
        wx.EVT_CLOSE(self, self.OnHideWindow)

    # WDR: methods for MainFrame

    def __properties(self):
        # path = os.path.abspath('./logo.ico')
        # icon = wx.Icon(path, wx.BITMAP_TYPE_ICO)
        # self.SetIcon(icon)
        self.config_file = open('../config.json')
        try:
            # Open the configuration file to read the settings from
            self.config = json.load(self.config_file)
        except:
            print 'Configuration file not found.'
            exit()

        self.key_maps = {
            '(nothing)': '(nothing)',
            'K_ALT': 'Alt',
            'K_CONTROL': 'Ctrl',
            'K_SHIFT': 'Shift',
            'K_LEFT': 'Left',
            'K_RIGHT': 'Right',
            'K_UP': 'Up',
            'K_DOWN': 'Down'
        }

        self.keys = [
            'Up', 'Down', 'Left', 'Right', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '+', '[', ']', '{', '}', '<', '>', '?', '/', ',', '.', '(', ')']

        self.panel = wx.Panel(self)
        self.Center()
        self.SetSize((450, 400))

        Publisher().subscribe(self.add_app_to_list, ('ApplicationName'))

    def __layout(self):
        self.CreateMyMenuBar()
        # insert main window here
        NotebookTab(self.panel)

        self.notebook = self.FindWindowById(ID_NOTEBOOK)
        exit_button = self.FindWindowById(EXIT_APP)
        exit_button.Bind(wx.EVT_BUTTON, self.OnHideWindow)

        if self.config['detection_method'] == 'Face':
            self.FindWindowById(CHOICE_FACE).SetValue(True)
            self.FindWindowById(CHOICE_HAND).SetValue(False)
        elif self.config['detection_method'] == 'Hand':
            self.FindWindowById(CHOICE_FACE).SetValue(False)
            self.FindWindowById(CHOICE_HAND).SetValue(True)

        self.save_methodbtn = self.FindWindowById(SAVE_METHOD)
        self.save_methodbtn.Bind(wx.EVT_BUTTON, self.save_method)

        # Get the application list page
        self.apps = self.notebook.GetPage(1)
        self.application_list(parent=self.apps)

        # Get the application config page
        self.app_config = self.notebook.GetPage(2)

        self.app_choice = self.FindWindowById(APP_CHOICE)

        self.key_left = self.FindWindowById(KEY_LEFT)
        self.key_right = self.FindWindowById(KEY_RIGHT)
        self.key_popen = self.FindWindowById(KEY_POPEN)
        self.key_pclose = self.FindWindowById(KEY_PCLOSE)

        self.key_left.Clear()
        self.key_left.AppendItems(self.keys)

        self.key_right.Clear()
        self.key_right.AppendItems(self.keys)

        self.key_popen.Clear()
        self.key_popen.AppendItems(self.keys)

        self.key_pclose.Clear()
        self.key_pclose.AppendItems(self.keys)

        self.app_save = self.FindWindowById(CONFIG_SAVE)
        self.app_delete = self.FindWindowById(APP_DELETE)

        self.__reload_app_config()

        self.app_choice.Bind(wx.EVT_CHOICE, self.display_app_config)

        self.app_save.Bind(wx.EVT_BUTTON, self.save_app_config)
        self.app_delete.Bind(wx.EVT_BUTTON, self.delete_app)

    def __reload_config(self):
        ''' Reload the config file '''
        self.config_file.close()
        json.dump(self.config, open(
            '../config.json', 'w'), sort_keys=True, indent=4)
        self.config_file = open('../config.json')
        self.config = json.load(self.config_file)

    def __reload_app_config(self):
        ''' Re-populate the application list in the config page '''
        self.app_choice.Clear()
        for window in self.config.get('allowed_windows'):
            self.app_choice.Append(window.get('name'))

    def CreateMyMenuBar(self):
        self.SetMenuBar(MyMenuBarFunc())

    def dynamic_app_list(self, app, parent):
        ''' An application list '''
        app_name = wx.StaticText(
            parent, ID_TEXT, app, wx.DefaultPosition, wx.DefaultSize, 0)
        parent.app_list.Add(app_name, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Set sizer and call fit
        parent.SetSizer(parent.app_list_vsizer)
        parent.app_list_vsizer.SetSizeHints(parent)

    def application_list(self, event=None, parent=None):
        ''' The window for displaying application list for adding, editing, deleting applications'''
        # Bind the 'Add New Application' button
        self.add_app = self.FindWindowById(ADD_APP)
        self.add_app.Bind(wx.EVT_BUTTON, self.new_app)
        # print len(self.config['allowed_windows'])
        parent.app_list.DeleteWindows()

        for window in self.config.get('allowed_windows'):
            # Dynamically add the application list to the window
            self.dynamic_app_list(window.get('name'), parent)

    # WDR: handler implementations for MainFrame
    def save_method(self, event):
        print self.FindWindowById(CHOICE_FACE).GetValue()
        print self.FindWindowById(CHOICE_HAND).GetValue()

        self.config['detection_method'] = 'Face' if self.FindWindowById(
            CHOICE_FACE).GetValue() else 'Hand'
        self.__reload_config()
        wx.MessageBox(
            'The settings have been saved.',
            style=wx.CENTER | wx.OK)

    def add_app_to_list(self, msg):
        ''' What happens when an application name is added '''
        parent = self.apps

        self.config[
            'allowed_windows'].append({'name': msg.data,
                                       'on_left': '',
                                       'on_right': '',
                                       'on_popen': '',
                                       'on_pclose': ''})
        self.__reload_config()
        self.dynamic_app_list(msg.data, parent)
        self.__reload_app_config()

    def display_app_config(self, event):
        ''' Display configuration of the selected application '''

        detection_method = {
            'Face': 'Face Detection and Tracking',
            'Hand': 'Hand Gesture Recognition and Tracking',
            'Both': 'Both Face & Hand'
        }

        for i, window in enumerate(self.config['allowed_windows']):
            if window.get('name') == self.app_choice.GetStringSelection():
                req_app = self.config['allowed_windows'][i]

        on_left = req_app.get('on_left').split('`')
        on_left.insert(0, u'(nothing)') if len(on_left) == 1 else ''

        on_right = req_app.get('on_right').split('`')
        on_right.insert(0, u'(nothing)') if len(on_right) == 1 else ''

        on_popen = req_app.get('on_popen').split('`')
        on_popen.insert(0, u'(nothing)') if len(on_popen) == 1 else ''

        on_pclose = req_app.get('on_pclose').split('`')
        on_pclose.insert(0, u'(nothing)') if len(on_pclose) == 1 else ''

        works_on = req_app.get('works_on')

        print on_left
        print on_right
        print on_popen
        print on_pclose

        # self.key_left.Bind(wx.EVT_CHOICE, self.add_left_key)
        # print self.key_left.GetItems()
        # print self.key_left.GetStringSelection()

        # Set the fields based on the configuration of the application
        self.FindWindowById(MODIFIER_LEFT).SetStringSelection(on_left[0])
        self.key_left.SetStringSelection(
            self.key_maps.get(on_left[1], on_left[1]))

        self.FindWindowById(MODIFIER_RIGHT).SetStringSelection(on_right[0])
        self.key_right.SetStringSelection(
            self.key_maps.get(on_right[1], on_right[1]))

        self.FindWindowById(MODIFIER_POPEN).SetStringSelection(on_popen[0])
        self.key_popen.SetStringSelection(
            self.key_maps.get(on_popen[1], on_popen[1]))

        self.FindWindowById(MODIFIER_PCLOSE).SetStringSelection(on_pclose[0])
        self.key_pclose.SetStringSelection(
            self.key_maps.get(on_pclose[1], on_pclose[1]))

        self.FindWindowById(WORKS_ON).SetStringSelection(
            detection_method[works_on])

    def save_app_config(self, event):
        ''' Save the application configuration to file '''
        detection_method = {
            'Face Detection and Tracking': 'Face',
            'Hand Gesture Recognition and Tracking': 'Hand',
            'Both Face & Hand': 'Both'
        }

        get_key = lambda search_value: self.key_maps.keys()[
            self.key_maps.values().index(search_value)] if search_value in self.key_maps.values() else search_value

        for i, window in enumerate(self.config['allowed_windows']):
            if window.get('name') == self.app_choice.GetStringSelection():
                on_left = get_key(self.FindWindowById(MODIFIER_LEFT).GetStringSelection()) + '`' + get_key(
                    self.key_left.GetStringSelection())

                on_right = get_key(self.FindWindowById(MODIFIER_RIGHT).GetStringSelection()) + '`' + get_key(
                    self.key_right.GetStringSelection())

                on_popen = get_key(self.FindWindowById(MODIFIER_POPEN).GetStringSelection()) + '`' + get_key(
                    self.key_popen.GetStringSelection())

                on_pclose = get_key(self.FindWindowById(MODIFIER_PCLOSE).GetStringSelection()) + '`' + get_key(
                    self.key_pclose.GetStringSelection())

                works_on = detection_method[
                    self.FindWindowById(WORKS_ON).GetStringSelection()]

                self.config['allowed_windows'][i]['on_left'] = on_left
                self.config['allowed_windows'][i]['on_right'] = on_right
                self.config['allowed_windows'][i]['on_popen'] = on_popen
                self.config['allowed_windows'][i]['on_pclose'] = on_pclose
                self.config['allowed_windows'][i]['works_on'] = works_on

                self.__reload_config()

                wx.MessageBox(
                    'The settings have been saved.',
                    style=wx.CENTER | wx.OK)

    def delete_app(self, event):
        ''' Delete an application from the list '''
        app_name = self.app_choice.GetStringSelection()

        result = wx.MessageBox(
            'Are you sure you want to delete the application ' +
            app_name + ' ?',
            style=wx.CENTER | wx.ICON_QUESTION | wx.YES_NO)

        if result == wx.YES:
            for i, window in enumerate(self.config['allowed_windows']):
                if window.get('name') == app_name:
                    # delete the application from memory and write it to file`
                    del(self.config['allowed_windows'][i])

                    self.__reload_config()

                    # Re-populate the application list in the config page
                    self.__reload_app_config()

                    self.application_list(parent=self.apps)

                    wx.MessageBox(
                        'The application has been deleted.',
                        style=wx.CENTER | wx.OK)

    def new_app(self, event=None):
        '''Launch dialog for adding a new application'''
        frame = NewAppDialog(None, -1, 'New Application', [
                             20, 20], [300, 130])
        frame.Show(True)
        # self.SetTopWindow(frame)
        return True

    def on_about(self, event):
        wx.InitAllImageHandlers()
        dialog = wx.MessageDialog(self, 'Perception Change Based on Object Movement\n'
                                        'Authors:\n'
                                        '\tRaj Kumar Shah\n'
                                        '\tSagar Giri\n'
                                        '\tSubodh Dahal\n'
                                        '\tSudeep Bagale\n',
                                  'About GestureApp', wx.OK | wx.ICON_INFORMATION)
        dialog.CentreOnParent()
        dialog.ShowModal()
        dialog.Destroy()

    def OnButton(self, event):
        evt_id = event.GetId()
        print evt_id
        if evt_id == self.app_edit.GetId():
            self.notebook.SetSelection(2)
            self.app_choice.SetSelection(self.app_choice.FindString('VLC'))

    def OnHideWindow(self, event):
        self.Hide()

    def OnQuit(self, event):
        result = wx.MessageBox(
            'Are you sure you want to close this window?',
            style=wx.CENTER | wx.ICON_QUESTION | wx.YES_NO)
        if result == wx.YES:
            self.Destroy()


class NewAppDialog(wx.Frame):

    '''Dialog for adding a new application'''

    def __init__(self, *args, **kwargs):
        kwargs[
            'style'] = wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.WANTS_CHARS | wx.STAY_ON_TOP

        super(NewAppDialog, self).__init__(*args, **kwargs)
        self.panel = wx.Panel(self)
        NewApplication(self.panel)
        self.panel.SetFocus()
        self.Center()

        button = self.FindWindowById(ADD_APP_TO_LIST)
        button.Bind(wx.EVT_BUTTON, self.AddAndClose)

        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnKeyDown(self, e):
        key = e.GetKeyCode()
        print key
        if key == wx.WXK_ESCAPE:
            self.Close()

    def AddAndClose(self, event):
        app_name = self.FindWindowById(NEW_APP_NAME)
        # Close the dialog box
        Publisher().sendMessage(('ApplicationName'), app_name.GetValue())
        self.Close(True)
#----------------------------------------------------------------------------


class SystemTray(wx.TaskBarIcon):
    ID_SETTINGS = wx.NewId()
    ID_ABOUT = wx.NewId()

    def __init__(self, main_frame):
        super(SystemTray, self).__init__()
        # Setup
        icon = wx.Icon('icon.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        # Event Handlers
        self.Bind(wx.EVT_MENU, self.OnMenu)

        self.main_frame = main_frame
        self.main_frame.Show(True)
        self.run_app()

    def CreatePopupMenu(self):
        ''' Base class virtual method for creating the popup menu for the icon. '''
        menu = wx.Menu()
        menu.Append(SystemTray.ID_SETTINGS, 'Settings')
        menu.Append(SystemTray.ID_ABOUT, 'About')
        menu.AppendSeparator()
        menu.Append(wx.ID_CLOSE, 'Exit')
        return menu

    def OnMenu(self, event):
        evt_id = event.GetId()
        if evt_id == SystemTray.ID_SETTINGS:
            self.main_frame.Show(True)
        if evt_id == SystemTray.ID_ABOUT:
            self.on_about()
        elif evt_id == wx.ID_CLOSE:
            result = wx.MessageBox(
                'Are you sure you want to close this window?',
                style=wx.CENTER | wx.ICON_QUESTION | wx.YES_NO)
            if result == wx.YES:
                self.exit()
        else:
            event.Skip()

    def run_app(self):
        pass

    def on_about(self):
        wx.MessageBox('Perception Change Based on Object Movement\n'
                               'Authors:\n'
                               '\tRaj Kumar Shah\n'
                               '\tSagar Giri\n'
                               '\tSubodh Dahal\n'
                               '\tSudeep Bagale\n',
                               'About GestureApp')

    def exit(self):
        try:
            self.main_frame.Destroy()
        except wx._core.PyDeadObjectError as e:
            pass
        finally:
            self.Destroy()


class GestureApp(wx.App):

    def OnInit(self):
        wx.InitAllImageHandlers()
        frame = MainFrame(None, -1, 'Settings :: Perception Change App', [
                          20, 20])
        SystemTray(frame)

        return True

#----------------------------------------------------------------------------
if __name__ == '__main__':
    app = GestureApp(False)
    app.MainLoop()
