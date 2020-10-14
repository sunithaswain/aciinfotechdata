from couchbase import FMT_JSON

from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import json
import base64

from app.utility import vault_manager


class User(object):
    __documenttype__ = 'user'

    def __init__(self, config, username, password, role, usertype, first_name, last_name):
        self.cb = config.cb
        self.config = config
        self.TRUEVAULT_API_KEY = self.config.tv_api_key
        self.TV_URI = self.config.tv_uri
        self.TV_URI_LOGIN = self.config.tv_uri_login
        self.TV_ACCOUNT_ID = self.config.tv_account_id
        self.username = username
        self.password = password
        self.role = role
        self.usertype = usertype
        self.first_name = first_name
        self.last_name = last_name
        self.create_date = datetime.now().isoformat()
        self.update_date = datetime.now().isoformat()
        self.created_by = 'system'
        self.updated_by = 'system'
        self.type = 'user'

    def save_to_db(self):

        data = dict()

        data['type'] = self.type
        data['username'] = self.username
        data['password'] = self.password
        data['role'] = self.role
        data['usertype'] = self.usertype
        data['first_name'] = self.first_name
        data['last_name'] = self.last_name
        data['create_date'] = self.create_date
        data['update_date'] = self.update_date
        data['created_by'] = self.created_by
        data['updated_by'] = self.updated_by

        try:
            response = self.cb.insert(data['username'], data, format=FMT_JSON)
        except Exception as e:
            print(e)

    def find_by_username(self, username):

        response = {}
        try:
            response = self.cb.get(username, quiet=True)
        except Exception as e:
            print(e)
        return response.value

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def create_tvuser(self, cp_api_key, status):
        username = self.username
        password = self.password
        attributes = {}
        attributes['fliptapikey'] = cp_api_key
        attributes['usertype'] = self.usertype
        attributes['username'] = self.username
        attributes['password'] = self.password
        attributes['status'] = status
        attributes['create_date'] = self.create_date

        attributes = base64.b64encode(str.encode(json.dumps(attributes)))
        userdata = {'username': username,
                    'password': password, 'attributes': attributes}
        updateURI = self.TV_URI
        updateURI = str(updateURI)
        updateTVURI = updateURI[:updateURI.rfind('/')]
        r = requests.post(updateTVURI,
                          auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''), data=userdata)
        if r.status_code == 400 or r.status_code == 404:
            return
        tvresponse = r.json()
        return tvresponse

    def read_tvuser(self, userid):

        data = {'full': True}
        updateURI = self.TV_URI
        updateURI = str(updateURI)
        updateTVURI = updateURI[:updateURI.rfind('/')]+'/'+str(userid)
        updateTVURI = updateTVURI.replace("/v1/","/v2/")
        r = requests.get(updateTVURI,
                         auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''), data=data)
        return r.json()

    def search_tvuser(self, search_option):

        search_opt = base64.b64encode(str.encode(json.dumps(search_option)))
        data = {'search_option': search_opt}
        '''
        print(f"printing the data in search option {data}")
        print(f"printing the tv uri in search option {self.TV_URI}")
        print(f"printing the tv api key in search option {self.TRUEVAULT_API_KEY}")
        print(f"printing the api key of erx in search option {data}")
        '''
        session = vault_manager.VaultSession().session
        r = session.post(self.TV_URI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''), data=data)
        response = r.json()

        if 'data' not in response:
            return None, None
        #print(f"print the json resposne {response}")
        if len(response['data']['documents']) == 0 and r.status_code == 200:
            return None, None
        att = json.loads(str(base64.b64decode(
            response['data']['documents'][0]['attributes']), 'utf-8'))
        #print(f"print ")
        userid = response['data']['documents'][0]['user_id']

        return att, userid
    
    def login_tvuser(self,username,password,isaccountid):
        
        useraccountid = None
        userattributes = None
        userid = None
        if isaccountid == 'N':
            search_option = {'full_document':True,'filter':{'$tv.username':{'type':'eq','value':username,'case_sensitive':False}},'filter_type':'and'}
            search_opt = base64.b64encode(str.encode(json.dumps(search_option)))
            data = {'search_option': search_opt}
                
            r = requests.post(self.TV_URI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''), data=data)
            searchresponse = r.json()
            
            if 'data' not in searchresponse:
                userattributes = None
            
            elif len(searchresponse['data']['documents']) == 0 and r.status_code == 200:
                userattributes = None
            else:
                totalrecords = searchresponse['data']['info']['total_result_count']
                for j in range(0,totalrecords): 
                    accatt = json.loads(base64.b64decode(searchresponse['data']['documents'][j]['attributes']).decode('utf-8'))
                    if "claim_portal_access" in accatt.keys():
                        userattributes = accatt
                        userid = searchresponse['data']['documents'][0]['user_id']
                        readresponse = self.read_tvuser(userid)
                        if readresponse["result"] == 'success':
                            useraccountid = readresponse["users"][0]["account_id"]
                        break
            if useraccountid is None:
                useraccountid = self.TV_ACCOUNT_ID
        
        else:
            useraccountid = self.TV_ACCOUNT_ID
        
        reqdata = {
            'username': username,
            'password': password,
            'account_id': useraccountid
        }

        loginresponse = requests.post(self.TV_URI_LOGIN, data=reqdata)
        response = loginresponse.json()

        
        if response["result"] == "success":

            if userattributes is None:
                soption = {'full_document':True,'filter':{'$tv.username':{'type':'eq','value':username,'case_sensitive':False}},'filter_type':'and'}
                sopt = base64.b64encode(str.encode(json.dumps(soption)))
                sdata = {'search_option': sopt}
            
                sr = requests.post(self.TV_URI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''), data=sdata)
                sresponse = sr.json()

                if 'data' not in sresponse:
                    userattributes = None
                
                elif len(sresponse['data']['documents']) == 0 and sr.status_code == 200:
                    userattributes = None
                else:
                    tot_records = sresponse['data']['info']['total_result_count']
                    for i in range(0,tot_records): 
                        att = json.loads(base64.b64decode(sresponse['data']['documents'][i]['attributes']).decode('utf-8'))
                        if "claim_portal_access" in att.keys():
                            userattributes = att
                            break
                        
            return response,userattributes
        else:
            response["error"]["userid"] = userid
            response["error"]["accountid"] = useraccountid
            response["error"]["apikey"] = self.TRUEVAULT_API_KEY
            return response,None
        
    def logout_tvuser(self,accesstoken):

        updateURI = self.TV_URI_LOGIN
        updateURI = str(updateURI)
        updateTVURI = updateURI[:updateURI.rfind('/')]+'/'+'logout'
        
        logoutresponse = requests.post(updateTVURI, auth=HTTPBasicAuth(accesstoken, ''))
        response = logoutresponse.json()
        return response

    def get_tvuserschema(self):
    
        acc_id = self.TV_ACCOUNT_ID
        r=requests.get('https://api.truevault.com/v1/accounts/%s/user_schema' % acc_id,auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''))
        return r.json()	
    
    def update_tvuserschema(self,dataschema):

        if "tvurl" in dataschema:
            tvurl = dataschema["tvurl"]
        else:
            tvurl = 'https://api.truevault.com/v1/accounts/%s/user_schema'
        
        if "tvaccountid" in dataschema:
            tvaccountid = dataschema["tvaccountid"]
        else:
            tvaccountid = self.TV_ACCOUNT_ID
        
        if "tvapikey" in dataschema:
            tvapikey = dataschema["tvapikey"]
        else:
            tvapikey = self.TRUEVAULT_API_KEY
        
        if "newindexname" in dataschema:
            newindexname = dataschema["newindexname"]
        else:
            newindexname = "fliptapikey"

        acc_id = tvaccountid 
        r=requests.get(tvurl % acc_id,auth=HTTPBasicAuth(tvapikey, ''))
        
        olduserschema = r.json()
        olduserschema = olduserschema["user_schema"]["fields"]
        
        userschema = {"name":"userschema"}
        indexaddition = {
                "index": 1,
                "name": newindexname,
                "type": "string"
            }
        
        indexAvailable = False
        for i in range(0,len(olduserschema)):
            if olduserschema[i]["name"] == newindexname:
                indexAvailable = True
        
        if not indexAvailable:
            olduserschema.append(indexaddition)

        userschema["fields"] = olduserschema
    
        uschema = base64.b64encode(str.encode(json.dumps(userschema)))
        data = {'schema':uschema}
        updateres=requests.put(tvurl % acc_id,auth=HTTPBasicAuth(tvapikey, ''),data=data)
        return updateres.json()
