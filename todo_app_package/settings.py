import os

# Configクラス: アプリケーションの一般的な設定
class Config:
    # DATABASE_URI: 環境変数からデータベースURL取得(なければデフォルト値)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:testpass123@db:5432/tododb')

    # SQALCHEMY_DATABASE_URI: SQAlchemyが使用するデータベース接続文字列
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    # SQLALCHEMY_TRACK_MODIFICATIONS: オブジェクト変更の追跡(メモリ消費を抑えるため、Falseに設定するのが一般的)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQALCHEMY_ENGINE_OPTIONS: 接続オプションの分離
    SQALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "options": "-c client_encoding=UTF8"
        }
    }

    # SECRET_KET: 秘密鍵(環境変数から取得)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_needs_to_be_longer_and_random')

# TestConfigクラス: テスト環境向けの設定を定義(Configクラスを継承)
class TestConfig(Config):
    TESTING = True
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 警告を避けるため
    
    WTF_CSRF_ENABLED = False 
    SECRET_KEY = 'test_secret_key_for_testing'