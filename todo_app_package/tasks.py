from flask import (
    Blueprint, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    session, 
    jsonify,
)
from .extensions import db
from .models import Task
from .forms import TaskForm, EditTaskForm
from flask_login import login_required, current_user

# ブループリント化
tasks_bp = Blueprint('tasks', __name__, url_prefix='/')

# 現状の取得
@tasks_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = TaskForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        # 新しいタスクを作成
        new_task = Task(
            task=form.task_content.data,  # フォームのフィールド名に合わせる
            priority=form.priority.data,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        flash('タスクが追加されました！', 'success')
        return redirect(url_for('tasks.index'))

    # GETリクエスト時はタスク一覧を取得
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    # 現在のフィルターやソート情報があれば渡す
    current_status = request.args.get('status', 'all')
    current_sort = request.args.get('sort', 'newest')

    return render_template(
        'tasks.html',
        task_form=form,  # tasks.html で参照する変数名に合わせる
        tasks=tasks,
        current_status=current_status,
        current_sort=current_sort
    )

# タスク初期化を、API経由で行う
@tasks_bp.route("/tasks/init", methods=["GET"])
@login_required
def init_tasks_api():
    #パラメータ取得
    filter_status = request.args.get("filter")
    sort_key = request.args.get("sort", "id")

    #ユーザーで絞込
    query = Task.query.filter_by(user_id=current_user.id)

    #フィルター適用
    if filter_status == "completed":
        query = query.filter_by(is_completed=True)
    elif filter_status == "incomplete":
        query = query.filter_by(is_completed=False)

    #ソート適用
    if sort_key == "priority":
        query = query.order_by(Task.priority.desc())
    elif sort_key == "title":
        query = query.order_by(Task.task.asc())
    else:
        query = query.order_by(Task.id.asc())

    #JSONで返す
    tasks = query.all()
    tasks_json = [
        {
            "id": t.id,
            "content": t.task, 
            "is_completed": t.is_completed, 
            "priority": t.priority
        }
        for t in tasks
    ]
    return jsonify(tasks_json), 200

# タスクの完了状態を、API経由で切り替え
@tasks_bp.route('/api/toggle_task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task_api(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            # タスクが見つからない場合はJSON形式でエラーを返す
            return jsonify({'success': False, 'message': 'タスクが見つかりません。'}), 404

        data = request.get_json()
        # リクエストボディが不正な場合はエラーを返す
        if data is None or 'is_completed' not in data:
            return jsonify({'success': False, 'message': '無効なリクエストです。'}), 400

        # タスクの状態を更新し、データベースをコミット
        task.is_completed = data['is_completed']
        db.session.commit()

        # 成功した場合は更新されたタスク情報をJSONで返す
        return jsonify({
            'success': True,
            'message': 'タスクの状態が正常に更新されました。',
            'task_id': task.id,
            'is_completed': task.is_completed
        })
    except Exception as e:
        # エラー発生時はロールバック
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# タスクをAPI経由で削除
@tasks_bp.route('/api/delete_task/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task_api(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            # タスクが見つからない場合はJSON形式でエラーを返す
            return jsonify({'success':  False, 'message': 'タスクが見つかりません。'}), 404
        
        # タスクをデータベースから削除
        db.session.delete(task)
        db.session.commit()
        # 成功した場合は成功メッセージをJSONで返す
        return jsonify({'success': True, 'message': 'タスクが正常に削除されました。'}), 200
    except Exception as e:
        # エラー発生時はロールバック
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 新しいタスクをAPI経由で追加
@tasks_bp.route('/api/add_task', methods=['POST'])
@login_required
def add_task_api():
    # フォームを使ってデータの検証
    form = TaskForm()

    # リクエストボディからタスク内容を取得
    data = request.get_json()
    if data:
        form.task_content.content = data.get('task_content')
        form.priority.data = int(data.get('priority'))

    if form.validate():
        try:
             # 新しいタスクを作成し、データベースに追加
            new_task = Task(
                user_id=current_user.id, 
                task=content.strip(), 
                is_completed=False,
                priority=priority
            )
            db.session.add(new_task)
            db.session.commit()

            # 成功した場合は新しく追加されたタスク情報をJSONで返す
            return jsonify({
                'success': True,
                'message': 'タスクが正常に追加されました。',
                'task': {
                    'id': new_task.id,
                    'content': new_task.task,
                    'is_completed': new_task.is_completed,
                    'priority': new_task.priority
                }
            }), 201

        except Exception as e:
            # エラー発生時はロールバック
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    else:
        # フォームのバリデーションエラーを返す
        first_error = next(iter(form.errors.values()))[0]
        return jsonify({'success': False, 'message': 'タスクの内容が入力されていません。'}), 400
       
# タスク編集のルート
# GETリクエスト: 編集フォームを表示
# POSTリクエスト: フォームのデータでタスク更新
@tasks_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    
    # ユーザーIDとタスクIDでタスクを検索
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if task is None:
        flash('指定されたタスクが見つからないか、操作権限がありません。', 'error')
        return redirect(url_for('tasks.index'))
    
    form = EditTaskForm()

    if request.method == 'POST':
        # バリデーション成功の場合、フォームのデータでタスクの内容を更新
        if form.validate_on_submit():
            task.task = form.task_content.data
            task.priority = form.priority.data
            task.is_completed = form.is_completed.data
            db.session.commit()
            flash('タスクを更新しました！', 'success')
            return redirect(url_for('tasks.index'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{form[field].label.text}: {error}', 'error')
            return render_template('edit.html', form=form, task=task)
    else:
        # GETリクエストの場合、既存のタスク内容をフォームにセット
        form.task_content.data = task.task
        form.priority.data = task.priority
        form.is_completed.data = task.is_completed
        return render_template('edit.html', form=form, task=task)