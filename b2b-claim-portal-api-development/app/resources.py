from flask_restful import Resource, reqparse
from app.models.user import User
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity, get_raw_jwt)
from flask_jwt_extended.view_decorators import _decode_jwt_from_request
from functools import wraps
from flask_jwt_extended.exceptions import NoAuthorizationError
import uuid
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
parser = reqparse.RequestParser(bundle_errors=True)

ACCESS = {
    'none':0,
    'readonly':1,
    'admin':2
}

def basicauthrequired(_apifunction=None, utype='none'):
    def decoratorbasicuser(apifunction):
        @wraps(apifunction)
        def wrapper(*args, **kwargs):
            isUserAuthorized = False
            search_option = {'full_document':True,'filter':{'fliptapikey':{'type':'eq','value':auth.username(),'case_sensitive':False}},'filter_type':'and'}
            userattribute,userid = OptionalModules.user().search_tvuser(search_option)
            if userid == None:
                isUserAuthorized = False
            else:
                isUserAuthorized = True
            
            if not isUserAuthorized:
                raise NoAuthorizationError("You are not authorized user to access the API")
            
            if not userattribute['status'] == 'Active':
                raise NoAuthorizationError("Your account is Inactive")
            
            return apifunction(userattribute)

        return auth.login_required(wrapper)
    if _apifunction is None:
        return decoratorbasicuser
    else:
        return decoratorbasicuser(_apifunction)


@auth.verify_password
def verify_apikeytoken(username,password):
    return True


def jwtrequiredrole(_apifunction=None, urole='none'):
    def decoratoruserrole(apifunction):
        @wraps(apifunction)
        def wrapper(*args, **kwargs):
            jwt_data = _decode_jwt_from_request(request_type='access')
            
            if ACCESS[jwt_data["identity"][1]] >= ACCESS[urole]:
                isRoleAuthorized = True
            else:
                isRoleAuthorized = False

            if not isRoleAuthorized:
                raise NoAuthorizationError("You are not authorized user to access the API")
            
            return apifunction(*args, **kwargs)

        return jwt_required(wrapper)
    if _apifunction is None:
        return decoratoruserrole
    else:
        return decoratoruserrole(_apifunction)



class UserRegistration(Resource):

    @jwtrequiredrole(urole='admin')
    def post(self):
        parser.add_argument('username', help = 'The username is mandatory', required = True, trim = True)
        parser.add_argument('password', help = 'The password is mandatory', required = True, trim = True)
        parser.add_argument('role', help = 'The role is mandatory and it will be [readonly,admin,none]', required = True, choices = ('readonly','admin','none'), default = 'readonly', trim = True, store_missing = True)
        parser.add_argument('usertype', help = 'The usertype is mandatory', required = True, trim = True)
        parser.add_argument('firstname', help = 'The firstname is mandatory', required = True, trim = True)
        parser.add_argument('lastname', required = False, trim = True, default = '')

        data = parser.parse_args()
        
        if data['username'] == '':
            return {'message':{
                'username':'The Username cannot be empty'
                }
            }
        
        if data['password'] == '':
            return {'message':{
                'password':'The Password cannot be empty'
                }
            }
        
        if data['firstname'] == '':
            return {'message':{
                'firstname':'The Firstname cannot be empty'
                }
            }

        if OptionalModules.user().find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}
        
        new_user = OptionalModules.user(
            username = data['username'],
            password = User.generate_hash(data['password']),
            role = data['role'],
            usertype = data['usertype'],
            first_name = data['firstname'],
            last_name = data['lastname']
        )
        
        try:
            new_user.save_to_db()
            return {
                'message': 'User {} was created'.format(data['username'])
            }
            
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        parser.add_argument('username', help = 'The username is mandatory', required = True)
        parser.add_argument('password', help = 'The password is mandatory', required = True)
        parser.add_argument('isAccountID')

        data = parser.parse_args()
        if data['username'] == '':
            return {'message':'The Username cannot be empty'}
        
        if data['password'] == '':
            return {'message':'The Password cannot be empty'}
        tokenuser,roleuser = OptionalModules.user().login_tvuser(data['username'],data['password'],data['isAccountID'])
        
        if tokenuser["result"] == 'error':
            return tokenuser["error"]
        
        if not roleuser:
            return {'message': 'Something went wrong or there is no user'}
        
        if "claim_portal_access" in roleuser.keys():

            # access_token = tokenuser["user"]["access_token"] # create_access_token(identity = [data['username'],current_user['role']])
            access_token = create_access_token(identity = [tokenuser["user"]["access_token"]])
            return {
                'message': 'Logged in as {}'.format(data['username']),
                'access_token': access_token,
                'claim_portal_access':roleuser["claim_portal_access"]
                }
        else:
            return {'message': 'User {} doesnot have enough domain role '.format(data['username'])}
        
