# 各クラスをインポート
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy import MetaData

# 外部キーなどの制約に自動で名前を付けるための設定
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',          # インデックス
    "uq": "uq_%(table_name)s_%(column_0_name)s", # ユニーク制約
    "ck": "ck_%(table_name)s_%(constraint_name)s", # チェック制約
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s", # 外部キー
    "pk": "pk_%(table_name)s"               # 主キー
}

# データベース操作のインスタンス
db = SQLAlchemy(metadata=MetaData(naming_convention=NAMING_CONVENTION))
# ユーザー認証管理のインスタンス
login_manager = LoginManager()
# データベースのスキーマ変更を管理するためのインスタンス
migrate = Migrate()