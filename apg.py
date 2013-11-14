#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from time import sleep
from random import randint as rdi
from threading import Thread

import wx

from pglib import fileshandle as fiha
from pglib import pgutils as pgut


class PwdGen(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        ### Quelques variables ###

        edit_bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_OTHER, (20,20))
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (20,20))
        copy_bmp = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_OTHER, (20,20))

        self.chars = fiha.loadJson("/pglib/charsets.json")

        self.pattern_setperso = re.compile(r'^([^\s]\s){1,}$')

        self.hidepwd = False

        self.persoslist = []

        self.messalive = False

        ### Interface, UI ###
        ##
        #
        #Lettres
        self.checkbox_letters = wx.CheckBox(self, -1, "Lettres", style=wx.ALIGN_RIGHT)
        self.label_letters = wx.StaticText(self, -1, " ".join(self.chars['letters']))
        self.button_letters = wx.BitmapButton(self, -1, edit_bmp)

        #Nombres
        self.checkbox_numbers = wx.CheckBox(self, -1, "numbers", style=wx.ALIGN_RIGHT)
        self.label_numbers = wx.StaticText(self, -1, " ".join(self.chars['numbers']))
        self.button_numbers = wx.BitmapButton(self, -1, edit_bmp)

        #SpeChars
        self.checkbox_specialchars = wx.CheckBox(self, -1, "Caractères spéciaux", style=wx.ALIGN_RIGHT)
        self.label_specials = wx.StaticText(self, -1, " ".join(self.chars['specials']))
        self.button_specialchars = wx.BitmapButton(self, -1, edit_bmp)

        #Perso
        self.checkbox_setperso = wx.CheckBox(self, -1, "Sets personnalisés", style=wx.ALIGN_RIGHT)
        self.combobox_setperso = wx.ComboBox(self, -1, choices=[], style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)

        self.sizer_charsets_staticbox = wx.StaticBox(self, -1, "Jeux")

        #Casse
        radiocasse = ["Majuscules et minuscules", "Minuscules uniquement", "Majuscules uniquement"]
        self.rbcasse = wx.RadioBox(self, -1, "", wx.DefaultPosition, wx.DefaultSize, radiocasse, 3, wx.RA_SPECIFY_COLS|wx.NO_BORDER)
        #self.radio_majuscules = wx.RadioButton(self, -1, "Majuscules uniquement")
        #self.radio_minuscules = wx.RadioButton(self, -1, "Minuscules uniquement")
        #self.radio_majmin = wx.RadioButton(self, -1, "Majuscules et minuscules")
        self.sizer_casse_staticbox = wx.StaticBox(self, -1, "Casse")

        #Nombres de caractères du mot de passe
        self.label_nbchars = wx.StaticText(self, -1, "De 0 à 100 (mettez à 0 pour le choix par défaut: 8)")
        self.spin_nbchars = wx.SpinCtrl(self, -1, "8", min=0, max=100)
        self.sizer_nbchars_staticbox = wx.StaticBox(self, -1, "Nombre de caractères")

        #Validation du formulaire
        self.static_line = wx.StaticLine(self, -1)
        self.button_quit = wx.Button(self, -1, "Quitter")
        self.button_reset = wx.Button(self, -1, "Réinitialiser")
        self.button_submit = wx.Button(self, -1, "Générer")
        self.checkbox_hidepwd = wx.CheckBox(self, -1, "Masquer")
        self.combobox_newpwd = wx.ComboBox(self, -1, choices=[], style=wx.CB_DROPDOWN)
        self.button_copypwd = wx.BitmapButton(self, -1, copy_bmp)

        ### Bindings ###
        ##
        #
        # Edition liste des lettres, nombres, spéciaux, et perso
        self.Bind(wx.EVT_BUTTON, self.editLetters, self.button_letters)
        self.Bind(wx.EVT_BUTTON, self.editNumbers, self.button_numbers)
        self.Bind(wx.EVT_BUTTON, self.editSpecials, self.button_specialchars)

        # Evénement touche entrée dans le comboxbox "set personnalisé"
        self.Bind(wx.EVT_TEXT_ENTER, self.editSetperso, self.combobox_setperso)

        # Validation
        self.Bind(wx.EVT_BUTTON, self.closeApp, self.button_quit)
        self.Bind(wx.EVT_BUTTON, self.resetApp, self.button_reset)
        self.Bind(wx.EVT_BUTTON, self.genPwd, self.button_submit)
        self.Bind(wx.EVT_CHECKBOX, self.hidePwd, self.checkbox_hidepwd)
        self.Bind(wx.EVT_BUTTON, self.copyPwd, self.button_copypwd)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("PwdGen")
        self.checkbox_letters.SetValue(1)
        self.checkbox_numbers.SetValue(1)
        self.checkbox_specialchars.SetValue(1)

        size_chkb = (170, 25)
        self.checkbox_letters.SetMinSize(size_chkb)
        self.checkbox_numbers.SetMinSize(size_chkb)
        self.checkbox_specialchars.SetMinSize(size_chkb)
        self.checkbox_setperso.SetMinSize(size_chkb)

        str_tooltip_chars = "Editer la liste de caractère"
        self.checkbox_letters.SetToolTipString(str_tooltip_chars)
        self.checkbox_numbers.SetToolTipString(str_tooltip_chars)
        self.checkbox_specialchars.SetToolTipString(str_tooltip_chars)

        self.combobox_setperso.SetMinSize((477, 31))
        self.label_nbchars.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

    def __do_layout(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_validation = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_nbchars_staticbox.Lower()
        sizer_nbchars = wx.StaticBoxSizer(self.sizer_nbchars_staticbox, wx.HORIZONTAL)
        self.sizer_casse_staticbox.Lower()
        sizer_casse = wx.StaticBoxSizer(self.sizer_casse_staticbox, wx.HORIZONTAL)
        self.sizer_charsets_staticbox.Lower()
        sizer_charsets = wx.StaticBoxSizer(self.sizer_charsets_staticbox, wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_specialchars = wx.BoxSizer(wx.HORIZONTAL)
        sizer_numbers = wx.BoxSizer(wx.HORIZONTAL)
        sizer_letters = wx.BoxSizer(wx.HORIZONTAL)
        sizer_letters.Add(self.checkbox_letters, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_letters.Add(self.label_letters, 1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_letters.Add(self.button_letters, 0, wx.ADJUST_MINSIZE, 0)
        sizer_charsets.Add(sizer_letters, 1, wx.EXPAND, 0)
        sizer_numbers.Add(self.checkbox_numbers, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_numbers.Add(self.label_numbers, 1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_numbers.Add(self.button_numbers, 0, wx.ADJUST_MINSIZE, 0)
        sizer_charsets.Add(sizer_numbers, 1, wx.EXPAND, 0)
        sizer_specialchars.Add(self.checkbox_specialchars, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_specialchars.Add(self.label_specials, 1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_specialchars.Add(self.button_specialchars, 0, wx.ADJUST_MINSIZE, 0)
        sizer_charsets.Add(sizer_specialchars, 1, wx.EXPAND, 0)
        sizer_2.Add(self.checkbox_setperso, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(self.combobox_setperso, 1, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE, 5)
        sizer_charsets.Add(sizer_2, 1, wx.EXPAND, 0)
        sizer_main.Add(sizer_charsets, 0, wx.ALL|wx.EXPAND, 5)
        sizer_casse.Add(self.rbcasse, 0, wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_casse, 0, wx.ALL|wx.EXPAND, 5)
        sizer_nbchars.Add(self.spin_nbchars, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        sizer_nbchars.Add(self.label_nbchars, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_main.Add(sizer_nbchars, 0, wx.ALL|wx.EXPAND, 5)
        sizer_main.Add(self.static_line, 0, wx.ALL|wx.EXPAND, 5)
        sizer_validation.Add(self.button_quit, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 5)
        sizer_validation.Add(self.button_reset, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 5)
        sizer_validation.Add(self.button_submit, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        sizer_validation.Add(self.checkbox_hidepwd, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_validation.Add(self.combobox_newpwd, 1, wx.ADJUST_MINSIZE, 0)
        sizer_validation.Add(self.button_copypwd, 0, wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_validation, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer_main)
        sizer_main.Fit(self)
        self.Layout()
        self.Centre()

    ###########################
    ###       METHODS       ###
    ###########################

    ### Edition des listes de caractères
    ##
    #
    # EDIT LETTRES
    def editLetters(self, e):
        edset = pgut.CharsCheckList(self, 0)
    # EDIT NUMBERS
    def editNumbers(self, e):
        edset = pgut.CharsCheckList(self, 1)
    # EDIT SPECIAL
    def editSpecials(self, e):
        edset = pgut.CharsCheckList(self, 2)

    # SETPERSO
    def editSetperso(self, e):
        x = self.combobox_setperso.GetValue()
        self.combobox_setperso.Append(x)
        self.combobox_setperso.SetValue("")
        self.persoslist.append(x)

    # Evénement checkbox nombre max
    def nbmaxCheckboxEvent(self, e):
        state = e.IsChecked()
        if  state == 1:
            self.spin_maxnbchars.Enable(True)
        else:
            self.spin_maxnbchars.Enable(False)

    # Evénement spinctrl nombre max
    def nbmaxSpin(self, e):
        spinminvalue = self.spin_nbchars.GetValue()
        spinmaxvalue = self.spin_maxnbchars.GetValue()

        if spinmaxvalue <= spinmaxvalue:
            self.spin_nbchars.SetValue(spinmaxvalue)

    ### Validation du formulaire
    ##
    #
    # Quitter
    def closeApp(self, e):
        self.Close()

    # Réinitialiser
    def resetApp(self, e):
        '''Pas sûr de cette méthode...
        Rafraîchrir l'application en la fermant et en la relançant (enfin pas dans cet ordre là, d'abord on la masque, on relance une autre instance, et on ferme la première) me paraît rupestre! ><
        Je ne sais pas comment procéder...

        Sinon une autre solution serait de traiter tous les champs du formulaire un  à un....
        En attendant, on va la neutraliser.
        '''
        dlg = wx.MessageDialog(self, "L'application va être fermer et relancée! Toute modification non enregistrée sera perdue. Confirmez le choix, OK pour valider.", "Recharger l'application", wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_OK:
            #self.Hide()
            #from subprocess import Popen
            # NOWAIT
            #pid = Popen([fiha.getPath('/pwdgen_ui.py')]).pid
            #self.Close()
            print("Pas encore implémenté")
            pass
        dlg.Destroy()

    def genPwd(self, e):
        dlg = None
        finalset = []
        setL = self.checkbox_letters.GetValue()
        setN = self.checkbox_numbers.GetValue()
        setSC = self.checkbox_specialchars.GetValue()
        setSP = self.checkbox_setperso.GetValue()

        def setCasse():
            aa = rdi(4, 16)
            bb = aa % 2
            if bb != 0:
                return 1
            else:
                return 0

        i = False

        if setL == 1:
            finalset += self.chars['letters']
            i = True
        if setN == 1:
            finalset += self.chars['numbers']
            i = True
        if setSC == 1:
            finalset += self.chars['specials']
            i = True
        if setSP == 1:
            tmp = self.combobox_setperso.GetValue().strip() + " "
            x = re.search(self.pattern_setperso, tmp)
            if x is not None:
                tmp.strip()
                finalset += tmp.split(' ')
                i = True
            else:
                dlg = wx.MessageDialog(self, "La chaîne de caractère semble mal formée. Tous les caractères doivent être séparés par un espace.\nExemple:\n\na b c = OK\na bb c = Not OK", "Recharger l'application", wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

        if i:
            chars_array_length = len(finalset)
            array_count = chars_array_length - 1

            newpwd = ''
            y = 0

            default_size = 8
            spin_size = self.spin_nbchars.GetValue()
            if spin_size > 0:
                default_size = spin_size

            tmpcasse = ''
            for i in range(default_size):
                y = rdi(0, array_count)
                z = self.rbcasse.GetSelection()

                tmpcasse = finalset[y].encode('utf-8')

                if z == 0:
                    cc = setCasse()
                    if cc == 1:
                        tmpcasse = tmpcasse.upper()
                elif z == 2:
                    tmpcasse = tmpcasse.upper()


                newpwd += tmpcasse

            self.combobox_newpwd.Append(str(newpwd))
            self.combobox_newpwd.SetStringSelection(str(newpwd))
        else:
            dlg = wx.MessageDialog(self, "Aucun jeux de caractère n'a été sélectionné. Vous devez en choisir au moins un", "Erreur", wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def hidePwd(self, e):
        if self.hidepwd:
            self.hidepwd = False
            self.combobox_newpwd.Show()
        else:
            self.hidepwd = True
            self.combobox_newpwd.Hide()

    def enableCopyBut(self, i):
        while True:
            sleep(0.25)
            if self.messalive is not True:
                break
        self.button_copypwd.Enable(True)

    def copyOk(self):
        self.enabbut = Thread(target=self.enableCopyBut, args=(0,))
        mess = pgut.MyMiniFrame(self, "Message", wx.DefaultPosition, (200,60), wx.DEFAULT_FRAME_STYLE, "Mot de passe copié!", True)
        self.enabbut.start()

    def copyPwd(self, e):
        if self.combobox_newpwd.GetValue() == "":
            dlg = wx.MessageDialog(self, "Il n'y a rien à copier, le chant est vide...", "Erreur", wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            if wx.TheClipboard.Open():
                self.button_copypwd.Enable(False)
                wx.TheClipboard.SetData(wx.TextDataObject(self.combobox_newpwd.GetValue()))
                wx.TheClipboard.Close()
                wx.CallAfter(self.copyOk)


def main():
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    pwdgen_mainframe = PwdGen(None, -1, "")
    app.SetTopWindow(pwdgen_mainframe)
    pwdgen_mainframe.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
