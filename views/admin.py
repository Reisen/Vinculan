import os
from views import Base
from collections import defaultdict
from json import dumps

class Index(Base):
    def get_rows(self, group = None):
        group = group or self.get_argument('group')
        self.write(dumps({
            'data': [
                {'path': key['path']} for key in self.db.execute('''
                    SELECT path FROM page WHERE grouping = ?
                ''', (group,)).fetchall()
            ]
        }))

    def get_variables(self, group = None, path = None):
        group = group or self.get_argument('group')
        path = path or self.get_argument('path')
        paths = list(filter(bool, path.split('/')))

        # Resolve time...
        variables = {}

        # Globals
        group_variables = self.db.execute('''
            SELECT * FROM variable
            WHERE path = ? AND path NOT IN (SELECT path FROM page)
        ''', (group,)).fetchall()

        for var in group_variables:
            variables[var['name']] = var['value']

        # Page Variables
        page_variables = self.db.execute('''
            SELECT * FROM variable
            WHERE path = ?
        ''', (path,)).fetchall()

        for var in page_variables:
            variables[var['name']] = var['value']

        # Get subpages.
        pages = self.db.execute('''
            SELECT * FROM page WHERE path LIKE ?
        ''', (path + '%',)).fetchall()

        self.write(dumps({
            'variables': sorted([{'name': k, 'value': v} for (k, v) in variables.items()], key = lambda v: v['name']),
            'pages': [page['path'][len(path):] + '/' for page in pages]
        }))

    def add_group(self):
        name = self.get_argument('name')
        self.db.execute('INSERT INTO grouping VALUES (?)', (name,))
        self.db.commit()
        self.write(dumps({
            'data': [
                {'name': key['name']} for key in self.db.execute('''
                    SELECT name FROM grouping
                ''').fetchall()
            ]
        }))

    def add_row(self):
        path = self.get_argument('path')
        group = self.get_argument('group')
        self.db.execute('INSERT INTO page VALUES (?, ?, ?)', (path, None, group))
        self.db.commit()
        self.get_rows(group)

    def add_variable(self):
        variable = self.get_argument('variable')
        group = self.get_argument('group')
        path = self.get_argument('path', None)
        value = self.get_argument('value', None)
        path = path if path else group
        self.db.execute('INSERT INTO variable VALUES (?, ?, ?)', (path, variable, value))
        self.db.commit()
        self.write(dumps({}))

    def get(self, method):
        try:
            data = {
                'rows': lambda: self.get_rows(),
                'variables': lambda: self.get_variables(),
                'add_group': lambda: self.add_group(),
                'add_variable': lambda: self.add_variable(),
                'add_row': lambda: self.add_row()
            }[method]()

        except Exception as e:
            print('Error: ', e)
            self.template('_admin2.html', {
                'groups': [{'name': key['name']} for key in self.db.execute('SELECT name FROM grouping').fetchall()],
                'group': self.get_argument('group', '')
            })

    def post(self, method):
        self.get(method)



























class OIndex(Base):
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
                SELECT page.page as host, page.domain, pagevar.name, pageval.value FROM pageval
                LEFT JOIN pagevar ON pagevar.name == pageval.variable AND pagevar.domain = pageval.domain
                LEFT JOIN page ON page.page == pageval.page
                WHERE pageval.domain = ?
                ORDER BY page.page, pagevar.name ASC
            ''', (domain,)).fetchall()

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
