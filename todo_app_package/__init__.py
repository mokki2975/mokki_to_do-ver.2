from flask import Flask
from .extensions import db, login_manager, migrate
from .models import User
from .auth import auth_bp
from .tasks import tasks_bp
from flask_migrate import Migrate
from .settings import Config, TestConfig

def create_app(config_class=Config):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tasks_bp, url_prefix='/')
    
    return app

import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    db.drop_all()
    db.create_all()

    from werkzeug.security import generate_password_hash
    test_user_username = 'testuser'
    test_user_password = 'password'

    if not User.query.filter_by(username=test_user_username).first():
        hashed_password = generate_password_hash(test_user_password)
        new_user = User(username=test_user_username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        click.echo(f'ユーザー "{test_user_username}" を追加しました。')
    else:
        click.echo(f'ユーザー "{test_user_username}" は既に存在します。')
    
    click.echo(f'データベースを初期化しました。')