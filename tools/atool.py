# -*- coding: utf-8 -*-
'''
Created on 2016. jún. 29.

@author: padanyigulyasgergely
'''
import os
import sys


class Atool(object):

    # initialization
    def __init__(self):
        # colors for stdout
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'
    
    # general exception handler, prints out the error 
    # and the appropriate line number of the appropriate file
    def handle_exception(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        self.print_colors('Some error occured', self.FAIL)
        print(exc_type, fname, exc_tb.tb_lineno)

    # general string file reader
    def read_file_content(self, filename):
        try:
            with open(filename, 'r') as file:
                data = file.read().replace('\n', '')
                return data
        except Exception, e:
            self.handle_exception(e)

    # colorful stdout printer
    def print_colors(self, text, color):
        print color + text + self.ENDC
    