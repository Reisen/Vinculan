from views import Base
from unicodedata import normalize
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
        orig = orig if orig else 'index'
        path = orig if '.' in orig else orig + '.html'
        path = os.path.join('templates/', path)
        data = self.db.execute('''
            SELECT variable.name, value.value FROM value
            LEFT JOIN variable ON variable.id == value.variable
            LEFT JOIN domain ON domain.id == value.domain
            WHERE domain.host LIKE ?
        ''', ('%{}%'.format(self.request.host),))

        bindings = {name: value for (name, value) in data}

        if os.path.exists(path) and os.path.isfile(path):
            self.template(orig + '.html', {
                'g': bindings
            })

        else:
            self.template('index.html', {
                'g': bindings
            })
