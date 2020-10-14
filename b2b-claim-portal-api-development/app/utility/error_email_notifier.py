import logging
from app.utility.sendgridemail import SendgridEmail
from app.utility.bootstrap import Configs


class EmailNotificationHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        logfile = open('Log.log', 'a')
        logfile.write(str(record) + '\r\n')

        if record.levelname == 'ERROR':
            emailobj = SendgridEmail()
            emailobj.email_log_custom('noreply@fliptrx.com', 'dwagle@fliptrx.com', None,
                                      'Claim Processing Error', [str(record)], None, False)

        logfile.close()
