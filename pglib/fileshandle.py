#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Manipulation de fichiers
"""

import sys
import os

def getPath(path):
    '''Retourne le chemin absolu vers un fichier passé en argument
    '''
    return "%s%s" % (os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]))), path)


def loadJson(path):
    '''Retourne le contenu d'un fichier json
    '''
    from json import loads
    f = getPath(path)
    fo = open(f, 'r')
    fr = fo.read()
    datas = loads(fr)
    fo.close()
    return datas

