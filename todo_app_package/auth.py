from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from .models import User
from .forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user

# ブループリントの作成
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ユーザー登録
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
    # インスタンス生成
    form = RegistrationForm()
    # バリデーション成功の場合
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = generate_password_hash(password)  # パスワードのハッシュ化
        new_user = User(username=username, _password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('登録が完了しました！ログインしてください。', 'success')
        # ログインページにリダイレクト
        return redirect(url_for('auth.login'))
    
    # GETリクエスト、またはバリデーション失敗時に登録フォームを表示
    return render_template('register.html', form=form)

# ログイン
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
    # インスタンス生成
    form = LoginForm()
    # バリデーション成功の場合
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data
        user = User.query.filter_by(username=username).first() # データベースからユーザー名でユーザーを検索

        # ユーザー、パスワードの一致の検証
        if user and check_password_hash(user._password_hash, password):
            login_user(user, remember=remember)
            flash('ログインしました！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('tasks.index'))
        else:
            # ログイン失敗時
            flash('ユーザー名またはパスワードが間違っています。', 'error')
    return render_template('login.html', form=form)

# ログアウト
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('tasks.index'))