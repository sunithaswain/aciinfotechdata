from couchbase.n1ql import N1QLQuery
from autologging import logged, traced
import couchbase.subdocument as SD
import json
import base64
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import pytz, pdb, logging
from ddtrace import patch_all
patch_all(logging=True)
log = logging.getLogger(__name__)
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

@logged
class ClaimPortalProvider(object):

    def __init__(self, config):
        self.config = config
        self.cb = self.config.cb
        self.instance_type = self.config.CB_INSTANCE
        self.TRUEVAULT_API_KEY = self.config.tv_api_key
        self.URI = self.config.tv_uri

    def getClaims(self, attribute_value):

        count = 0
        totalreccount = 0

        result = {"total": 0, "count": 0, "result": []}

        basequery = 'Select a1.auth_id, a1.sequenceNumber, a1.startDate, a1.endDate, a1.claim_response.transaction_response_status as response_status, a1.claim_transfer_response.transaction_response_status,a1.claim_request.product_id, a1.claim_request.group_id, a1.claim_request.cardholder_id, a1.claim_request.person_code, a1.claim_request.relationship_code, a1.claim_request.transaction_code, b1.drug_name from `' + \
            self.instance_type+'` a1 LEFT JOIN `'+self.instance_type + \
                '` b1 ON b1.type = "ndc_drugs" AND a1.claim_request.product_id = b1.ndc where a1.type="claim" and a1.auth_id <>""'
        basequery1 = basequery
        if attribute_value[0] != '':
            basequery = basequery + ' and a1.auth_id=$v1'
        if attribute_value[1] != '':
            basequery = basequery + \
                ' and (a1.claim_request.cardholder_id=$v2)'
        if attribute_value[2] != '':
            basequery = basequery + \
                ' and DATE_FORMAT_STR(a1.startDate,"1111-11-11")>=$v3'
        if attribute_value[3] != '':
            basequery = basequery + \
                ' and DATE_FORMAT_STR(a1.startDate,"1111-11-11")<=$v4'

        # added group_id
        if attribute_value[4] != '':
            basequery = basequery + ' and a1.group_id=$v5'

        basequery = basequery + \
            ' order by a1.startDate desc, a1.auth_id desc, a1.sequenceNumber desc'
        query = N1QLQuery(
            basequery, v1=attribute_value[0], v2=attribute_value[1], v3=attribute_value[2], v4=attribute_value[3],
            v5=attribute_value[4]
        )
        authidlist = []

        log.debug(query)
        log.debug("before going to loop")
        log.debug(self.cb.n1ql_query(query))
        log.debug("for single result")
        log.debug(basequery)
        log.debug(self.cb.n1ql_query(basequery1).get_single_result())
        data = self.cb.n1ql_query(basequery1).get_single_result()

        # for rowresult in self.cb.n1ql_query(query):
        #     log.debug("rowresult -----------------------")
        #     log.debug(rowresult)
        #     log.debug(" after rowresult -----------------------")
        #     if rowresult["auth_id"] not in authidlist:
        #         authidlist.append(rowresult["auth_id"])
        #         totalreccount = totalreccount + 1
        #         if totalreccount > attribute_value[5] and totalreccount <= (attribute_value[5] + 20):
        #             result["result"].append(rowresult)
        #             count = count + 1

        result["count"] = count
        result["total"] = totalreccount
        result["result"].append(data)

        return result

    def getClaimWithUser(self, attribute_value):

        count = 0
        result = {"count": 0, "result": []}



        basequery = 'Select a1.auth_id, a1.sequenceNumber, a1.startDate, a1.endDate, a1.claim_response.transaction_response_status as response_status, a1.claim_transfer_response.transaction_response_status, a1.claim_request.product_id, a1.claim_request.group_id, a1.claim_request.cardholder_id, a1.claim_request.person_code, a1.claim_request.relationship_code, a1.claim_request.transaction_code, b1.drug_name from `' + \
            self.instance_type+'` a1 LEFT JOIN `'+self.instance_type + \
                '` b1 ON b1.type = "ndc_drugs" AND a1.claim_request.product_id = b1.ndc where a1.type="claim" and a1.auth_id <>""'

        if attribute_value[0] != '':
            basequery = basequery + ' and a1.auth_id=$v1'

        basequery = basequery + \
            ' order by a1.startDate desc, a1.auth_id desc, a1.sequenceNumber desc'

        query = N1QLQuery(basequery, v1=attribute_value[0])


        est = pytz.timezone('US/Eastern')
        utc = pytz.utc
        fmtout = '%Y-%m-%d %H:%M'
        fmtinp = '%Y-%m-%dT%H:%M'
        

        for rowresult in self.cb.n1ql_query(query):
            count = count + 1
            temp = {}

            temp["claim_details"] = "override"
            temp["status"] = ""
            if "response_status" in rowresult.keys():
                temp["status"] = rowresult["response_status"]
            temp["transferstatus"] = ""
            if "transaction_response_status" in rowresult.keys():
                temp["transferstatus"] = rowresult["transaction_response_status"]
            temp["claimstatus"] = ""
            if "claim_status" in rowresult.keys():
                temp["claimstatus"] = rowresult["claim_status"]
            temp["memberid"] = ""
            if "cardholder_id" in rowresult.keys():
                temp["memberid"] = rowresult["cardholder_id"]

            temp["auth_id"] = rowresult["auth_id"]
            # temp["date_time"] = rowresult["startDate"][0:16]
            isodtime = datetime.strptime(rowresult["startDate"][0:16],fmtinp)
            utcdtime = datetime(isodtime.year,isodtime.month, isodtime.day, isodtime.hour, isodtime.minute, isodtime.second, tzinfo=utc)
            temp["date_time_utc"] = utcdtime.strftime(fmtout)
            temp["date_time"] = utcdtime.astimezone(est).strftime(fmtout)
            
            temp["product_name"] = ""
            if "drug_name" in rowresult.keys():
                temp["product_name"] = rowresult["drug_name"]

            temp["group_id"] = ""
            if "group_id" in rowresult.keys():
                temp["group_id"] = rowresult["group_id"]
            temp["transactioncode"] = ""
            if "transaction_code" in rowresult.keys():
                temp["transactioncode"] = rowresult["transaction_code"]
            temp["sequencenumber"] = rowresult["sequenceNumber"]

            temp["firstname"] = ""
            temp["lastname"] = ""
            temp["personcode"] = ""

            if "person_code" in rowresult.keys():
                temp["personcode"] = rowresult["person_code"]
                tvuserresult = self.getTVUserDetails(
                    rowresult["cardholder_id"])
                pcode = str(rowresult["cardholder_id"])[-2:]
                if "first_name" in tvuserresult:
                    temp["firstname"] = tvuserresult["first_name"]
                if "last_name" in tvuserresult:
                    temp["lastname"] = tvuserresult["last_name"]

                if "person_code" in tvuserresult and pcode == tvuserresult["person_code"]:
                    temp["firstname"] = tvuserresult["first_name"]
                    temp["lastname"] = tvuserresult["last_name"]

                elif "dependents" in tvuserresult:
                    for i in range(0, len(tvuserresult["dependents"])):
                        if "person_code" in tvuserresult["dependents"][i] and pcode == tvuserresult["dependents"][i]["person_code"]:
                            temp["firstname"] = tvuserresult["dependents"][i]["first_name"]
                            temp["lastname"] = tvuserresult["dependents"][i]["last_name"]
                            break

            result["result"].append(temp)

        result["count"] = count
        pdb.set_trace()
        return result

    def updateClaimOverride(self, attribute_value):
        
        basequery = 'UPDATE `'+self.instance_type + \
            '` SET over_ride="Y", copay_override=$v1, override_amount=$v2, override_percentage=$v3, overridenumber=$v4, override_from=$v5, override_thru=$v6 where type="claim" and auth_id=$v7 and sequenceNumber=$v8 RETURNING *'
        query = N1QLQuery(
            basequery, v1=attribute_value[0], v2=attribute_value[1], v3=attribute_value[2], v4=attribute_value[3], v5=attribute_value[4], v6=attribute_value[5], v7=attribute_value[6], v8=attribute_value[7])

        try:
            # rowresult = self.cb.n1ql_query(query).execute()
            rowresult = self.cb.n1ql_query(query).get_single_result()
            if rowresult is None:
                return None
            return 1
        except Exception as _:
            return None

    def getClaimOverride(self, attribute_value):

        basequery = 'Select * from `'+self.instance_type + \
            '` where type="claim" and auth_id=$v1 and sequenceNumber=$v2'

        query = N1QLQuery(
            basequery, v1=attribute_value[0], v2=attribute_value[1])
        result = None
        for rowresult in self.cb.n1ql_query(query):
            result = rowresult[self.instance_type]

        return result
    
    def getClaimMember(self, attribute_value):

        count = 0
        result = {}
        temp = {}
        temp["memberid"] = attribute_value[0]
        temp["personcode"] = attribute_value[1]
        flipt_person_id = str(temp["memberid"])[:-2]

        search_option = {'full_document': True,
                            'filter': {
                                'flipt_person_id': {'type': 'eq', 'value': flipt_person_id,
                                                    'case_sensitive': False},
                                '$tv.status': {'type': 'eq', 'value': 'ACTIVATED'}}, 'filter_type': 'and'}

        search_opt = base64.b64encode(str.encode(json.dumps(search_option)))
        search_json = {'search_option': search_opt}
        res = requests.post(self.URI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''),
                            data=search_json)

        response = res.json()

        if 'error' in response:
            err_msg = str(response['error'])
            return result
        elif (res.status_code != 200 or 'data' not in response or
                (res.status_code == 200 and not response['data'].get('documents'))):
            return result
        else:
            res = json.loads(base64.b64decode(response['data']['documents'][0]['attributes']).
                                decode('utf-8'))
        result = res
        
        return result

    def getClaimTransaction(self, attribute_value):

        basequery = 'Select * from `'+self.instance_type + \
            '` where type="claim" and auth_id=$v1 and sequenceNumber=$v2'

        query = N1QLQuery(
            basequery, v1=attribute_value[0], v2=attribute_value[1])
        result = None
        for rowresult in self.cb.n1ql_query(query):
            result = rowresult[self.instance_type]

        return result
    
    def getTVUserDetails(self,cid):

        member_id = cid
        
        flipt_member_id = str(member_id)[:-2]
        person_code = str(flipt_member_id)[-2:]

        search_option = {'full_document': True,
                                'filter': {
                                    'flipt_person_id': {'type': 'eq', 'value': flipt_member_id,
                                                        'case_sensitive': False},
                                    '$tv.status': {'type': 'eq', 'value': 'ACTIVATED'}}, 'filter_type': 'and'}

        search_opt = base64.b64encode(
                str.encode(json.dumps(search_option)))
        search_json = {'search_option': search_opt}
        res = requests.post(self.URI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''),
                                data=search_json)

        response = res.json()

        if 'error' in response:
            err_msg = str(response['error'])
        elif (res.status_code != 200 or 'data' not in response or
                    (res.status_code == 200 and not response['data'].get('documents'))):
            return res
        else:
            res = json.loads(base64.b64decode(response['data']['documents'][0]['attributes']).decode('utf-8'))
            # res = res.json()
            return res
    
    def getNDCDrug(self, attribute_value):

        basequery = 'Select * from `'+self.instance_type + \
            '` where type="ndc_drugs" and ndc=$v1'

        query = N1QLQuery(
            basequery, v1=attribute_value)
        result = None
        for rowresult in self.cb.n1ql_query(query):
            result = rowresult[self.instance_type]
        
        return result
    
    def getPrescription(self, attribute_value):

        basequery = 'Select * from `'+self.instance_type + \
            '` where type="prescription" and prescription_id=$v1'

        query = N1QLQuery(
            basequery, v1=attribute_value)
        result = None
        for rowresult in self.cb.n1ql_query(query):
            result = rowresult[self.instance_type]
        
        return result
    
    def getPharmacy(self, attribute_value):
        
        basequery = 'Select * from `'+self.instance_type + \
            '` where type="cp_pharmacy" and pharmacynpi=$v1'

        query = N1QLQuery(
            basequery, v1=attribute_value)
        result = None
        for rowresult in self.cb.n1ql_query(query):
            result = rowresult[self.instance_type]
        
        return result

    def getEligibilityUserDetails(self,svalue):
        
        if svalue['searchkey'] == 'memberid':
            member_id = svalue['searchvalue']
        
            flipt_member_id = str(member_id)[:-2]

            search_option = {'full_document': True,
                                'filter': {
                                    'flipt_person_id': {'type': 'eq', 'value': flipt_member_id,
                                                        'case_sensitive': False},
                                    '$tv.status': {'type': 'eq', 'value': 'ACTIVATED'}}, 'filter_type': 'and'}

        else:
            lastname = svalue['searchvalue']

            search_option = {'full_document': True,
                                'filter': {
                                    'last_name': {'type': 'eq', 'value': lastname,
                                                        'case_sensitive': False},
                                    '$tv.status': {'type': 'eq', 'value': 'ACTIVATED'}}, 'filter_type': 'and'}
        
        search_opt = base64.b64encode(
                str.encode(json.dumps(search_option)))
        search_json = {'search_option': search_opt}
        res = requests.post(self.URI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''),
                                data=search_json)

        response = res.json()
        
        search_result = []
        if 'error' in response:
            err_msg = str(response['error'])
            return err_msg, None
        elif (res.status_code != 200 or 'data' not in response or
                    (res.status_code == 200 and not response['data'].get('documents'))):
            return 'No Data', None
        else:
            tot_records = response['data']['info']['total_result_count']
            for i in range(0,tot_records): 
                res = json.loads(base64.b64decode(response['data']['documents'][i]['attributes']).decode('utf-8'))
                search_result.append(res)
            return 'success', search_result
    

    def getEligibilityMember(self,svalue):
        
        
        member_id = svalue['memberid']
        
        flipt_member_id = str(member_id)[:-2]

        search_option = {'full_document': True,
                                'filter': {
                                    'flipt_person_id': {'type': 'eq', 'value': flipt_member_id,
                                                        'case_sensitive': False},
                                    '$tv.status': {'type': 'eq', 'value': 'ACTIVATED'}}, 'filter_type': 'and'}

        
        search_opt = base64.b64encode(
                str.encode(json.dumps(search_option)))
        search_json = {'search_option': search_opt}
        res = requests.post(self.URI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''),
                                data=search_json)

        response = res.json()
        
        search_result = []
        if 'error' in response:
            err_msg = str(response['error'])
            return err_msg, None
        elif (res.status_code != 200 or 'data' not in response or
                    (res.status_code == 200 and not response['data'].get('documents'))):
            return 'No Data', None
        else:
            res = json.loads(base64.b64decode(response['data']['documents'][0]['attributes']).decode('utf-8'))
            return 'success', res
    
    def updateEligibilityMember(self, headerdata):
        
        att = None
        userid = None
        currentyear = str(datetime.now().year)
        search_option = {'full_document': True, 'filter': {
            '$tv.username': {'type': 'eq', 'value': headerdata['workmail'], 'case_sensitive': False},
            '$tv.status': {'type': 'eq', 'value': 'ACTIVATED'}}, 'filter_type': 'and'}
        search_opt = base64.b64encode(str.encode(json.dumps(search_option)))
        data = {'search_option': search_opt}
        r = requests.post(self.URI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''), data=data)
        response = r.json()
        if 'data' not in response: 
            att = None
            userid = None
        elif len(response['data']['documents']) == 0 and r.status_code == 200: 
            att = None
            userid = None
        else:
            att = json.loads(str(base64.b64decode(response['data']['documents'][0]['attributes']), 'utf-8'))
            userid = response['data']['documents'][0]['user_id']
        
        if userid is not None and att['employment_status'] != headerdata['coveragestatus']:
            
            if att['employment_status'] == 'Active' and headerdata['coveragestatus'] == 'Terminated':
                att['employment_status'] = headerdata['coveragestatus']
                if 'eligibility' in att:
                    for i in range(0,len(att['eligibility'])):
                        if att['eligibility'][i]['plan_year'] == currentyear:
                            att['eligibility'][i]['coverage_termination_date'] = headerdata['coverageterminationdate']
                else:
                    att['plan_year'] = currentyear
                    att['coverage_termination_date'] = headerdata['coverageterminationdate']
                    att['coverage_effective_date'] = headerdata['coverageeffectivedate']
                    att['cobra_effective_date'] = headerdata['cobraeffectivedate']
                    att['cobra_termination_date'] = headerdata['cobraterminationdate']
            elif headerdata['coveragestatus'] == 'COBRA':
                if 'eligibility' in att:
                    for i in range(0,len(att['eligibility'])):
                        if att['eligibility'][i]['plan_year'] == currentyear:
                            att['employment_status'] = headerdata['coveragestatus']
                            att['eligibility'][i]['coverage_effective_date'] = headerdata['coverageeffectivedate']
                            att['eligibility'][i]['coverage_termination_date'] = headerdata['coverageterminationdate']
                            att['eligibility'][i]['cobra_effective_date'] = headerdata['cobraeffectivedate']
                            att['eligibility'][i]['cobra_termination_date'] = headerdata['cobraterminationdate']
                else:
                    # att['employment_status'] = headerdata['coveragestatus']
                    att['plan_year'] = currentyear
                    att['coverage_termination_date'] = headerdata['coverageterminationdate']
                    att['coverage_effective_date'] = headerdata['coverageeffectivedate']
                    att['cobra_effective_date'] = headerdata['cobraeffectivedate']
                    att['cobra_termination_date'] = headerdata['cobraterminationdate']
            elif headerdata['coveragestatus'] == 'Active':
                if 'eligibility' in att:
                    for i in range(0,len(att['eligibility'])):
                        if att['eligibility'][i]['plan_year'] == currentyear:
                            att['employment_status'] = headerdata['coveragestatus']
                            att['eligibility'][i]['coverage_effective_date'] = headerdata['coverageeffectivedate']
                            att['eligibility'][i]['coverage_termination_date'] = headerdata['coverageterminationdate']
                            att['eligibility'][i]['cobra_effective_date'] = ''
                            att['eligibility'][i]['cobra_termination_date'] = ''
                else:
                    # att['employment_status'] = headerdata['coveragestatus']
                    att['plan_year'] = currentyear
                    att['coverage_termination_date'] = headerdata['coverageterminationdate']
                    att['coverage_effective_date'] = headerdata['coverageeffectivedate']
                    att['cobra_effective_date'] = headerdata['cobraeffectivedate']
                    att['cobra_termination_date'] = headerdata['cobraterminationdate']
            new_att = base64.b64encode(str.encode(json.dumps(att)))
            data = {'attributes': new_att}
            # print(att)
            updateURI = self.URI
            updateURI = str(updateURI)
            updateTVURI = updateURI[:updateURI.rfind('/')]+'/'+str(userid)
            r = requests.put(updateTVURI, auth=HTTPBasicAuth(self.TRUEVAULT_API_KEY, ''),data=data)
            res = r.json()
            
            return res

        else:
            pass
        return {}
