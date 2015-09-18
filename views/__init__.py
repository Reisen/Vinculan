from tornado.web import RequestHandler
from jinja2 import FileSystemLoader, Environment
from main import Mail
import re
import sqlite3
import time
import datetime


html = re.compile(r'<(\w+).*>', re.M)

def detecthtml(s):
    return html.search(s) is not None


def print_template(s, *args):
    with Mail() as mail:
        mail.mail(s, **dict(args))

    return ''


def datetimeformat(format):
    ctime = time.time()
    ctime = datetime.datetime.fromtimestamp(ctime)
    return ctime.strftime(format)


def update_uri(s, part):
    pass


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
        value = self.get_secure_cookie('captcha').decode('UTF-8')
        atmpt = self.get_argument('captcha')
        return value == atmpt


from views import front, admin
