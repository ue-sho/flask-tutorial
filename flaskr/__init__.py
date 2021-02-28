import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    # インスタンスの生成
    app = Flask(__name__, instance_relative_config=True)
    # appが使用する標準設定
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # init-dbはappに登録され、前のページでのrunコマンドと似たように、flaskコマンドを使用して呼び出すことができます。
    from . import db
    db.init_app(app)

    return app
