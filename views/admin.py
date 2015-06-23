import os
from views import Base
from collections import defaultdict
from json import dumps

class Index(Base):
    def get(self):
        data = self.db.execute('''
            SELECT domain.host, variable.name, value.value FROM value
            LEFT JOIN variable ON variable.name == value.variable
            LEFT JOIN domain ON domain.host == value.domain
            ORDER BY domain.host, variable.name ASC
        ''').fetchall()

        bindings = defaultdict(dict)

        for (domain, name, value) in data:
            bindings[domain][name] = value

        self.template('_admin.html', {
            'templates': filter(lambda v: '.' not in v, os.listdir('templates/')),
            'domains': self.db.execute('''SELECT * FROM domain''').fetchall(),
            'variables': self.db.execute('''SELECT * FROM variable ORDER BY name ASC''').fetchall(),
            'values': dumps(bindings),
            'all': data
        })

    def post(self):
        method = self.get_argument('method')

        if method == 'host':
            value = self.get_argument('value')
            self.db.execute('''INSERT INTO domain VALUES (?, '')''', (value,))

            for variable in self.db.execute('''SELECT * FROM variable'''):
                self.db.execute('''INSERT INTO value (domain, variable, value) VALUES (?, ?, '')''', (value, variable['name']))

        if method == 'bind':
            value = self.get_argument('value')
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

        self.db.commit()
        self.write(dumps({
            'status': 'success'
        }))
