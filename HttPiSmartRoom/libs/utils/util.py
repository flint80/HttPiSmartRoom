'''
Created on Oct 21, 2015

@author: avramenko
'''
import os
import logging

logger = logging.getLogger('root')

def readTempFile(filename):
    fullPath = "temp/%s" % filename
    if not os.path.exists(fullPath):
        return None
    f = open(fullPath, 'r')
    try:
        return f.read()
    finally:
        f.close()

def writeTempFile(filename, content):
    fullPath = "temp/%s" % filename
    f = open(fullPath, 'w')
    try:
        f.write(content)
    finally:
        f.close()
def deleteTempFile(filename):
    fullPath = "temp/%s" % filename
    if not os.path.exists(fullPath):
        return None
    os.remove(fullPath)

def readConfig(filename):
    result = {}
    if not os.path.exists(filename):
        return result
    f = open(filename, 'r')
    try:
        for line in f.readlines():
            items = line.split('=',2)
            if len(items) == 2:
                result[items[0].strip()] = items[1].strip().replace("\eq","=")
        return result
    finally:
        f.close()