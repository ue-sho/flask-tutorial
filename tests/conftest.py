import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    # tempfile.mkstemp()は一時ファイルを作成して開き、そのfileオブジェクトとパスを返します。DATABASEのパスは上書きされて、インスタンスフォルダの代わりに、作成した一時ファイルのパスを指すようになります。パスを設定した後、データベースの表が作成されテストデータが挿入されます。テストが終了した後は、一時ファイルが閉じられ削除されます
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,  # appがテストモードであることをFlaskへ伝えます。Flaskはいくらか内部的な振る舞いを変更してテストしやすいようにし、さらに、その他の（Flaskの）拡張も自身をテストしやすくするために、この（TESTING）フラグを使用する可能性があります。
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
# app関数のfixtureによって作成されたアプリケーションのオブジェクトを使って、app.test_client()を呼び出します。テストではこのclientを使用して、サーバを実行させずに、アプリケーションへのリクエストを作成します
def client(app):
    return app.test_client()


@pytest.fixture
# app.test_cli_runner()は、アプリケーションに登録されたClickのコマンドを呼び出し可能なrunner（実行者）を作成します
def runner(app):
    return app.test_cli_runner()



class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)