from tornado.web import RequestHandler
from jinja2 import FileSystemLoader, Environment
import re
import sqlite3
import time
import datetime


#-------------------------------------------------------------------------------


import smtplib

class Mail:
    def __init__(self):
        self.server = smtplib.SMTP(settings['smtp_host'], settings['smtp_port'])
        self.server.ehlo()
        self.server.starttls()
        self.server.login(settings['user'], settings['pass'])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.server.close()

    def mail(self, message, **kwargs):
        headers = '\n'.join(': '.join(header) for header in kwargs.items())
        message = "{}\n\n{}".format(headers, message)
        self.server.sendmail(
            kwargs.get('From', settings['smtp_from']),
            kwargs.get('To', '').split(', '),
            message
        )


#-------------------------------------------------------------------------------


html = re.compile(r'<(\w+).*>', re.M)

def detecthtml(s):
    return html.search(s) is not None

def print_template(s, to, frm, subject):
    with Mail() as mail:
        mail.mail(s, **{
            'To': to,
            'From': frm,
            'Subject': subject
        })

    return ''


def datetimeformat(format):
    ctime = time.time()
    ctime = datetime.datetime.fromtimestamp(ctime)
    return ctime.strftime(format)


template = Environment(loader = FileSystemLoader(['templates/']))
template.filters['detecthtml'] = detecthtml
template.filters['strftime'] = datetimeformat
template.filters['sendmail'] = print_template


#-------------------------------------------------------------------------------


class Base(RequestHandler):
    def prepare(self):
        self.db = sqlite3.connect('data.db')
        self.db.row_factory = sqlite3.Row

    def on_finish(self):
        self.db.close()

    def template(self, name, args):
        args['xsrf'] = self.xsrf_token.decode('UTF-8')
        args['this'] = self
        self.write(template.get_template(name).render(args))

    def confirm_captcha(self):
        value = self.get_secure_cookie('captcha')
        atmpt = self.get_argument('captcha')
        return value == atmpt


from views import front, admin
