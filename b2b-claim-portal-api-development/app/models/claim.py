from datetime import datetime


class Claim:

    def __init__(self):
        self.auth_id = ''
        self.startDate = datetime.now().isoformat()
        self.createDate = datetime.now().isoformat()
        self.updateDate = datetime.now().isoformat()
        self.endDate = None
        self.ClaimRequest = None
        self.ClaimResponse = None
        self.responseCode = None
        self.message = None
        self.sequenceNumber = None
        self.type = 'claim'
        self.requestData = None
        self.transactionId = ''
