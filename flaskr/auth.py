import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # sessionは、リクエストを跨いで格納されるデータのdictです。検証が成功したときは、ユーザのidは新しいsessionに格納されます。そのデータはブラウザへ送信されるcookieに格納され、それからブラウザは以降のリクエストで（cookieを）送信し返します。Flaskはデータを改ざんできないようにするために、安全にデータを署名します。
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# bp.before_app_request()はどのURLがリクエストされたかに関わらず、viewの関数の前に実行する関数を登録します。load_logged_in_userは、ユーザidがsessionに格納されているかチェックし、それからデータベースからユーザのデータを取得し、それをリクエストの期間中は存続するg.userへ格納します。もしユーザidが（セッションに）ない場合、もしくはそのidが（データベースに）存在しない場合、g.userはNoneになります。
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# このdecoratorは適用した元のview（の関数）を包み込む（wrap）、新しいviewの関数を返します。その新しい関数はユーザ情報が読み込まれているかチェックして、読み込まれていない場合はログインページへリダイレクトします。もしユーザ情報が読み込まれている場合は、元のviewが呼び出されて通常どおりに続けます。ブログのviewを作成するとき、このdecoratorを使用していきます。
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # url_for()関数はviewの名前と引数に基づいて対応するURLを生成します。viewに関連付けられた名前はエンドポイントとも呼ばれ、標準設定ではviewの関数の名前と同じになります。
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view