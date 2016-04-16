import os
from views import Base
from collections import defaultdict
from json import dumps

class Index(Base):
    def get(self):
        if not self.get_secure_cookie('auth'):
            self.redirect('/login')

        data = self.db.execute('''
            SELECT domain.host, domain.template, variable.name, value.value FROM value
            LEFT JOIN variable ON variable.name == value.variable
            LEFT JOIN domain ON domain.host == value.domain
            ORDER BY domain.host, variable.name ASC
        ''').fetchall()

        bindings = defaultdict(dict)

        for (domain, template, name, value) in data:
            bindings[domain]['template'] = template
            bindings[domain][name] = value

        self.template('_admin.html', {
            'templates': filter(lambda v: '.' not in v, os.listdir('templates/')),
            'domains': self.db.execute('''SELECT * FROM domain''').fetchall(),
            'variables': self.db.execute('''SELECT * FROM variable ORDER BY name ASC''').fetchall(),
            'values': dumps(bindings),
            'order': self.get_argument('order', False),
            'direction': self.get_argument('direction', 0),
            'all': data
        })

    def post(self):
        method = self.get_argument('method')

        if method == 'host':
            value = self.get_argument('value')
            if value != '':
                self.db.execute('''INSERT INTO domain VALUES (?, '')''', (value,))

                for variable in self.db.execute('''SELECT * FROM variable'''):
                    self.db.execute('''INSERT INTO value (domain, variable, value) VALUES (?, ?, '')''', (value, variable['name']))

        if method == 'bind':
            value = self.get_argument('value')
            if value != '':
                self.db.execute('''INSERT INTO variable VALUES (?)''', (value,))

                for domain in self.db.execute('''SELECT * FROM domain'''):
                    self.db.execute('''INSERT INTO value (domain, variable, value) VALUES (?, ?, '')''', (domain['host'], value))

        if method == 'save':
            host = self.get_argument('host')
            bind = self.get_argument('bind')
            value = self.get_argument('value')
            self.db.execute('''INSERT OR REPLACE INTO value (domain, variable, value) VALUES (?, ?, ?)''', (host, bind, value))

        if method == 'template':
            host = self.get_argument('host')
            value = self.get_argument('value')
            self.db.execute('''UPDATE domain SET template = ? WHERE host = ?''', (value, host))

        if method == 'delete-site':
            host = self.get_argument('value')
            self.db.execute('''DELETE FROM domain WHERE host = ?''', (host,))
            self.db.execute('''DELETE FROM value WHERE value.domain = ?''', (host,))

        if method == 'delete-variable':
            variable = self.get_argument('value')
            self.db.execute('''DELETE FROM value WHERE value.variable = ?''', (variable,))
            self.db.execute('''DELETE FROM variable WHERE name = ?''', (variable,))

        self.db.commit()
        self.write(dumps({
            'status': 'success'
        }))

class SubIndex(Base):
    def get(self, domain):
        try:
            if not self.get_secure_cookie('auth'):
                self.redirect('/login')

            data = self.db.execute('''
                SELECT domain.host, page.name as template, pagevar.name, pageval.value FROM pageval
                LEFT JOIN pagevar ON pagevar.name == pageval.variable AND pagevar.page == pageval.page
                LEFT JOIN domain ON domain.host == pageval.domain
                ORDER BY page.name, variable.name ASC
            ''').fetchall()

            bindings = defaultdict(dict)

            for (domain, page, name, value) in data:
                bindings[page][name] = value

            self.template('_admin.html', {
                'templates': filter(lambda v: '.' not in v, os.listdir('templates/')),
                'domains': self.db.execute('''SELECT * FROM page''').fetchall(),
                'variables': self.db.execute('''SELECT * FROM pagevar ORDER BY name ASC''').fetchall(),
                'values': dumps(bindings),
                'order': self.get_argument('order', False),
                'direction': self.get_argument('direction', 0),
                'all': data
            })

        except Exception as e:
            self.write(str(e))


class SubDIndex:
    def get(self, domain):
        try:
            if not self.get_secure_cookie('auth'):
                self.redirect('/login')

            variables = set()

            data = self.db.execute('''
                SELECT page, variable, value FROM page
                WHERE domain = ?
                ORDER BY page, variable ASC
            ''', (domain,)).fetchall()

            bindings = defaultdict(dict)
        
            for (page, variable, value) in data:
                bindings[page][variable] = value
                variables.add(variable)

            self.template('_admin.html', {
                'templates': filter(lambda v: '.' not in v, os.listdir('templates/')),
                'domains': self.db.execute('''SELECT * FROM domain''').fetchall(),
                'variables': variables,
                'values': dumps(bindings),
                'order': self.get_argument('order', False),
                'direction': self.get_argument('direction', 0),
                'all': data
            })

        except Exception as e:
            self.write('Exception: ' + str(e))

        #self.template('_subadmin.html', {
        #    'templates': filter(lambda v: '.' not in v, os.listdir('templates/')),
        #    'values': dumps(bindings),
        #    'order': self.get_argument('order', False),
        #    'direction': self.get_argument('direction', 0),
        #    'all': data
        #})

    def post(self, domain):
        method = self.get_argument('method')

        if method == 'host':
            value = self.get_argument('value')
            if value != '':
                self.db.execute('''INSERT INTO page VALUES (?, '')''', (value,))

                for variable in self.db.execute('''SELECT * FROM variable'''):
                    self.db.execute('''INSERT INTO value (domain, variable, value) VALUES (?, ?, '')''', (value, variable['name']))

        if method == 'bind':
            value = self.get_argument('value')
            if value != '':
                self.db.execute('''INSERT INTO variable VALUES (?)''', (value,))

                for domain in self.db.execute('''SELECT * FROM domain'''):
                    self.db.execute('''INSERT INTO value (domain, variable, value) VALUES (?, ?, '')''', (domain['host'], value))

        if method == 'save':
            host = self.get_argument('host')
            bind = self.get_argument('bind')
            value = self.get_argument('value')
            self.db.execute('''INSERT OR REPLACE INTO value (domain, variable, value) VALUES (?, ?, ?)''', (host, bind, value))

        if method == 'template':
            host = self.get_argument('host')
            value = self.get_argument('value')
            self.db.execute('''UPDATE domain SET template = ? WHERE host = ?''', (value, host))

        if method == 'delete-site':
            host = self.get_argument('value')
            self.db.execute('''DELETE FROM domain WHERE host = ?''', (host,))
            self.db.execute('''DELETE FROM value WHERE value.domain = ?''', (host,))

        if method == 'delete-variable':
            variable = self.get_argument('value')
            self.db.execute('''DELETE FROM value WHERE value.variable = ?''', (variable,))
            self.db.execute('''DELETE FROM variable WHERE name = ?''', (variable,))

        self.db.commit()
        self.write(dumps({
            'status': 'success'
        }))