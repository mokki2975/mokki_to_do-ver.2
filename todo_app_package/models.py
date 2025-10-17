from .extensions import db
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from datetime import datetime

# Userモデル: ユーザー情報を格納(db.Model, UserMixinの継承)
class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(120), nullable=False)

    # tasks: Taskモデルのリストを保持するためのリレーション（'Task'は関連するモデルの名前）
    # backref='user'で、Userオブジェクトにアクセス可
    # lazy=True は、関連するデータが必要になったときにロードすることを示す
    # cascade='all, delete-orphan' は、ユーザーが削除されたときに紐づくタスクもすべて削除することを示す
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')

    # オブジェクトを文字列で表現するためのメソッド
    def __repr__(self):
        return f'<User {self.username}>'

# Taskクラス: タスク情報を格納(db.Modelの継承)
class Task(db.Model):
    # id: 主キー
    # user_id: 外部キー、Userモデルのid参照
    # task: タスク内容の格納
    # is_completed: タスク完了、未完了を示す真偽値(デフォルトはFalse)
    # priority: タスクの優先度表示
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task = db.Column(db.String(120), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # オブジェクトを文字列で表現するためのメソッド
    def __repr__(self):
        return f'<Task {self.task} (Done: {self.is_completed})>'