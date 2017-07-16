# -*- coding: cp936 -*-
'''
Created on 2017年6月26日

@author: c00265801
'''
from openstack import connection

import requests
import json

class login(object):
    '''
    classdocs
    '''
    conn = None
    token_info = {}
    token = ''

    def __init__(self, params):
        '''
        Constructor
        '''
       
    def create_connection(self,auth_url, region, project_name, username, password, user_domain_name):
        auth_args = {
            'auth_url': auth_url,
            'project_name': project_name,
            'username': username,
            'password': password,
            "region": region,
            "user_domain_name":user_domain_name
        }
        
        self.conn = connection.Connection(**auth_args)
        return self.conn    
    
    def create_connection_login(self,auth_url, region, project_name, username, password, user_domain_name):
   
        body_text = """
        {"auth": 
            {"identity": 
                {"methods": ["password"],
                  "password": 
                      {"user": 
                          {"name": "%s",
                            "password": "%s",
                            "domain": 
                                {"name": "%s"}
                            }
                        }
                    },
                    "scope": {
                        "project": {
                            "domain": {
                            "name": "%s"
                            },
                        "name": "%s"
                        }
                    }}}}
          """ %(username, password, user_domain_name,  user_domain_name, project_name)
        #print(body_text) 
        r = requests.post (auth_url+"/auth/tokens", data = body_text)    
        
        #print (r.status_code)
        #print (r.text)
        #print (r.headers) 
        
        #print (r.headers['x-subject-token'])
        
        
        self.token = r.headers['x-subject-token']
        
        self.tokeninfo = json.loads(r.text)

        return  self.token
    
    def get_project_id(self):
        return self.tokeninfo['token']['project']['id']   
    
    def get_token(self):
        return self.token
    
    def get_conn(self):
        return self.conn