#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import re
from threading import Thread

import wx

from fileshandle import loadJson as lj


class MyMiniFrame(wx.MiniFrame):
    def __init__(self, parent, title, pos, size, style, mess, autohide):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)

        self.closewin = None
        self.prnt = parent
        self.prnt.messalive = True

        panel = wx.Panel(self, -1)
        txt = wx.StaticText(panel, -1, str(mess))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)


        self.CenterOnParent(wx.BOTH)
        self.Show()

        if autohide:
            self.closewin = Thread(target=self.timer, args=(0,))
            self.closewin.start()

    def timer(self, a):
        x = 0
        while x < 2:
            x += 1
            sleep(1)

        wx.CallAfter(self.OnCloseMe)

    def OnCloseMe(self):
        self.prnt.messalive = False
        self.Close()

    def OnCloseWindow(self, e):
        self.Destroy()


class CharsCheckList(wx.Frame):
    def __init__(self, parent, ref):
        wx.Frame.__init__(self, parent, -1, "")

        self.prnt = parent

        self.notebook = wx.Notebook(self, -1, style=0)
        self.pane_0 = wx.Panel(self.notebook, -1)
        self.pane_1 = wx.Panel(self.notebook, -1)
        self.pane_2 = wx.Panel(self.notebook, -1)

        self.chars = lj("/pglib/charsets.json")

        self.ref = ref

        self.statecb0 = True
        self.statecb1 = True
        self.statecb2 = True

        lbpane1ck = ['a', 'b', 'c']
        lb_size = (330, 160)
        self.lb_pane0 = wx.CheckListBox(self.pane_0, -1, (5, 5), lb_size, self.chars['letters'])
        for i in range(self.lb_pane0.GetCount()):
            if self.chars['letters'][i] in self.prnt.chars['letters']:
                self.lb_pane0.Check(i, True)
        self.lb_pane1 = wx.CheckListBox(self.pane_1, -1, (5, 5), lb_size, self.chars['numbers'])
        for i in range(self.lb_pane1.GetCount()):
            if self.chars['numbers'][i] in self.prnt.chars['numbers']:
                self.lb_pane1.Check(i, True)
        self.lb_pane2 = wx.CheckListBox(self.pane_2, -1, (5, 5), lb_size, self.chars['specials'])
        for i in range(self.lb_pane2.GetCount()):
            if self.chars['specials'][i] in self.prnt.chars['specials']:
                self.lb_pane2.Check(i, True)

        self.checklb = wx.Button(self, -1, "Cocher/Décocher")
        self.static_line_1 = wx.StaticLine(self, -1)
        self.text_ctrl_setperso = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.sizer_setperso_staticbox = wx.StaticBox(self, -1, "Modifier set perso")
        self.static_line_2 = wx.StaticLine(self, -1)
        self.button_quit = wx.Button(self, -1, "Quitter")
        self.button_submit = wx.Button(self, -1, "Valider")

        self.Bind(wx.EVT_BUTTON, self.checkUncheck, self.checklb)
        self.Bind(wx.EVT_BUTTON, self.closeEdit, self.button_quit)
        self.Bind(wx.EVT_BUTTON, self.validEdit, self.button_submit)

        self.__set_properties()
        self.__do_layout()

        if ref is not None:
            self.notebook.ChangeSelection(ref)

        if len(self.prnt.persoslist) > 0:
            x = True
            br = "\n"
            for i in self.prnt.persoslist:
                if x:
                    br = ""
                    x = False
                else:
                    br = "\n"
                self.text_ctrl_setperso.AppendText("%s%s" % (br, str(i)))

    def __set_properties(self):
        self.SetTitle("Edition des jeux")
        self.notebook.SetMinSize((350, 200))

    def __do_layout(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_submit = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_setperso_staticbox.Lower()
        sizer_setperso = wx.StaticBoxSizer(self.sizer_setperso_staticbox, wx.HORIZONTAL)
        self.notebook.AddPage(self.pane_0, "Lettres")
        self.notebook.AddPage(self.pane_1, "Nombres")
        self.notebook.AddPage(self.pane_2, "Speciaux")
        sizer_main.Add(self.notebook, 2, wx.ALL|wx.EXPAND, 5)
        sizer_main.Add(self.checklb, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        sizer_main.Add(self.static_line_1, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        sizer_setperso.Add(self.text_ctrl_setperso, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_setperso, 1, wx.ALL|wx.EXPAND, 5)
        sizer_main.Add(self.static_line_2, 0, wx.ALL|wx.EXPAND, 5)
        sizer_submit.Add(self.button_quit, 1, wx.RIGHT|wx.ADJUST_MINSIZE, 7)
        sizer_submit.Add(self.button_submit, 1, wx.LEFT|wx.ADJUST_MINSIZE, 7)
        sizer_main.Add(sizer_submit, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer_main)
        sizer_main.Fit(self)
        self.Layout()
        self.Centre()
        self.Show()

    def checkUncheck(self, e):
        getpage = self.notebook.GetSelection()
        lbc = None
        x = True

        if getpage == 0:
            lbc = self.lb_pane0
            if self.statecb0:
                self.statecb0 = False
                x = False
            else:
                self.statecb0 = True
        if getpage == 1:
            lbc = self.lb_pane1
            if self.statecb1:
                self.statecb1 = False
                x = False
            else:
                self.statecb1 = True
        if getpage == 2:
            lbc = self.lb_pane2
            if self.statecb2:
                self.statecb2 = False
                x = False
            else:
                self.statecb2 = True

        for i in range(lbc.GetCount()):
            lbc.Check(i, x)

    def closeEdit(self, e):
        self.Close()

    def validEdit(self, e):
        testpersos = False
        persos = self.text_ctrl_setperso.GetValue()

        if persos != "":
            persos = persos.strip() + "\n"
            x = re.search(r'^([^\s]\s){1,}$', persos)
            if x is not None:
                testpersos = True
            else:
                dlg = wx.MessageDialog(self, 'Le(s) set(s) perso(s) semble(nt) mal formé(s)? Pour valider sans utiliser les sets persos clickez sur OK, sinon clickez sur Annuler pour revenir à la fenêtre.', 'Message', wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
                if dlg.ShowModal() == wx.ID_OK:
                    testpersos = True
        else:
            testpersos = True

        if testpersos:
            if persos != "":
                self.prnt.combobox_setperso.Clear()
                persos = persos.strip()
                t = persos.split("\n")
                for i in t:
                    self.prnt.combobox_setperso.Append(i)

            newletters = []
            for i in range(self.lb_pane0.GetCount()):
                if self.lb_pane0.IsChecked(i):
                    val = self.lb_pane0.GetString(i)
                    newletters.append(str(val))
            self.prnt.chars['letters'] = newletters
            self.prnt.label_letters.SetLabel(" ".join(newletters))

            newnumbers = []
            for i in range(self.lb_pane1.GetCount()):
                if self.lb_pane0.IsChecked(i):
                    val = self.lb_pane1.GetString(i)
                    newnumbers.append(str(val))
            self.prnt.chars['numbers'] = newnumbers
            self.prnt.label_numbers.SetLabel(" ".join(newnumbers))

            newspecials = []
            for i in range(self.lb_pane2.GetCount()):
                if self.lb_pane2.IsChecked(i):
                    val = self.lb_pane2.GetString(i)
                    newspecials.append(str(val.encode('utf-8')))
            self.prnt.chars['specials'] = newspecials
            self.prnt.label_specials.SetLabel(" ".join(newspecials))

            mess = MyMiniFrame(self, "Message", wx.DefaultPosition, (200,60), wx.DEFAULT_FRAME_STYLE, "Modifications validées!", True)

