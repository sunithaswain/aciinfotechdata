from datetime import datetime
import pytz, pdb

class ClaimPortalProcessor(object):

    def __init__(self, config, claimobj, claimportaldataprovobj):
        self.requestdata = ''
        self.claimobj = claimobj
        self.claimportaldataprovobj = claimportaldataprovobj
        self.config = config
        

    def getClaim(self, requestdata):
        self.requestdata = requestdata
        headerdata = {}

        try:
            headerdata = self.requestdata
            if "authid" not in headerdata:
                headerdata["authid"] = ""
            if "memberid" not in headerdata:
                headerdata["memberid"] = ""
            if "startdate" not in headerdata:
                headerdata["startdate"] = ""
            # elif headerdata["startdate"]  != "":
            #    headerdata["startdate"] = headerdata["startdate"][6:10]+"-"+headerdata["startdate"][0:2]+"-"+headerdata["startdate"][3:5]
            if "enddate" not in headerdata:
                headerdata["enddate"] = ""
            # elif headerdata["enddate"]  != "":
            #    headerdata["enddate"] = headerdata["enddate"][6:10]+"-"+headerdata["enddate"][0:2]+"-"+headerdata["enddate"][3:5]
            if "offset" not in headerdata:
                headerdata["offset"] = 0
            if "groupid" not in headerdata:
                headerdata["groupid"] = ""
        except Exception as _:
            # self.__log.info('Could not determine  claim')
            pass

        # added with group id
        # pdb.set_trace()
        clean_header_data = {k: v.strip() for k, v in headerdata.items()}
        resultQuery = self.claimportaldataprovobj.getClaims(
            [clean_header_data["authid"], clean_header_data["memberid"], clean_header_data["startdate"],
             clean_header_data["enddate"],
             clean_header_data["groupid"], clean_header_data["offset"]])
        # resultQuery = self.claimportaldataprovobj.getClaims(
        #     [headerdata["authid"], headerdata["memberid"], headerdata["startdate"], headerdata["enddate"], headerdata["offset"]])

        responseResult = []
        est = pytz.timezone('US/Eastern')
        utc = pytz.utc
        fmtout = '%Y-%m-%d %H:%M'
        fmtinp = '%Y-%m-%dT%H:%M'


        for rec in resultQuery["result"]:

            temp = {}
            
            temp["claim_details"] = "claim"
            temp["status"] = ""
            if "response_status" in rec.keys():
                temp["status"] = rec["response_status"]
            temp["transferstatus"] = ""
            if "transaction_response_status" in rec.keys():
                temp["transferstatus"] = rec["transaction_response_status"]
            temp["claimstatus"] = ""
            if "claim_status" in rec.keys():
                temp["claimstatus"] = rec["claim_status"]

            temp["memberid"] = ""
            if "cardholder_id" in rec.keys():
                temp["memberid"] = rec["cardholder_id"]

            temp["auth_id"] = rec["auth_id"]
            # temp["date_time"] = rec["startDate"][0:16]
            isodtime = datetime.strptime(rec["startDate"][0:16],fmtinp)
            utcdtime = datetime(isodtime.year,isodtime.month, isodtime.day, isodtime.hour, isodtime.minute, isodtime.second, tzinfo=utc)
            temp["date_time_utc"] = utcdtime.strftime(fmtout)
            temp["date_time"] = utcdtime.astimezone(est).strftime(fmtout)
            temp["product_name"] = ""
            if "drug_name" in rec.keys():
                temp["product_name"] = rec["drug_name"]

            temp["group_id"] = ""
            if "group_id" in rec.keys():
                temp["group_id"] = rec["group_id"]
            temp["transactioncode"] = ""
            if "transaction_code" in rec.keys():
                temp["transactioncode"] = rec["transaction_code"]
            temp["firstname"] = ""
            temp["lastname"] = ""
            temp["personcode"] = ""
            if "person_code" in rec.keys():
                temp["personcode"] = rec["person_code"]
                tvuserresult = self.claimportaldataprovobj.getTVUserDetails(rec["cardholder_id"])
                pcode = str(rec["cardholder_id"])[-2:]
                if "first_name" in tvuserresult:
                    temp["firstname"] = tvuserresult["first_name"]
                if "last_name" in tvuserresult:
                    temp["lastname"] = tvuserresult["last_name"]
                
                if "person_code" in tvuserresult and pcode == tvuserresult["person_code"]:
                    temp["firstname"] = tvuserresult["first_name"]
                    temp["lastname"] = tvuserresult["last_name"]
                     
                elif "dependents" in tvuserresult:
                    for i in range(0,len(tvuserresult["dependents"])):
                        if "person_code" in tvuserresult["dependents"][i] and pcode == tvuserresult["dependents"][i]["person_code"]:
                            temp["firstname"] = tvuserresult["dependents"][i]["first_name"]
                            temp["lastname"] = tvuserresult["dependents"][i]["last_name"]
                            break
                    
            
            temp["sequencenumber"] = rec["sequenceNumber"]

            responseResult.append(temp)

        resultQuery["result"] = responseResult
        return resultQuery
    
    def getClaimDetails(self, requestparams):
        headerdata = {}
        headerdata["authid"] = requestparams.get(
            'authid') if requestparams.get('authid') != None else ""

        return self.claimportaldataprovobj.getClaimWithUser([headerdata["authid"]])


    def getClaimOverride(self, requestparams):
        headerdata = {}
        headerdata["authid"] = requestparams.get(
            'authid') if requestparams.get('authid') != None else ""
        headerdata["sequencenumber"] = int(requestparams.get(
            'sequencenumber')) if requestparams.get('sequencenumber') != None else ""
        headerdata["productname"] = requestparams.get(
            'productname') if requestparams.get('productname') != None else ""

        claimresult = self.claimportaldataprovobj.getClaimOverride(
            [headerdata["authid"], headerdata["sequencenumber"]])
        
        tvuserresult = self.claimportaldataprovobj.getTVUserDetails(
            claimresult["claim_request"]["cardholder_id"])
        
        responseresult = {}
        responseresult["authid"] = claimresult["auth_id"]
        responseresult["sequencenumber"] = claimresult["sequenceNumber"]
        responseresult["product_id"] = ''
        if "product_id" in claimresult["claim_request"]:
            responseresult["product_id"] = claimresult["claim_request"]["product_id"]
        
        responseresult["cardholder_id"] = ''
        if "cardholder_id" in claimresult["claim_request"]:
            responseresult["cardholder_id"] = claimresult["claim_request"]["cardholder_id"]
        
        responseresult["prescription_id"] = ""
        if "prescription_id" in claimresult["claim_request"]:
            responseresult["prescription_id"] = claimresult["prescription_id"]

        if 'group' in tvuserresult:
            responseresult["groupname"] = tvuserresult["group"]
        else:
            responseresult["groupname"] = ""
        if "flipt_person_id" in tvuserresult:
            responseresult["memberid"] = tvuserresult["flipt_person_id"]
        else:
            responseresult["memberid"] = ''
        if 'first_name' in tvuserresult:
            responseresult["firstname"] = tvuserresult["first_name"]
        else:
            responseresult["firstname"] = ''
        if 'last_name' in tvuserresult:
            responseresult["lastname"] = tvuserresult["last_name"]
        else:
            responseresult["lastname"] = ''
        
        if 'relationship_code' in tvuserresult:
            responseresult["relationshipcode"] = tvuserresult["relationship_code"]
        else:
            responseresult["relationshipcode"] = ''
        

        if 'over_ride' in claimresult:
            responseresult["over_ride"] = claimresult["over_ride"]
        else:
            responseresult["over_ride"] = ""
        if 'copay_override' in claimresult:
            responseresult["copay_override"] = claimresult["copay_override"]
        else:
            responseresult["copay_override"] = ""
        if 'override_amount' in claimresult:
            responseresult["override_amount"] = claimresult["override_amount"]
        else:
            responseresult["override_amount"] = ""
        if 'override_percentage' in claimresult:
            responseresult["override_percentage"] = claimresult["override_percentage"]
        else:
            responseresult["override_percentage"] = ""
        if 'overridenumber' in claimresult:
            responseresult["overridenumber"] = claimresult["overridenumber"]
        else:
            responseresult["override_number"] = ""
        if 'override_from' in claimresult:
            responseresult["override_from"] = claimresult["override_from"]
        else:
            responseresult["override_from"] = ''
        if 'override_thru' in claimresult:
            responseresult["override_thru"] = claimresult["override_thru"]
        else:
            responseresult["override_thru"] = ""

        if 'person_code' in claimresult["claim_request"]:
            responseresult["personcode"] = claimresult["claim_request"]["person_code"]
        else:
            responseresult["personcode"] = ''
    
        responseresult["productname"] = headerdata["productname"]
        responseresult["gpicode"] = claimresult["claim_request"]["gpi"]
        responseresult["authorizationnumber"] = claimresult["auth_id"]
        return responseresult


    def updateClaimOverride(self, requestdata):
        self.requestdata = requestdata
        self.claimobj.requestData = self.requestdata

        headerdata = {}
        try:
            headerdata = eval(self.requestdata)

            if "copay_override" not in headerdata:
                headerdata["copay_override"] = ""
            if "override_amount" not in headerdata:
                headerdata["override_amount"] = ""
            if "override_percentage" not in headerdata:
                headerdata["override_percentage"] = ""
            if "overridenumber" not in headerdata:
                headerdata["overridenumber"] = ""
            if "overridefrom" not in headerdata:
                headerdata["overridefrom"] = ""
            if "overridethru" not in headerdata:
                headerdata["overridethru"] = ""
            if "authid" not in headerdata:
                headerdata["authid"] = ""
            if "sequencenumber" not in headerdata:
                headerdata["sequencenumber"] = ""
            if "prescriptionid" not in headerdata:
                headerdata["prescriptionid"] = ""
        except Exception as _:
            return {"result": False, "message": "Data is invalid"}

        updateresult = self.claimportaldataprovobj.updateClaimOverride(
            [headerdata["copay_override"], headerdata["override_amount"], headerdata["override_percentage"],
             headerdata["overridenumber"], headerdata["overridefrom"], headerdata["overridethru"],
             headerdata["authid"], headerdata["sequencenumber"]])
        
        if updateresult:
            return {"result": True, "count": updateresult}
        return {"result": False, "count": 0}


    def getClaimMember(self, requestparams):
        headerdata = {}
        headerdata["memberid"] = requestparams.get(
            'memberid') if requestparams.get('memberid') != None else ""
        headerdata["personcode"] = requestparams.get(
            'personcode') if requestparams.get('personcode') != None else ""

        tvresult = self.claimportaldataprovobj.getClaimMember(
            [headerdata.get("memberid"), headerdata.get("personcode")])
        
        responseresult = {}

        if "active" not in tvresult:
            responseresult["active"] = ""
        else:
            responseresult["active"] = tvresult["active"]
        
        responseresult["carrierid"] = 'FLIPT'
        responseresult["carriername"] = 'FLIPT'
        
        if "domain_name" not in tvresult:
            responseresult["accountid"] = ""
        else:
            responseresult["accountid"] = tvresult["domain_name"]
        
        if "domain_name" not in tvresult:
            responseresult["accountname"] = ''
        else:
            responseresult["accountname"] = tvresult["domain_name"]
        if "group" not in tvresult:
            responseresult["groupid"] = ''
        else:
            responseresult["groupid"] = tvresult["group"]
        
        if "group"not in tvresult:
            responseresult["groupname"] = ''
        else:
            responseresult["groupname"] = tvresult["group"]
        
        responseresult["memberid"] = headerdata["memberid"]

        if "flipt_person_id" not in tvresult:
            responseresult["flipt_person_id"] = ''
        else:
            responseresult["flipt_person_id"] = tvresult["flipt_person_id"]
        
        if "coverage_effective_date" not in tvresult:
            responseresult["coveragefromdate"] = ''
        else:
            responseresult["coveragefromdate"] = tvresult["coverage_effective_date"]
        
        if "coverage_termination_date" not in tvresult:
            responseresult["coveragetodate"] = ''
        else:
            responseresult["coveragetodate"] = tvresult["coverage_termination_date"]
        
        responseresult["firstname"] = ''
        responseresult["lastname"] = ''
        responseresult["personcode"] = ''
        responseresult["middlename"] = ''
        responseresult["relationshipcode"] = ''
        responseresult["gender"] = ''
        responseresult["dob"] = ''
        
        pcod = str(headerdata["memberid"])[-2:]

        if "first_name" in tvresult:
            responseresult["firstname"] = tvresult["first_name"]
        if "last_name" in tvresult:
            responseresult["lastname"] = tvresult["last_name"]
        
        if "person_code" in tvresult and pcod == tvresult["person_code"]:
            responseresult["firstname"] = tvresult["first_name"]
            responseresult["lastname"] = tvresult["last_name"]
            responseresult["personcode"] = tvresult["person_code"]
            responseresult["gender"] = tvresult["gender"]
            responseresult["dob"] = tvresult["date_of_birth"]
                
        elif "dependents" in tvresult:
            for i in range(0,len(tvresult["dependents"])):
                if "person_code" in tvresult["dependents"][i] and pcod == tvresult["dependents"][i]["person_code"]:
                    responseresult["firstname"] = tvresult["dependents"][i]["first_name"]
                    responseresult["lastname"] = tvresult["dependents"][i]["last_name"]
                    responseresult["personcode"] = tvresult["dependents"][i]["person_code"]
                    responseresult["gender"] = tvresult["dependents"][i]["gender"]
                    responseresult["dob"] = tvresult["dependents"][i]["date_of_birth"]
                    break

        """
        if "first_name" not in tvresult:
            responseresult["firstname"] = ''
        else:
            responseresult["firstname"] = tvresult["first_name"]
        
        if "last_name" not in tvresult:
            responseresult["lastname"] = ''
        else:
            responseresult["lastname"] = tvresult["last_name"]
        
        if "person_code" not in tvresult:
            responseresult["personcode"] = ''
        else:
            responseresult["personcode"] = tvresult["person_code"]
        
        responseresult["middlename"] = ''

        responseresult["relationshipcode"] = ''

        if "gender" not in tvresult:
            responseresult["gender"] = ''
        else:
            responseresult["gender"] = tvresult["gender"]
        
        if "date_of_birth" not in tvresult:
            responseresult["dob"] = ''
        else:
            responseresult["dob"] = tvresult["date_of_birth"]
        """
        if "home_address_1" not in tvresult:
            responseresult["address"] = ''
        else:
            responseresult["address"] = tvresult["home_address_1"]
        
        if "city" not in tvresult:
            responseresult["city"] = ''
        else:
            responseresult["city"] = tvresult["city"]
        
        if "state" not in tvresult:
            responseresult["state"] = ''
        else:
            responseresult["state"] = tvresult["state"]
        
        if "zip" not in tvresult:
            responseresult["zip"] = ''
        else:
            responseresult["zip"] = tvresult["zip"]
        
        responseresult["phone"] = ''
        if "personal_phones" in tvresult:
            phonenumber = []
            for k in range(0,len(tvresult["personal_phones"])):
                
                if "phone_number" in tvresult["personal_phones"][k] and "verified" in tvresult["personal_phones"][k] and "preferred" in tvresult["personal_phones"][k]:
                    phonenumber.append(tvresult["personal_phones"][k]["phone_number"])
            
            
            responseresult["phone"] = ", ".join(phonenumber)

        if "work_email" not in tvresult:
            responseresult["email"] = ''
        else:
            responseresult["email"] = tvresult["work_email"]
        
        responseresult["planoverride"] = ''
        if "benefit_plan_name" not in tvresult:
            responseresult["planoverride"] = ''
        else:
            responseresult["planoverride"] = tvresult["benefit_plan_name"]

        if "hire_date" not in tvresult:
            responseresult["fromdate"] = ''
        else:
            responseresult["fromdate"] = tvresult["hire_date"]
        
        if "termination_date" not in tvresult:
            responseresult["throughdate"] = ''
        else:
            responseresult["throughdate"] = tvresult["termination_date"]

        return responseresult


    def getClaimTransaction(self, requestparams):
        headerdata = {}
        headerdata["authid"] = requestparams.get(
            'authid') if requestparams.get('authid') != None else ""
        headerdata["sequencenumber"] = int(requestparams.get(
            'sequencenumber')) if requestparams.get('sequencenumber') != None else ""

        tresult = self.claimportaldataprovobj.getClaimTransaction(
            [headerdata.get("authid"), headerdata.get("sequencenumber")])
        
        tvuserresult = self.claimportaldataprovobj.getTVUserDetails(
            tresult["claim_request"]["cardholder_id"])
        
        ndcresult = None
        ndcresult = self.claimportaldataprovobj.getNDCDrug(
            tresult["claim_request"]["product_id"])
        prescriptionresult = None
        if "prescription_id" in tresult.keys():
            prescriptionresult = self.claimportaldataprovobj.getPrescription(
                tresult["prescription_id"])

        pharmacyresult = None
        if "claim_request" in tresult.keys() and "service_provider_id" in tresult["claim_request"]:
            pharmacyresult = self.claimportaldataprovobj.getPharmacy(tresult["claim_request"]["service_provider_id"])
        
        responseresult = {}
        responseresult["rejection"] = {}
        responseresult["providers"] = {}
        responseresult["overview"] = {}
        responseresult["pricing"] = {}

        responseresult["authid"] = tresult["auth_id"]
        responseresult["sequencenumber"] = tresult["sequenceNumber"]
        if tresult.get("claim_response") is None:
            responseresult["rejection"]["rejectcode"] = ''
            responseresult["rejection"]["rejectmessage1"] = ''
            responseresult["rejection"]["rejectmessage2"] = ""
        else:
            if "reject_code" in tresult["claim_response"]:
                responseresult["rejection"]["rejectcode"] = tresult["claim_response"]["reject_code"]
            else:
                responseresult["rejection"]["rejectcode"] = ''
            
            if "message" in tresult["claim_response"]:
                responseresult["rejection"]["rejectmessage1"] = tresult["claim_response"]["message"]
            else:
                responseresult["rejection"]["rejectmessage1"] = ''
            
            responseresult["rejection"]["rejectmessage2"] = ""
            if "additional_message_information" in tresult["claim_response"]:
                responseresult["rejection"]["rejectmessage2"] = tresult["claim_response"]["additional_message_information"]
            
        if tresult.get("claim_transfer_response") is None:
            responseresult["rejection"]["payerrejectcode"] = ''
            responseresult["rejection"]["payerrejectmessage1"] = ''
            responseresult["rejection"]["payerrejectmessage2"] = ''
        else:
            if "reject_code" in tresult["claim_transfer_response"]:
                responseresult["rejection"]["payerrejectcode"] = tresult["claim_transfer_response"]["reject_code"]
            else:
                responseresult["rejection"]["payerrejectcode"] = ''
            
            if "message" in tresult["claim_transfer_response"]:
                responseresult["rejection"]["payerrejectmessage1"] = tresult["claim_transfer_response"]["message"]
            else:
                responseresult["rejection"]["payerrejectmessage1"] = ''
            
            responseresult["rejection"]["payerrejectmessage2"] = ""
            if "additional_message_information" in tresult["claim_transfer_response"]:
                responseresult["rejection"]["payerrejectmessage2"] = tresult["claim_transfer_response"]["additional_message_information"]
          

        if tresult.get("claim_request") is None:
            responseresult["providers"]["pharmacynpi"] = ""
        else:
            if "service_provider_id" in tresult["claim_request"]:
                responseresult["providers"]["pharmacynpi"] = tresult["claim_request"]["service_provider_id"]
            else:
                responseresult["providers"]["pharmacynpi"] = ''
        
        if pharmacyresult is None:
            responseresult["providers"]["pharmacyncpdp"] = ""
            responseresult["providers"]["pharmacyaddress"] = ""
            responseresult["providers"]["pharmacyphone"] = ""
            responseresult["providers"]["pharmacyfax"] = ""
        else:
            responseresult["providers"]["pharmacyncpdp"] = pharmacyresult["cp_pharmacy_info"][0]["pharmacyid"]
            responseresult["providers"]["pharmacyaddress"] = pharmacyresult["pharmacyname"]+", "+pharmacyresult["pharmacyaddress1"]+", "+pharmacyresult["pharmacyaddress2"]+", "+pharmacyresult["pharmacycity"]+", "+pharmacyresult["pharmacystate"]+", "+pharmacyresult["pharmacyzip1"]
            responseresult["providers"]["pharmacyphone"] = pharmacyresult["pharmacyphone"]
            responseresult["providers"]["pharmacyfax"] = pharmacyresult["pharmacyfax"]
        
        if tresult.get("claim_request") is None:
            responseresult["providers"]["prescribernpi"] = ""
        else:
            if "prescriber_id" in tresult["claim_request"]:
                responseresult["providers"]["prescribernpi"] = tresult["claim_request"]["prescriber_id"]
            else:
                responseresult["providers"]["prescribernpi"] = ''
        
        if tresult.get("claim_request") is None:
            responseresult["providers"]["prescriberaddress"] = ""
        else:
            if "prescriber_city_address" in tresult["claim_request"]:
                responseresult["providers"]["prescriberaddress"] = tresult["claim_request"]["prescriber_city_address"]
            else:
                responseresult["providers"]["prescriberaddress"] = ''
        
        
        if tresult.get("claim_request") is None:
            responseresult["providers"]["prescriberphone"] = ""
        else:
            if "prescriber_phone_number" in tresult["claim_request"]:
                responseresult["providers"]["prescriberphone"] = tresult["claim_request"]["prescriber_phone_number"]
            else:
                responseresult["providers"]["prescriberphone"] = ''
        
        responseresult["providers"]["prescriberfax"] = ""

        responseresult["overview"]["claimbin"] = tresult["claim_request"]["bin_number"]
        responseresult["overview"]["claimpcn"] = tresult["claim_request"]["processor_control_number"]
        responseresult["overview"]["claimdateofservice"] = tresult["claim_request"]["date_of_service"]
        responseresult["overview"]["claimdatetime"] = tresult["startDate"]
        responseresult["overview"]["claimauthid"] = tresult["auth_id"]
        responseresult["overview"]["claimsequencenumber"] = tresult["sequenceNumber"]
        if tresult.get("claim_response") is None:
            responseresult["overview"]["claimstatus"] = ''
        else:
            responseresult["overview"]["claimstatus"] = tresult["claim_response"]["transaction_response_status"]
        responseresult["overview"]["claimrxnumber"] = tresult["claim_request"]["prescription_reference_number"]
        
        
        if tresult.get("claim_transfer_request") is None:
            responseresult["overview"]["claimtransferbin"] = ''
            responseresult["overview"]["claimtransferpcn"] = ''
        else:
            responseresult["overview"]["claimtransferbin"] = ''
            responseresult["overview"]["claimtransferpcn"] = ''
            if "bin_number" in tresult["claim_transfer_request"]:
                responseresult["overview"]["claimtransferbin"] = tresult["claim_transfer_request"]["bin_number"]
            if "processor_control_number" in tresult["claim_transfer_request"]:
                responseresult["overview"]["claimtransferpcn"] = tresult["claim_transfer_request"]["processor_control_number"]

        
        if tresult.get("claim_transfer_response") is None:
            responseresult["overview"]["claimtransferstatus"] = ''
        else:
            responseresult["overview"]["claimtransferstatus"] = tresult["claim_transfer_response"]["transaction_response_status"]
        
        if tresult.get("transactionId") is None:
            responseresult["overview"]["claimerxtranactionid"] = ''
        else:
            responseresult["overview"]["claimerxtranactionid"] = tresult["transactionId"]
        
        responseresult["overview"]["pharmacynpi"] = tresult["claim_request"]["service_provider_id"]
        if pharmacyresult is None:
            responseresult["overview"]["pharmacyncpdp"] = ""
            responseresult["overview"]["pharmacyname"] = ""
        else:
            responseresult["overview"]["pharmacyncpdp"] = pharmacyresult["cp_pharmacy_info"][0]["pharmacyid"]
            responseresult["overview"]["pharmacyname"] = pharmacyresult["pharmacyname"]
            
        responseresult["overview"]["membercarrier"] = "FLIPT"
        
        responseresult["overview"]["memberaccount"] = ''
        responseresult["overview"]["membergroup"] = ''
        responseresult["overview"]["memberid"] = ''
        responseresult["overview"]["firstname"] = ''
        responseresult["overview"]["lastname"] = ''
        responseresult["overview"]["personcode"] = ''
        responseresult["overview"]["relationshipcode"] = ""
        responseresult["overview"]["dob"] = ''
        responseresult["overview"]["gender"] = ''
        
        if "domain_name" in tvuserresult:
            responseresult["overview"]["memberaccount"] = tvuserresult["domain_name"]
        if "group" in tvuserresult:
            responseresult["overview"]["membergroup"] = tvuserresult["group"]
        pcode = ''
        if "cardholder_id" in tresult["claim_request"]:
            pcode = str(tresult["claim_request"]["cardholder_id"])[-2:]

        if "first_name" in tvuserresult:
            responseresult["overview"]["firstname"] = tvuserresult["first_name"]
        if "last_name" in tvuserresult:
            responseresult["overview"]["lastname"] = tvuserresult["last_name"]
        
        if "person_code" in tvuserresult and pcode == tvuserresult["person_code"]:
            responseresult["overview"]["firstname"] = tvuserresult["first_name"]
            responseresult["overview"]["lastname"] = tvuserresult["last_name"]
            responseresult["overview"]["personcode"] = tvuserresult["person_code"]
            responseresult["overview"]["gender"] = tvuserresult["gender"]
            responseresult["overview"]["dob"] = tvuserresult["date_of_birth"]
                
        elif "dependents" in tvuserresult:
            for i in range(0,len(tvuserresult["dependents"])):
                if "person_code" in tvuserresult["dependents"][i] and pcode == tvuserresult["dependents"][i]["person_code"]:
                    responseresult["overview"]["firstname"] = tvuserresult["dependents"][i]["first_name"]
                    responseresult["overview"]["lastname"] = tvuserresult["dependents"][i]["last_name"]
                    responseresult["overview"]["personcode"] = tvuserresult["dependents"][i]["person_code"]
                    responseresult["overview"]["gender"] = tvuserresult["dependents"][i]["gender"]
                    responseresult["overview"]["dob"] = tvuserresult["dependents"][i]["date_of_birth"]
                    break
        """
        if "gender" in tvuserresult:
            responseresult["overview"]["gender"] = tvuserresult["gender"]
        """
        if tresult.get("claim_request") is None:
            responseresult["overview"]["memberid"] = ""
            responseresult["overview"]["personcode"] = ""
            responseresult["overview"]["relationshipcode"] = ""
            # responseresult["overview"]["dob"] = ""
        else:
            if "cardholder_id" in tresult["claim_request"]:
                responseresult["overview"]["memberid"] = tresult["claim_request"]["cardholder_id"]
            else:
                responseresult["overview"]["memberid"] = ''
            
            if "relationship_code" in tresult["claim_request"]:
                responseresult["overview"]["relationshipcode"] = tresult["claim_request"]["relationship_code"]
            else:
                responseresult["overview"]["relationshipcode"] = ''
            """
            if "person_code" in tresult["claim_request"]:
                responseresult["overview"]["personcode"] = tresult["claim_request"]["person_code"]
            else:
                responseresult["overview"]["personcode"] = ''
            
            if "date_of_birth" in tresult["claim_request"]:
                responseresult["overview"]["dob"] = tresult["claim_request"]["date_of_birth"]
            else:
                responseresult["overview"]["dob"] = ''
            """
        responseresult["overview"]["productid"] = tresult["claim_request"]["product_id"]
        responseresult["overview"]["gpicode"] = tresult["claim_request"]["gpi"]
        
        responseresult["overview"]["productquantity"] = ""
        if "quantity_dispensed" in tresult["claim_request"]:
            responseresult["overview"]["productquantity"] = tresult["claim_request"]["quantity_dispensed"]

        responseresult["overview"]["productdaysupply"] = ""
        if "days_supply" in tresult["claim_request"]:
            responseresult["overview"]["productdaysupply"] = tresult["claim_request"]["days_supply"]

        if ndcresult is None:
            responseresult["overview"]["productname"] = ""
            responseresult["overview"]["productmultisourcecode"] = ""
            responseresult["overview"]["productotcindicator"] = ""
            responseresult["overview"]["productmanufacturer"] = ""
        else:
            responseresult["overview"]["productname"] = ndcresult["drug_name"]
            responseresult["overview"]["productmultisourcecode"] = ''
            if "multi_source" in ndcresult:
                responseresult["overview"]["productmultisourcecode"] = ndcresult["multi_source"]
            responseresult["overview"]["productotcindicator"] = ''
            if "otc_indicator" in ndcresult:
                responseresult["overview"]["productotcindicator"] = ndcresult["otc_indicator"]
            responseresult["overview"]["productmanufacturer"] = ''
            if "mfg" in ndcresult:
                responseresult["overview"]["productmanufacturer"] = ndcresult["mfg"]

        responseresult["overview"]["priorauthnumber"] = ""
        if "overridenumber" in tresult.keys():
            responseresult["overview"]["priorauthnumber"] = tresult["overridenumber"]

        responseresult["overview"]["transactionid"] = ""
        if "prescription_id" in tresult.keys():
            responseresult["overview"]["transactionid"] = tresult["prescription_id"]
        
        responseresult["overview"]["othercoveragecode"] = ''
        if "other_coverage_code" in tresult["claim_request"].keys():
            responseresult["overview"]["othercoveragecode"] = tresult["claim_request"]["other_coverage_code"]
        
        responseresult["overview"]["othercoverageamount"] = ""

        responseresult["pricing"]["submittedingcost"] = ''
        if "ingredient_cost_submitted" in tresult["claim_request"].keys() and tresult["claim_request"]["ingredient_cost_submitted"] != '':
            responseresult["pricing"]["submittedingcost"] = "${}".format(tresult["claim_request"]["ingredient_cost_submitted"])

        responseresult["pricing"]["submitteddispfee"] = ''
        if "dispensing_fee_submitted" in tresult["claim_request"].keys() and tresult["claim_request"]["dispensing_fee_submitted"] != '':
            responseresult["pricing"]["submitteddispfee"] = "${}".format(tresult["claim_request"]["dispensing_fee_submitted"])
        
        responseresult["pricing"]["submittedadminfee"] = ""

        responseresult["pricing"]["submittedsalestax"] = ''
        if "percentage_sales_tax_amount_submitted" in tresult["claim_request"].keys():
            responseresult["pricing"]["submittedsalestax"] = tresult["claim_request"]["percentage_sales_tax_amount_submitted"]
        
        responseresult["pricing"]["submittedpatpay"] = ''
        if "patient_paid_amount_submitted" in tresult["claim_request"].keys() and tresult["claim_request"]["patient_paid_amount_submitted"] != '':
            responseresult["pricing"]["submittedpatpay"] = "${}".format(tresult["claim_request"]["patient_paid_amount_submitted"])
        
        responseresult["pricing"]["submittedUC"] = ''
        if "gross_amount_due" in tresult["claim_request"].keys() and tresult["claim_request"]["gross_amount_due"] != '':
            responseresult["pricing"]["submittedUC"] = "${}".format(tresult["claim_request"]["gross_amount_due"])
        if prescriptionresult is None:
            responseresult["pricing"]["calculatedingcost"] = ""
            responseresult["pricing"]["calculatedispfee"] = ""
            responseresult["pricing"]["calculatedpatpay"] = ""
            responseresult["pricing"]["calculatedtotaldue"] = ""
            responseresult["pricing"]["clientengcost"] = ""
            responseresult["pricing"]["clientdispfee"] = ""
            responseresult["pricing"]["clientpatpay"] = ""
            responseresult["pricing"]["clienttotaldue"] = ""
        else:
            responseresult["pricing"]["calculatedingcost"] = "${}".format(prescriptionresult["drug_cost"])
            responseresult["pricing"]["calculatedispfee"] = "${}".format(prescriptionresult["pharmacy_dispensing_fee"])
            responseresult["pricing"]["calculatedpatpay"] = "${}".format(prescriptionresult["employee_opc"])
            responseresult["pricing"]["calculatedtotaldue"] = "${}".format(prescriptionresult["employer_cost"])
            responseresult["pricing"]["clientengcost"] = "${}".format(prescriptionresult["drug_cost"])
            responseresult["pricing"]["clientdispfee"] = "${}".format(prescriptionresult["pharmacy_dispensing_fee"])
            responseresult["pricing"]["clientpatpay"] = "${}".format(prescriptionresult["employee_opc"])
            responseresult["pricing"]["clienttotaldue"] = "${}".format(prescriptionresult["employer_cost"])

        responseresult["pricing"]["calculatedadminfee"] = ""
        responseresult["pricing"]["calculatedsalestax"] = ""
        responseresult["pricing"]["calculatedUC"] = ""
        responseresult["pricing"]["clientadminfee"] = ""
        responseresult["pricing"]["clientsalestax"] = ""
        responseresult["pricing"]["clientUC"] = ""
        
        if tresult.get("claim_response") is None:
            responseresult["pricing"]["responseingcost"] = ""
            responseresult["pricing"]["responsedispfee"] = ""
            responseresult["pricing"]["responseadminfee"] = ""
            responseresult["pricing"]["responsesalestax"] = ""
            responseresult["pricing"]["responsepatpay"] = ""
            responseresult["pricing"]["responseUC"] = ""
            responseresult["pricing"]["responsetotaldue"] = ""

        else:
            if "ingredient_cost_paid" in tresult["claim_response"].keys() and tresult["claim_response"]["ingredient_cost_paid"] != '':
                responseresult["pricing"]["responseingcost"] = "${}".format(tresult["claim_response"]["ingredient_cost_paid"])
            else:
                responseresult["pricing"]["responseingcost"] = ''
            
            if "dispensing_fee_paid" in tresult["claim_response"].keys() and tresult["claim_response"]["dispensing_fee_paid"] != '':
                responseresult["pricing"]["responsedispfee"] = "${}".format(tresult["claim_response"]["dispensing_fee_paid"])
            else:
                responseresult["pricing"]["responsedispfee"] = ''
            
            responseresult["pricing"]["responseadminfee"] = ""
            
            if "flat_sales_tax_amount_paid" in tresult["claim_response"].keys() and tresult["claim_response"]["flat_sales_tax_amount_paid"] != '':
                responseresult["pricing"]["responsesalestax"] = "${}".format(tresult["claim_response"]["flat_sales_tax_amount_paid"])
            else:
                responseresult["pricing"]["responsesalestax"] = ''
            
            if "patient_pay_amount" in tresult["claim_response"].keys() and tresult["claim_response"]["patient_pay_amount"] != '':
                responseresult["pricing"]["responsepatpay"] = "${}".format(tresult["claim_response"]["patient_pay_amount"])
            else:
                responseresult["pricing"]["responsepatpay"] = ''
            
            responseresult["pricing"]["responseUC"] = ""
            
            if "total_amount_paid" in tresult["claim_response"].keys() and tresult["claim_response"]["total_amount_paid"] != '':
                responseresult["pricing"]["responsetotaldue"] = "${}".format(tresult["claim_response"]["total_amount_paid"])
            else:
                responseresult["pricing"]["responsetotaldue"] = ''
            
        if pharmacyresult is None:
            responseresult["pricing"]["pharmacypricetype"] = ""
            responseresult["pricing"]["pharmacymaclist"] = ""
            responseresult["pricing"]["clientmaclist"] = ""
        else:
            responseresult["pricing"]["pharmacypricetype"] = pharmacyresult["pharmprice"]
            responseresult["pricing"]["pharmacymaclist"] = pharmacyresult["cp_pharmacy_info"][0]["maclistid"]
            responseresult["pricing"]["clientmaclist"] = pharmacyresult["cp_pharmacy_info"][0]["maclistid"]
        
        if prescriptionresult is None:
            responseresult["pricing"]["pharmacyunitprice"] = ""
            responseresult["pricing"]["clientunitprice"] = ""
            responseresult["pricing"]["attribtoded"] = ""
        else:
            if "unit_price" in prescriptionresult.keys() and prescriptionresult["unit_price"] != '':
                responseresult["pricing"]["pharmacyunitprice"] = "${}".format(prescriptionresult["unit_price"])
                responseresult["pricing"]["clientunitprice"] = "${}".format(prescriptionresult["unit_price"])
            else:
                responseresult["pricing"]["pharmacyunitprice"] = ""
                responseresult["pricing"]["clientunitprice"] = ""
            
            
            if "drug_deductible_exempt" in prescriptionresult:
                if prescriptionresult["drug_deductible_exempt"].upper() == "TRUE":
                    responseresult["pricing"]["attribtoded"] = 'N'
                else:
                    responseresult["pricing"]["attribtoded"] = 'Y'
        
        responseresult["pricing"]["clientpricetype"] = ""
        responseresult["pricing"]["oop"] = ""

        return responseresult
    
    def getEligibilityReport(self, requestparams):

        headerdata = {}
        headerdata["searchvalue"] = requestparams.get(
            'searchvalue') if requestparams.get('searchvalue') != None else ""
        
        
        if headerdata["searchvalue"].isdigit():
            headerdata["searchkey"] = 'memberid'
        else:
            headerdata["searchkey"] = 'lastname'

        msgstatus,tvuserresult = self.claimportaldataprovobj.getEligibilityUserDetails(headerdata)

        custom_result = []
        if tvuserresult:
            
            for i in range(0,len(tvuserresult)):
                
                if 'dependents' in tvuserresult[i]:
                    
                    for j in range(0,len(tvuserresult[i]['dependents'])):
                        temp = {}
                        temp['fliptpersonid'] = tvuserresult[i]['dependents'][j]['flipt_person_id']
                        temp['lastname'] = tvuserresult[i]['dependents'][j]['last_name']
                        temp['firstname'] = tvuserresult[i]['dependents'][j]['first_name']
                        temp['personcode'] = tvuserresult[i]['dependents'][j]['person_code']
                        temp['dob'] = tvuserresult[i]['dependents'][j]['date_of_birth']
                        temp['fromdate'] = ''
                        temp['thrudate'] = ''
                        if 'eligibility' in tvuserresult[i]['dependents'][j]:
                            depeligibility = tvuserresult[i]['dependents'][j]['eligibility']
                            for k in range(0,len(depeligibility)):
                                temp['fromdate'] = depeligibility[k]['coverage_effective_date']
                                temp['thrudate'] = depeligibility[k]['coverage_termination_date']
                        else:
                            if 'coverage_effective_date' in tvuserresult[i]:
                                temp['fromdate'] = tvuserresult[i]['coverage_effective_date']
                            
                            if 'coverage_termination_date' in tvuserresult[i]:
                                temp['thrudate'] = tvuserresult[i]['coverage_termination_date']
                        temp['membertype'] = 'dependent'
                        temp['memberid'] = tvuserresult[i]['flipt_person_id'] + tvuserresult[i]['person_code']
                        temp['domain_name'] = tvuserresult[i]['domain_name']
                        temp['workmail'] = ''
                        if 'work_email' in tvuserresult[i]:
                            temp['workmail'] = tvuserresult[i]['work_email']
                        temp['group'] = ''
                        if 'group' in tvuserresult[i]:
                            temp['group'] = tvuserresult[i]['group']
                        custom_result.append(temp)
                temp = {}
                temp['memberid'] = tvuserresult[i]['flipt_person_id'] + tvuserresult[i]['person_code']
                temp['domain_name'] = tvuserresult[i]['domain_name']
                temp['workmail'] = ''
                if 'work_email' in tvuserresult[i]:    
                    temp['workmail'] = tvuserresult[i]['work_email']
                temp['group'] = ''
                if 'group' in tvuserresult[i]:
                    temp['group'] = tvuserresult[i]['group']
                temp['fliptpersonid'] = tvuserresult[i]['flipt_person_id']
                temp['lastname'] = tvuserresult[i]['last_name']
                temp['firstname'] = tvuserresult[i]['first_name']
                temp['personcode'] = tvuserresult[i]['person_code']
                temp['dob'] = tvuserresult[i]['date_of_birth']
                
                temp['fromdate'] = ''
                if 'coverage_effective_date' in tvuserresult[i]:
                    temp['fromdate'] = tvuserresult[i]['coverage_effective_date']
                temp['thrudate'] = ''
                if 'coverage_termination_date' in tvuserresult[i]:
                    temp['thrudate'] = tvuserresult[i]['coverage_termination_date']
                
                temp['fromdate'] = ''
                temp['thrudate'] = ''
                if 'eligibility' in tvuserresult[i]:
                    depeligibility = tvuserresult[i]['eligibility']
                    for k in range(0,len(depeligibility)):
                        if 'coverage_effective_date' in depeligibility[k]:
                            temp['fromdate'] = depeligibility[k]['coverage_effective_date']
                        if 'coverage_termination_date' in depeligibility[k]:
                            temp['thrudate'] = depeligibility[k]['coverage_termination_date']
                else:
                    if 'coverage_effective_date' in tvuserresult[i]:
                        temp['fromdate'] = tvuserresult[i]['coverage_effective_date']
                    
                    if 'coverage_termination_date' in tvuserresult[i]:
                        temp['thrudate'] = tvuserresult[i]['coverage_termination_date']

                temp['membertype'] = 'primary'

                custom_result.append(temp)
            return {"message":msgstatus,"result":custom_result}
        else:
            return {"message":msgstatus,"result":[]}


    def getEligibilityMember(self, requestparams):

        
        headerdata = {}
        headerdata["memberid"] = requestparams.get(
            'memberid') if requestparams.get('memberid') != None else ""
        headerdata["personcode"] = requestparams.get(
            'personcode') if requestparams.get('personcode') != None else ""
        headerdata["workmail"] = requestparams.get(
            'workmail') if requestparams.get('workmail') != None else ""
        headerdata["membertype"] = requestparams.get(
            'membertype') if requestparams.get('membertype') != None else ""
        headerdata["domainname"] = requestparams.get(
            'domainname') if requestparams.get('domainname') != None else ""
        
        msgstatus,tvuserresult = self.claimportaldataprovobj.getEligibilityMember(headerdata)
        if tvuserresult:
            tvresult = tvuserresult
            responseresult = {}
            
            responseresult["carrierid"] = 'FLIPT'
            responseresult["carriername"] = 'FLIPT'
            responseresult["active"] = ''
            if "active" in tvresult:
                responseresult["active"] = tvresult["active"]

            responseresult["accountid"] = ''
            responseresult["accountname"] = ''
            if "domain_name" in tvresult:
                responseresult["accountid"] = tvresult["domain_name"]
                responseresult["accountname"] = tvresult["domain_name"]
            
            responseresult["groupid"] = ''
            responseresult["groupname"] = ''
            if "group" in tvresult:
                responseresult["groupid"] = tvresult["group"]
                responseresult["groupname"] = tvresult["group"]
            
            responseresult["memberid"] = ''
            if "flipt_person_id" in tvresult:
                responseresult["memberid"] = tvresult["flipt_person_id"]
            # responseresult["coveragefromdate"] = tvresult["coverage_effective_date"]
            # responseresult["coveragetodate"] = tvresult["coverage_termination_date"]
            responseresult["firstname"] = ''
            if "first_name" in tvresult:
                responseresult["firstname"] = tvresult["first_name"]
            

            responseresult["lastname"]  = ''
            if "last_name" in tvresult:
                responseresult["lastname"] = tvresult["last_name"]
            
            responseresult["middlename"] = ''

            responseresult["personcode"] = ''
            if "person_code" in tvresult:
                responseresult["personcode"] = tvresult["person_code"]
            
            responseresult["relationshipcode"] = ''

            responseresult["gender"] = ''
            if "gender" in tvresult:
                responseresult["gender"] = tvresult["gender"]
            

            responseresult["dob"] = ''
            if "date_of_birth" in tvresult:
                responseresult["dob"] = tvresult["date_of_birth"]
            

            responseresult["address"]  = ''
            if "home_address_1" in tvresult:
                responseresult["address"] = tvresult["home_address_1"]
            

            responseresult["city"] = ''
            if "city" in tvresult:
                responseresult["city"] = tvresult["city"]
            

            responseresult["state"] = ''
            if "state" in tvresult:
                responseresult["state"] = tvresult["state"]
            

            responseresult["zip"] = ''
            if "zip" in tvresult:
                responseresult["zip"] = tvresult["zip"]
            
            responseresult["phone"] = ''

            responseresult["email"] = ''
            if "work_email" in tvresult:
                responseresult["email"] = tvresult["work_email"]
            
            
            responseresult['coveragestatus'] = ''
            if "employment_status" in tvresult:
                responseresult['coveragestatus'] = tvresult["employment_status"]

            if 'eligibility' in tvresult:
                responseresult["eligibility"] = []

                for memeliindex in range(0,len(tvresult['eligibility'])):
                    temp = {}
                    temp[tvresult['eligibility'][memeliindex]["plan_year"]] = {}

                    temp[tvresult['eligibility'][memeliindex]["plan_year"]]["planyear"] = ''
                    if "plan_year" in tvresult['eligibility'][memeliindex]:
                        temp[tvresult['eligibility'][memeliindex]["plan_year"]]["planyear"] = tvresult['eligibility'][memeliindex]["plan_year"]
                    
                    temp[tvresult['eligibility'][memeliindex]["plan_year"]]["coverageeffectivedate"] = ''
                    if "coverage_effective_date" in tvresult['eligibility'][memeliindex]:
                        temp[tvresult['eligibility'][memeliindex]["plan_year"]]["coverageeffectivedate"] = tvresult['eligibility'][memeliindex]["coverage_effective_date"]
                    
                    temp[tvresult['eligibility'][memeliindex]["plan_year"]]["coverageterminationdate"] = ''
                    if "coverage_termination_date" in tvresult['eligibility'][memeliindex]:
                        temp[tvresult['eligibility'][memeliindex]["plan_year"]]["coverageterminationdate"] = tvresult['eligibility'][memeliindex]["coverage_termination_date"]
                    
                    
                    temp[tvresult['eligibility'][memeliindex]["plan_year"]]["cobraeffectivedate"] = ''
                    if "cobra_effective_date" in tvresult['eligibility'][memeliindex]:
                        temp[tvresult['eligibility'][memeliindex]["plan_year"]]["cobraeffectivedate"] = tvresult['eligibility'][memeliindex]["cobra_effective_date"]
                    
                    temp[tvresult['eligibility'][memeliindex]["plan_year"]]["cobraterminationdate"] = ''
                    if "cobra_termination_date" in tvresult['eligibility'][memeliindex]:
                        temp[tvresult['eligibility'][memeliindex]["plan_year"]]["cobraterminationdate"] = tvresult['eligibility'][memeliindex]["cobra_termination_date"]
                    
                    responseresult["eligibility"].append(temp)                    
            else:
                responseresult["planyear"] = ""
                if "plan_year" in tvresult:
                    responseresult["planyear"] = tvresult["plan_year"]
                responseresult["coverageeffectivedate"] = ''
                if "coverage_effective_date" in tvresult:
                    responseresult["coverageeffectivedate"] = tvresult["coverage_effective_date"]
                responseresult["coverageterminationdate"] = ''
                if "coverage_effective_date" in tvresult:
                    responseresult["coverageterminationdate"] = tvresult["coverage_termination_date"]
                responseresult["cobraeffectivedate"] = ''
                if "cobra_effective_date" in tvresult:
                    responseresult["cobraeffectivedate"] = tvresult["cobra_effective_date"]
                responseresult["cobraterminationdate"] = ''
                if "cobra_termination_date" in tvresult:
                    responseresult["cobraterminationdate"] = tvresult["cobra_termination_date"]

            # responseresult["planoverride"] = 'benefit_plan_name'
            # responseresult["fromdate"] = tvresult["hire_date"]
            # responseresult["throughdate"] = tvresult["termination_date"]
            tvalueresult = {}
            tvalueresult["result"] = responseresult
            return tvalueresult   
        else:
            return {} 
    
    def updateEligibilityMember(self, requestdata):
        self.requestdata = requestdata
 
        headerdata = {}
        try:
            headerdata = eval(self.requestdata)
            if "workmail" not in headerdata:
                headerdata["workmail"] = ""
            if "personcode" not in headerdata:
                headerdata["personcode"] = ""
            if "relationshipcode" not in headerdata:
                headerdata["relationshipcode"] = ""
            if "coveragestatus" not in headerdata:
                headerdata["coveragestatus"] = ""
            if "coverageeffectivedate" not in headerdata:
                headerdata["coverageeffectivedate"] = ""
            if "coverageterminationdate" not in headerdata:
                headerdata["coverageterminationdate"] = ""
            if "cobraeffectivedate" not in headerdata:
                headerdata["cobraeffectivedate"] = ""
            if "cobraterminationdate" not in headerdata:
                headerdata["cobraterminationdate"] = ""
            
        except Exception as _:
            return {}

        updateresult = self.claimportaldataprovobj.updateEligibilityMember(
            headerdata)
        
        if updateresult:
            return {"result": True, "count": updateresult}
        return {}
