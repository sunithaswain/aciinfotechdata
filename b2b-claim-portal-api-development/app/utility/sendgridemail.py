# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import sendgrid
import os
from sendgrid.helpers.mail import Email, Content, Attachment, Mail, Personalization, FileContent, FileType, FileName, Disposition, ContentId
import urllib.request as urllib
import base64
from datetime import datetime
import socket
from app.utility.bootstrap import Configs

cf = Configs.config()


class SendgridEmail:

    def __init__(self):
        self.hostname = cf.app_instance
        self.sg = sendgrid.SendGridAPIClient(api_key=cf.SENDGRID_API_KEY)

    def email_log(self, sender, receiver1, receivers, subject_, body, file_path, attached=True):

        sender = 'noreply@fliptrx.com'
        from_email = (sender, "")
        to_emails = [(receiver1, "")]
        if receivers != None:
            for i in receivers:
                to_emails.append((i, ""))

        subject = self.hostname+':'+subject_

        if len(body) == 1:
            content_ = 'Dear Admin Team,\n '+body[0]+' has started at ' + str(datetime.now(
            ))+'. We will send you a log file as soon as processing is completed. Please review the log file as soon as you receive them for exceptions and take appropriate actions.\n \n Best regards,\n FLIPT Integration Team'
        else:
            content_ = 'Dear Admin Team,\n '+body[0]+' is completed at ' + str(datetime.now(
            ))+'. Please review the attached log file for exceptions and take appropriate actions. Also run Couchbase '+body[1]+' SQL to find more information.\n \n Best regards,\n FLIPT Integration Team'

        content = Content("text/plain", content_)
        mail = Mail(from_email=from_email, to_emails=to_emails,
                    subject=subject, plain_text_content=content)

        data = None
        if attached == True:
            with open(file_path, 'rb') as f:
                data = f.read()
                f.close()
            encoded = base64.b64encode(data).decode()
            attachment = Attachment()
            attachment.file_content = FileContent(encoded)
            attachment.file_type = FileType("application/pdf")
            attachment.file_name = FileName(file_path.split('/')[-1])
            attachment.disposition = Disposition("attachment")
            attachment.content_id = ContentId("Example Content ID")
            mail.attachment = attachment

        response = self.sg.send(mail)

    def email_log_custom(self, sender, receiver1, receivers, subject_, body, file_path, attached=True):

        sender = 'noreply@fliptrx.com'
        from_email = (sender, "")
        to_emails = [(receiver1, "")]
        if receivers != None:
            for i in receivers:
                to_emails.append((i, ""))

        subject = self.hostname+':'+subject_

        content_ = 'Dear Admin Team,\n\n' + \
            body[0] + ' \n\n Best regards,\n FLIPT Integration Team'

        content = Content("text/plain", content_)
        mail = Mail(from_email=from_email, to_emails=to_emails,
                    subject=subject, plain_text_content=content)

        data = None
        if attached == True:
            with open(file_path, 'rb') as f:
                data = f.read()
                f.close()
            encoded = base64.b64encode(data).decode()
            attachment = Attachment()
            attachment.file_content = FileContent(encoded)
            attachment.file_type = FileType("application/pdf")
            attachment.file_name = FileName(file_path.split('/')[-1])
            attachment.disposition = Disposition("attachment")
            attachment.content_id = ContentId("Example Content ID")
            mail.attachment = attachment

        response = self.sg.send(mail)

    def email_log_custombody(self, sender, receiver1, receivers, subject_, body, file_path, attached=True):

        sender = 'noreply@fliptrx.com'
        from_email = (sender, "")
        to_emails = [(receiver1, "")]
        if receivers != None:
            for i in receivers:
                to_emails.append((i, ""))

        subject = self.hostname+':'+subject_

        content_ = body

        content = Content("text/plain", content_)
        mail = Mail(from_email=from_email, to_emails=to_emails,
                    subject=subject, plain_text_content=content)

        data = None
        if attached == True:
            with open(file_path, 'rb') as f:
                data = f.read()
                f.close()
            encoded = base64.b64encode(data).decode()
            attachment = Attachment()
            attachment.file_content = FileContent(encoded)
            attachment.file_type = FileType("application/pdf")
            attachment.file_name = FileName(file_path.split('/')[-1])
            attachment.disposition = Disposition("attachment")
            attachment.content_id = ContentId("Example Content ID")
            mail.attachment = attachment
        response = self.sg.send(mail)

    def email_log_zip(self, sender, receiver1, receivers, subject_, body, file_path, attached=True):

        sender = 'noreply@fliptrx.com'
        from_email = (sender, "")
        to_emails = [(receiver1, "")]
        if receivers != None:
            for i in receivers:
                to_emails.append((i, ""))

        subject = self.hostname+':'+subject_

        content_ = body

        content = Content("text/plain", content_)
        mail = Mail(from_email=from_email, to_emails=to_emails,
                    subject=subject, plain_text_content=content)

        data = None
        if attached == True:
            with open(file_path, 'rb') as f:
                data = f.read()
                f.close()
            encoded = base64.b64encode(data).decode()
            attachment = Attachment()
            attachment.file_content = FileContent(encoded)
            attachment.file_type = FileType("application/zip")
            attachment.file_name = FileName(file_path.split('/')[-1])
            attachment.disposition = Disposition("attachment")
            attachment.content_id = ContentId("Example Content ID")
            mail.attachment = attachment
        response = self.sg.send(mail)
