import requests
import json
from hashlib import md5
from random import randint

from palmyra import constant

#  This is the client api for Palmyra REST API
class PalmyraClient:
    # Constructor
    def __init__(self, url, context, user, password):
        self.url = url + "/" + context
        self.context = context
        self.username = user
        self.__password = md5(password.encode()).hexdigest()
    
    # Find the record by primary key
    def findById(self, id, type):
        """Returns single dict. """
        target = constant.URL_FIND_BYID.format(self.url, type, id)
        return self._get(target)

    # Find the records by Unique keys. if the table has multiple unique keys
    # it is quite possible to return multiple records.     
    def findByUniqueKey(self, key, value, type):
        """Returns List of dict. """
        data = {key : value}
        filter = {"criteria" : data}
        target = constant.URL_QUERY_UNIQUE.format(self.url, type)
        return self._post(target, filter)

    # Find unique record by given search criteria. If more than one records found 
    # error code 302 will be received. 
    def findUniqueByItem(self, data, type):
        # Returns single dict
        filter = {"criteria" : data}
        target = constant.URL_QUERY_UNIQUE.format(self.url, type)
        return self._post(target, filter)

    # find records matching the given criteria. 
    def queryByItem(self, data, type):
        # Returns with resultset format. 
        filter = {"criteria" : data}
        target = constant.URL_QUERY.format(self.url, type)
        print(target)
        return self._post(target, filter)

    # Returns the first dict  with the matching criteria
    def queryFirst(self, data, type):
        filter = {"criteria" : data}
        target = constant.URL_QUERY_FIRST.format(self.url, type)
        return self._post(target, filter)

    # Returns list of dict with the matching criteria.
    def listByItem(self, data, type):
        filter = {"criteria" : data}
        target = constant.URL_QUERY_LIST.format(self.url, type)
        return self._post(target, filter)

    # save or create a new record
    def save(self, data, type):
        target = constant.URL_SAVE.format(self.url, type)
        return self._post(target, data)

    # delete the given record.
    def delete (self, id, type):
        target = constant.URL_DELETE.format(self.url, type, id)
        return self._delete(target)

    def _delete(self,url):        
        headers = PalmyraAuthProvider.getAuthHeader(self.context, self.username, self.__password)        
        resp = requests.delete(url, headers=headers)
        return self._processCode(resp)

    def _post(self,url, data):
        str_data = json.dumps(data)
        print ("request body" + str_data)
        headers = PalmyraAuthProvider.getAuthHeader(self.context, self.username, self.__password)
        resp = requests.post(url, data = str_data, headers=headers)
        return self._processCode(resp)
        
    def _get(self,url):
        headers = PalmyraAuthProvider.getAuthHeader(self.context, self.username, self.__password)
        resp = requests.get(url, headers=headers)
        if(200 == resp.status_code):
            return resp.json()
        elif(404 == resp.status_code):
            return None
        else:
            return _processCode(resp)

    def _processCode(self,resp):
        if(200 == resp.status_code):
            return resp.json()        
        elif(204 == resp.status_code):
            return None
        raise PalmyraException(resp.status_code, resp.content)
        

class PalmyraAuthProvider:
    def getAuthHeader(context, username, password):
        headers = {'Content-Type' : 'application/json'}        
        random_number = str(randint(1, 1000))
        auth = username+"@"+context+":" + password + random_number
        authHeader = md5(auth.encode())
        headers[constant.HEADER_X_SECRET] = authHeader.hexdigest()
        headers[constant.HEADER_X_USER] = username
        headers[constant.HEADER_X_RANDOM] = random_number
        return headers

class PalmyraException(Exception):
    def __init__ (self, code, message):
        self.code = code
        self.message = message