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
    try:
        if uid.startswith('0x'):
            uid = int(uid[2:], 16)
        else:
            uid = int(uid)
    except ValueError:
        raise NotFound()
    my_facade = get_facade()
    uid_to_html = my_facade.uid_to_html
    space = my_facade.space
    if not space.is_valid(uid):
        raise NotFound()
    iter_0 = ((uid_to_html(key), uid_to_html(space.cross(uid, key)))
        for key in sorted(space.get_keys(uid)))
    nav_iter = ((key if len(key) > 1 else f'"{key}"', value)
        for key, value in iter_0)
    navbar = ''.join(f'<li>{key} : {value}</li>' for key, value in nav_iter)
    contents = ''.join(my_facade.uid_to_html(child)
        for child in space.get_content(uid))
    title = f'UID {uid} ({hex(uid)})'
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
  </head>
  <body>
    <h1>{title}</h1>
    <ul>{navbar}</ul>
    <p>{contents}</p>
  </body>
</html>
'''

if __name__ == "__main__":
    app.run()