class UserLogout(Resource):
    def post(self):
        jwt_data = _decode_jwt_from_request(request_type='access')
        userresult = OptionalModules.user().logout_tvuser(jwt_data["identity"][0])
        if userresult["result"] == 'success':
            return {'message':'User logout is success','result':'success'}
        else:
            return userresult
        
class AllUsers(Resource):
    def get(self):
        return User.return_all()
    
    def delete(self):
        return User.delete_all()

class TVUserRegistration(Resource):

    def post(self):
        parser.add_argument('username', help = 'The username is mandatory', required = True, trim = True)
        parser.add_argument('password', help = 'The password is mandatory', required = True, trim = True)
        parser.add_argument('usertype', help = 'The usertype is mandatory', required = True, trim = True)
        parser.add_argument('status', help = 'The status is mandatory', required = True, trim = True)


        data = parser.parse_args()
        
        if data['username'] == '':
            return {'message':{
                'username':'The Username cannot be empty'
                }
            }
        
        if data['password'] == '':
            return {'message':{
                'password':'The Password cannot be empty'
                }
            }
        
        if data['usertype'] == '':
            return {'message':{
                'usertype':'The User Type cannot be empty'
                }
            }
        
        if data['status'] == '':
            return {'message':{
                'status':'The Status cannot be empty'
                }
            }
        
        

        search_option = {'full_document':True,'filter':{'$tv.username':{'type':'eq','value':data['username'],'case_sensitive':False}},'filter_type':'and'}
        
        att,userid = OptionalModules.user().search_tvuser(search_option)
        if userid == None:
            newtvuser = OptionalModules.user(
                username = data['username'],
                password = data['password'],
                usertype = data['usertype']
            )
            
            try:
                cp_api_key = str(uuid.uuid4())
                tvuserresponse = newtvuser.create_tvuser(cp_api_key,data['status'])
                # return tvuserresponse
                return {
                    'message': 'User {} was created'.format(data['username']),
                    'cp_api_key': cp_api_key
                }
            
            except:
                return {'message': 'Something went wrong'}, 500

        else:
            return {'message': 'User {} already exists'.format(data['username'])}
        
class TVUserDetail(Resource):

    def post(self):
        parser.add_argument('username', help = 'The username is mandatory', required = True)
        parser.add_argument('password', help = 'The password is mandatory', required = True)
        data = parser.parse_args()
        if data['username'] == '':
            return {'message':{
                'username':'The Username cannot be empty'
                }
            }
        
        if data['password'] == '':
            return {'message':{
                'password':'The Password cannot be empty'
                }
            }
        
        search_option = {'full_document':True,'filter':{'$tv.username':{'type':'eq','value':data['username'],'case_sensitive':False}},'filter_type':'and'}
        att,userid = OptionalModules.user().search_tvuser(search_option)
        if userid == None:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        else:
    
            tvuserresponse = OptionalModules.user().read_tvuser(userid)
            return tvuserresponse

class TVUserSchemaUpdate(Resource):
    def get(self):
        result = OptionalModules.user().get_tvuserschema()
        return result
    
    def put(self):
        parser.add_argument('tvurl')
        parser.add_argument('tvaccountid')
        parser.add_argument('tvapikey')
        parser.add_argument('newindexname')
        data = parser.parse_args()
        
        result = OptionalModules.user().update_tvuserschema(data)
        return result
