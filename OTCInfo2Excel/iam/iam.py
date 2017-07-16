# -*- coding: cp936 -*-
'''
Created on 2017年7月5日

@author: c00265801
'''

class iam(object):
    '''
    classdocs
    '''
    
    conn = None
    def __init__(self, conn):
        '''
        Constructor
        '''
        self.conn = conn
        
    def list_endpoints(self):
        print('List endpoints')
        for endpoint in self.conn.compute.endpoints():
            print(endpoint)


                                