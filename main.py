from tornado.ioloop import IOLoop
from tornado.web import Application, url
from views import *
import os


settings = {
    'smtp_host': '',
    'smtp_port': 587,
    'smtp_user': '',
    'smtp_pass': '',
    'smtp_from': '',
    'cookie_secret': b'\r\xc7\xa0\x1d:\xa32\x12\x82q\x89\x8d\xe9ZP1G\xe2f\xa0\x83\x0bB\xa99\x11e\x1a^\xd9\x16)',
    'xsrf_cookies': True,
    'static_path': os.path.join(os.path.dirname(__file__), 'assets'),
    'autoreload': True,
    'url_map': [
        url(r'/admin/?',   admin.Index),
        url(r'/snippet/?', front.Snippet),
        url(r'/login/?',   front.Login),
        url(r'/captcha/?', front.Captcha),
        url(r'/(.+?)?/?',  front.Serve),
    ]
}


#-------------------------------------------------------------------------------


if __name__ == '__main__':
    with open('schema.sql') as f:
        import sqlite3
        db = sqlite3.connect('data.db')
        db.executescript(f.read())

    app = Application(settings['url_map'], **settings)

    # Overwrite the Mod Handlers thanks to Tornado being opinionated.
    mod_handlers = []

    for handler, rules in app.handlers:
        handlers = []
        for rule in rules:
            if 'robots' not in rule.regex.pattern and 'favicon' not in rule.regex.pattern:
                handlers.append(rule)

        mod_handlers.append((handler, handlers))

    app.handlers = mod_handlers

    app.listen(8001)
    IOLoop.current().start()
