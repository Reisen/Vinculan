from tornado.web import RequestHandler
from jinja2 import FileSystemLoader, Environment
import sqlite3


template = Environment(loader = FileSystemLoader(['templates/']))


class Base(RequestHandler):
    def prepare(self):
        self.db = sqlite3.connect('data.db')
        self.db.row_factory = sqlite3.Row

    def on_finish(self):
        self.db.close()

    def template(self, name, args):
        args['xsrf'] = self.xsrf_token.decode('UTF-8')
        self.write(template.get_template(name).render(args))


from views import front, admin
