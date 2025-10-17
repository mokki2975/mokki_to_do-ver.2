from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User

# RegistrationForm: 新規ユーザー登録用のフォーム
class RegistrationForm(FlaskForm):
    # DataRequired: 入力が必須であることを指定
    # Length: 文字列の長さの指定
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=6)])
    # EqualTo: 値の一致を検証
    confirm_password = PasswordField('パスワード（確認用）', validators=[DataRequired(), EqualTo('password', message='パスワードが一致しません。')])
    submit = SubmitField('登録する')

    # フィールド名と一致するvalidate_<フィールド名>という命名規則で自動的に実行される
    def validate_username(self, username):
        # データベースを検索し、同じユーザー名が既に存在するか確認
        # 既に存在する場合はValidationErrorを発生させ、エラーメッセージを表示
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('そのユーザー名は既に使われています。別のユーザー名を選んでください。')

# LoginForm: ログイン用のフォーム
class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    # ログイン情報を維持するかどうかのチェックボックス
    remember_me = BooleanField('ログイン情報を記憶する')
    submit = SubmitField('ログインする')

# TaskForm: タスク追加のフォーム
class TaskForm(FlaskForm):
    task_content = StringField('新しいタスクを入力', validators=[DataRequired(), Length(min=1)])
    priority = SelectField(
        '優先度',
        choices=[(1,'低'), (2,'中'), (3,'高')],
        coerce=int,
        default=1
    )
    submit = SubmitField('追加')

# EditTaskForm: タスク編集のフォーム
class EditTaskForm(FlaskForm):
    task_content = StringField('タスク内容', validators=[DataRequired(), Length(min=1)])
    priority = SelectField(
        '優先度',
        choices=[(1, '低'), (2, '中'), (3, '高')],
        coerce=int,
    )
    is_completed = BooleanField('完了済み')
    submit = SubmitField('更新')