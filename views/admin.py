from views import Base
from collections import defaultdict
from json import dumps

class Index(Base):
    def get(self):
        data = self.db.execute('''
            SELECT domain.host, variable.name, value.value FROM value
            LEFT JOIN variable ON variable.id == value.variable
            LEFT JOIN domain ON domain.id == value.domain
        ''')

        bindings = defaultdict(dict)

        for (domain, name, value) in data:
            bindings[domain][name] = value

        self.template('_admin.html', {
            'domains': self.db.execute('''SELECT * FROM domain'''),
            'variables': self.db.execute('''SELECT * FROM variable'''),
            'values': dumps(bindings)
        })

    def post(self):
        method = self.get_argument('method')

        if method == 'host':
            value = self.get_argument('value')
            self.db.execute('''INSERT INTO domain VALUES (NULL, ?)''', (value,))
            self.db.commit()

        if method == 'bind':
            value = self.get_argument('value')
            self.db.execute('''INSERT INTO variable VALUES (NULL, ?)''', (value,))
            self.db.commit()

        if method == 'save':
            host = self.get_argument('host')
            bind = self.get_argument('bind')
            value = self.get_argument('value')
            self.db.execute('''INSERT OR REPLACE INTO value (domain, variable, value) VALUES (?, ?, ?)''', (host, bind, value))
            self.db.commit()

        self.write(dumps({
            'status': 'success'
        }))
