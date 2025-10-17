from flask import Flask
import os
from .extensions import db, login_manager, migrate
from .models import User
from .auth import auth_bp
from .tasks import tasks_bp
from .settings import Config
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import CSRFProtect
import click
from flask.cli import with_appcontext

# CSRF保護のインスタンス作成
csrf = CSRFProtect()

def create_app(config_class=Config):
    # Flaskアプリケーションインスタンスを作成
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 拡張機能をアプリケーションインスタンスに紐づけ
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # ログインマネージャーの設定
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'ログインが必要です。'
    login_manager.login_message_category = 'info'
    
    # ユーザーをロードするコールバック
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # ユーザーIDに基づく
    
    # ブループリント登録
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tasks_bp, url_prefix='/')

    with app.app_context():
        
        pass # 現状特に処理なし

    
    return app 

# 'flask init-db' コマンド用の設定
@click.command('init-db')
@with_appcontext
def init_db_command():
    # データベース作成
    db.create_all()

    test_user_username = os.environ.get('TEST_USER_USERNAME', 'testuser') # 仮の値
    test_user_password = os.environ.get('TEST_USER_PASSWORD', 'password') # 仮の値

    # ユーザーが存在しない場合のみ追加
    if not User.query.filter_by(username=test_user_username).first():
        hashed_password = generate_password_hash(test_user_password)
        new_user = User(username=test_user_username, _password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        click.echo(f'ユーザー "{test_user_username}" を追加しました。')
    else:
        click.echo(f'ユーザー "{test_user_username}" は既に存在します。')

    # 完了メッセージ
    click.echo(f'データベースを初期化しました。')