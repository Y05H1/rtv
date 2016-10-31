# -*- coding: utf-8 -*-
 
import requests
import json
 
"""
/usr/lib/python2.6/site-packages/requests/packages/urllib3/connectionpool.py:734: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.org/en/latest/security.html  InsecureRequestWarning)
"""
requests.packages.urllib3.disable_warnings()

class RestClient(object):
  
  def __init__(self, api_key, host):
    self.api_key = api_key
    self.host = host
    self.url = ''
    self.path = ''
    self.data = {}
    self.headers  = {
      'Content-Type': 'application/json',
      'X-Redmine-API-Key': self.api_key
    }
  
  def post(self, path, data=''):
    self.data = data
    self.url = self.host + path
    return requests.post(self.url, headers=self.headers, verify=False, data=self.data)
  
  def get(self, path, data=''):
    self.data = data
    self.url = self.host + path
    return requests.get(self.url, headers=self.headers, verify=False, data=self.data)
  
  def put(self, path, data=''):
    self.data = data
    self.url = self.host + path
    return requests.put(self.url, headers=self.headers, verify=False, data=self.data)
 
  def delete(self, path, data=''):
    self.data = data
    self.url = self.host + path
    return requests.delete(self.url, headers=self.headers, verify=False, data=self.data)
  
