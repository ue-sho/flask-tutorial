import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    # gは特別なオブジェクトで、リクエストごとに個別なものになります。それは、リクエストの（処理）期間中は複数の関数によってアクセスされるようなデータを格納するために使われます。connectionは（gオブジェクトに）格納されて、もしも同じリクエストの中でget_dbが2回呼び出された場合、新しいconnectionを作成する代わりに、再利用されます。
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], # current_appはリクエストを処理中のFlaskアプリケーションをさす。
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # sqlite3.Row は列のアクセス

    return g.db


def close_db(e=None):
    db = g.pop('db', None) # connectionがされていればpopされる

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    # open_resource()は、パッケージflaskrから相対的な場所で指定されたファイルを開きます
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db') # click.command()は、init_db関数を呼び出して成功時のメッセージを表示する、init-dbと呼ばれる、コマンドラインから使用できるコマンドを定義します。
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # app.teardown_appcontext()は、レスポンスを返した後のクリーンアップを行っているときに、上記の関数（close_db）を呼び出すように、Flaskへ伝えます。
    app.teardown_appcontext(close_db)
    # app.cli.add_command()は、flaskコマンドを使って呼び出すことができる新しいコマンドを追加します。
    app.cli.add_command(init_db_command)