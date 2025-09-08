#デバッグ用のコード（普段は使わない）

import pytest
from todo_app_package import create_app, db
from todo_app_package.models import User
from todo_app_package.settings import TestConfig
from werkzeug.security import generate_password_hash, check_password_hash

@pytest.fixture
def client():
    app = create_app(config_class=TestConfig)
    
    with app.test_client() as client:
        with app.app_context():
            db.session.remove() # セッションを閉じる
            db.drop_all()       # テーブルを削除
            db.create_all()     # テーブルを再作成
            yield client
            db.session.remove() # テスト後もセッションを閉じる
            db.drop_all()       # テスト後もテーブルを削除

# tests/test_auth.py (test_signup 関数)
import uuid # uuidモジュールを追加

def test_signup(client):
    # 毎回ユニークなユーザー名を生成
    unique_username = f"User{uuid.uuid4().hex[:10]}" 

    response = client.post('/auth/register', data={
        'username': unique_username, # ユニークなユーザー名を使用
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    print(f"\n[DEBUG] test_signup response data: {response.data.decode('utf-8')}")

    assert response.request.path == '/auth/login'
    assert "登録が完了しました！ログインしてください。" in response.data.decode('utf-8')

    with client.application.app_context():
        user = User.query.filter_by(username=unique_username).first() # ここもユニークなユーザー名でフィルタ
        assert user is not None
        assert user.username == unique_username # ここもユニークなユーザー名でアサート
        assert check_password_hash(user.password, 'password123')

def test_login(client):
    with client.application.app_context():
        # Step 1: テストユーザーを作成し、パスワードハッシュを確認
        test_password = 'password123' # テストで使う平文パスワード
        hashed_password = generate_password_hash(test_password, method='pbkdf2:sha256')
        
        # デバッグプリントを追加
        print(f"\n[DEBUG] 生成されたハッシュパスワード: {hashed_password}")

        user = User(username='Test User', password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # DBからユーザーを再取得して、ハッシュが正しく保存されているか確認（オプション）
        retrieved_user = User.query.filter_by(username='Test User').first()
        print(f"[DEBUG] DBから取得したユーザーのハッシュ: {retrieved_user.password}")


    # Step 2: ログイン試行時のパスワードとDBのハッシュを比較
    # Flaskのcheck_password_hashが正しく動作するか確認
    # これはFlask内部で実行されるので、ここでは直接デバッグプリントできません
    
    response = client.post('/auth/login', data={
        'username': 'Test User',
        'password': test_password # 平文パスワードを渡す
    }, follow_redirects=True)

    # ログイン成功時のパス
    assert response.request.path == '/' 
    assert "ログインしました！" in response.data.decode('utf-8')

    # ログイン失敗時のパス
    response = client.post('/auth/login', data={
        'username': 'Test User',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert response.request.path == '/auth/login'
    assert "ユーザー名またはパスワードが間違っています。" in response.data.decode('utf-8')
    
def test_profile_requests_login(client):
    response = client.get('/', follow_redirects=True)
    assert response.request.path == '/auth/login'
    pass

# tests/test_auth.py (test_logout 関数)

def test_logout(client):
    with client.application.app_context():
        existing_user = User.query.filter_by(username='Test User').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print("[DEBUG] 'Test User' をテスト前に削除しました。")

        unique_logout_username = f"LogoutUser{uuid.uuid4().hex[:10]}" 
        hashed_password = generate_password_hash('password123', method='pbkdf2:sha256')
        user = User(username=unique_logout_username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
   
    login_response = client.post('/auth/login', data={'username': unique_logout_username, 'password': 'password123'}, follow_redirects=True) 
    assert login_response.request.path == '/' 
    assert "ログインしました！" in login_response.data.decode('utf-8')

    with client.session_transaction() as sess:
        # '_user_id' がセッションに存在するかどうかを確認 (Flask-Loginの内部キー)
        print(f"[DEBUG] セッション内のユーザーID (ログイン後): {sess.get('_user_id')}")
        assert '_user_id' in sess # ログインが成功していれば '_user_id' があるはず

    response = client.get('/auth/logout', follow_redirects=True)

    with client.session_transaction() as sess:
        print(f"[DEBUG] セッション内のユーザーID (ログアウト後): {sess.get('_user_id')}")
        # ログアウトが成功していれば '_user_id' はないはず
        assert '_user_id' not in sess or sess.get('_user_id') is None

    assert response.request.path == '/auth/login'
    assert "ログアウトしました。" in response.data.decode('utf-8')