import logging
from datetime import datetime, timedelta
from app import resources
from app.resources import basicauthrequired
from app.utility.bootstrap import Configs
from app.utility.bootstrap import Service
from ddtrace import patch_all
from flask import jsonify
from flask import request, Flask, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from flask_restful import Api

patch_all(logging=True)


app = Flask(__name__)

log = logging.getLogger(__name__)

FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

#FORMAT = ('- %(message)s')

logging.basicConfig(format=FORMAT, level=logging.DEBUG)

api = Api(app)
cportal = Service.portal_service()
CORS(app)
cf = Configs.config()

app.config['SECRET_KEY'] = cf.secret_key
app.config['JWT_SECRET_KEY'] = cf.jwt_secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['PROPAGATE_EXCEPTIONS'] = True
jwt = JWTManager(app)

api.add_resource(resources.UserRegistration, '/api/v1/user/registration')
api.add_resource(resources.UserLogin, '/api/v1/user/login')
api.add_resource(resources.UserLogout, '/api/v1/user/logout')
api.add_resource(resources.TVUserRegistration, '/api/v1/tvuser/registration')
api.add_resource(resources.TVUserDetail, '/api/v1/tvuser/detail')
api.add_resource(resources.TVUserSchemaUpdate, '/api/v1/tvuser/schema')


@app.route('/home', methods=['GET'])
def testfunc():
    print("hi")
    return "Test"

@app.route('/api/v1/Auth', methods=['GET'])
# @basicauthrequired(utype='eRx')
def try_auth(userattribute):
    # print(userattribute)
    return "Welcome to FLipt, You are Authenticated"


@app.route('/api/v1/test', methods=['GET'])
# @basicauthrequired()
def try_get():
    log.debug("This will be traced by data-dog")
    return "Welcome to Flipt, API is up and Running"

@app.route('/api/v1/claim/search', methods=['POST'])
# @jwt_required
def getclaim():
    global cportal
    log.debug("Received the claim filter and processing to search the claim")

    responsestring = cportal.getClaim(request.args)
    return jsonify(responsestring), 200


@app.route('/api/v1/claim/detail', methods=['GET'])
# @jwt_required
def getclaimdetails():
    global cportal
    log.debug(
        "Received the claim detaiil request and processing to search the claim details")

    responsestring = cportal.getClaimDetails(request.args)
    return jsonify(responsestring), 200


@app.route('/api/v1/claim/override', methods=['GET'])
# @jwt_required
def getclaimoverride():
    global cportal
    log.debug(
        "Received the claim override request and processing to return the claim override")

    responsestring = cportal.getClaimOverride(request.args)
    return jsonify(responsestring), 200


@app.route('/api/v1/claim/override', methods=['PUT'])
# @jwt_required
def updateclaimoverride():
    global cportal
    log.debug(
        "Received the claim override request and processing to update the claim override")

    responsestring = cportal.updateClaimOverride(request.data)
    return jsonify(responsestring), 200


@app.route('/api/v1/claim/member', methods=['GET'])
# @jwt_required
def getclaimmember():
    global cportal
    log.debug(
        "Received the claim member request and processing to return the claim member")

    responsestring = cportal.getClaimMember(request.args)
    return jsonify(responsestring), 200


@app.route('/api/v1/claim/transaction', methods=['GET'])
# @jwt_required
def getclaimtransaction():
    global cportal
    log.debug(
        "Received the claim transaction request and processing to return the claim transaction")

    responsestring = cportal.getClaimTransaction(request.args)
    return jsonify(responsestring), 200


@app.route('/api/v1/eligibility/search', methods=['GET'])
# @jwt_required
def geteligibility():
    global cportal
    log.debug(
        "Received the eligibility member request for search and processing to return the eligibility member")

    responsestring = cportal.getEligibilityReport(request.args)
    return jsonify(responsestring), 200


@app.route('/api/v1/eligibility/member', methods=['GET'])
# @jwt_required
def geteligibilitymember():
    global cportal
    log.debug(
        "Received the eligibility member request and processing to return the eligibility member")

    responsestring = cportal.getEligibilityMember(request.args)
    return jsonify(responsestring), 200


@app.route('/api/v1/eligibility/member', methods=['PUT'])
# @jwt_required
def updateeligibilitymember():
    global cportal
    log.debug(
        "Received the eligibility member request and processing to update the eligibility member")

    responsestring = cportal.updateEligibilityMember(request.data)
    return jsonify(responsestring), 200



if __name__ == '__main__':
    # logging.basicConfig(handlers=[Utilities.emailnotif()], level=int(
    #     cf.LEVEL), format='%(threadName)s:%(levelname)s:%(asctime)s:%(name)s:%(funcName)s:%(message)s', datefmt='%d-%m-%y %H:%M:%S')
    app.run(port=5010, host='0.0.0.0', use_reloader=False,
            threaded=False, debug=True)
