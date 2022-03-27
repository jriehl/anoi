'''Web application for A Network of Ideas.
'''

from flask import Flask, redirect, url_for
from werkzeug.exceptions import NotFound
from markupsafe import escape

from anoi import basis
from anoi.facade import get_facade


NIL = basis.ANOIReserved.NIL.value


app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('viewer', title='index'))


@app.route('/edit/<title>', methods=['GET', 'PUT'])
def editor(title):
    # TODO
    return f'<h1>Edit "{escape(title)}"...</h1>'


@app.route('/<title>')
def viewer(title):
    # TODO
    return f'''<h1>{escape(title)}</h1>
<a href='{url_for('editor', title=title)}'>Edit...</a>
'''


@app.route('/nav/<uid>')
def nav(uid: str):
    my_facade = get_facade()
    try:
        if uid.startswith('0x'):
            uid = int(uid[2:], 16)
        else:
            uid = int(uid)
        return my_facade.render_uid(uid)
    except ValueError:
        raise NotFound()


if __name__ == "__main__":
    app.run()
