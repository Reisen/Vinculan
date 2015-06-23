from views import Base
from unicodedata import normalize
import json
import os
import re


_filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')

def secure_filename(filename):
    if isinstance(filename, str):
        filename = normalize('NFKD', filename).encode('ascii', 'ignore')
        filename = filename.decode('ascii')

    for separator in (os.path.sep, os.path.altsep):
        if separator:
            filename = filename.replace(separator, ' ')

    filename = filename.split()
    filename = '_'.join(filename)
    filename = _filename_ascii_strip_re.sub('', filename)
    filename = str(filename).strip('._')

    return filename


class Serve(Base):
    def get(self, orig):
        data = self.db.execute('''
            SELECT variable.name, value.value FROM value
            LEFT JOIN variable ON variable.name == value.variable
            LEFT JOIN domain ON domain.host == value.domain
            WHERE domain.host LIKE ?
        ''', ('%{}%'.format(self.request.host.split(':', 1)[0]),)).fetchall()

        host = self.db.execute('''
            SELECT * FROM domain
            WHERE domain.host LIKE ?
        ''', ('%{}%'.format(self.request.host.split(':', 1)[0]),)).fetchone()

        orig = orig if orig else 'index'
        path = orig if '.' in orig else orig + '.html'
        path = os.path.join(host['template'], path)
        path = os.path.join('templates/', path)

        bindings = {name: value for (name, value) in data}

        if os.path.exists(path) and os.path.isfile(path) and path.endswith('.html'):
            self.template(path.split('/', 1)[1], {
                'g': bindings
            })

        else:
            self.template('index.html', {
                'g': bindings
            })


class Snippet(Base):
    def get(self):
        host = self.get_argument('host')
        variable = self.get_argument('variable')
        data = self.db.execute('''SELECT value.value FROM value WHERE value.domain = ? AND value.variable = ?''', (host, variable)).fetchone()
        self.write(json.dumps({
            'html': data['value']
        }))


class Login(Base):
    def get(self):
        self.template('_login.html', {
        })

    def post(self):
        username = self.get_argument('user')
        password = self.get_argument('pass')

        # REALLY BAD. NEED TO FIX THIS.
        auths = []
        for line in open('auths.txt', 'r'):
            auths.append(tuple(line.split()))

        print(auths)

        if (username, password) in auths:
            self.set_secure_cookie('auth', 'true')
            self.redirect('/admin')

        else:
            self.redirect('/login')
