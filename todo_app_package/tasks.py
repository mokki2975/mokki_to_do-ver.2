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

tasks_bp = Blueprint('tasks', __name__, url_prefix='/')

@tasks_bp.route('/')
@login_required
def index():
    tasks = []
    task_form = TaskForm()

    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'newest')

    query = Task.query.filter_by(user_id=current_user.id)

    if status_filter == 'done':
        query = query.filter_by(is_completed=True)
    elif status_filter == 'active':
        query = query.filter_by(is_completed=False)

    if sort_by == 'newest':
        query = query.order_by(Task.id.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Task.id.asc())
    elif sort_by == 'alphabetical':
        query = query.order_by(Task.task.asc())
        
    tasks = query.all()

    return render_template('index.html', tasks=tasks,
                           current_status=status_filter, current_sort=sort_by,
                           task_form=task_form)

@tasks_bp.route('/add', methods=['POST'])
@login_required
def add_task():
    
    task_form = TaskForm()
    if task_form.validate_on_submit():
        task_content = task_form.task_content.data
        try:
            new_task = Task(user_id=current_user.id, task=task_content, is_completed=False)
            db.session.add(new_task)
            db.session.commit()
            flash('タスクを追加しました！', 'success')
        except Exception as e:
            flash(f'タスクの追加中にエラーが発生しました: {e}', 'error')
            print(f"エラー: {e}")
            db.session.rollback()

    else:
        for field, errors in task_form.errors.items():
            for error in errors:
                flash(f' {task_form[field].label.text} : {error}', 'error')
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/toggle/<int:task_id>')
@login_required
def toggle_task(task_id):
    
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if task:
        task.is_completed = not task.is_completed
        db.session.commit()
        flash('タスクの状態を更新しました！', 'success')
    else:
        flash('指定されたタスクが見つからないか、操作権限がありません。', 'error')
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            flash('タスクを削除しました！', 'success')
        else:
            flash('指定されたタスクが見つからないか、操作権限がありません。', 'error')
    except Exception as e:
        flash(f'タスクの削除中にエラーが発生しました: {e}', 'error')
        print(f"エラー: {e}")
        db.session.rollback()
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if task is None:
        flash('指定されたタスクが見つからないか、操作権限がありません。', 'error')
        return redirect(url_for('tasks.index'))
    
    form = EditTaskForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            task.task = form.task_content.data
            db.session.commit()
            flash('タスクを更新しました！', 'success')
            return redirect(url_for('tasks.index'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{form[field].label.text}: {error}', 'error')
            return render_template('edit.html', form=form, task=task)
    else:
        form.task_content.data = task.task
        return render_template('edit.html', form=form, task=task)

@tasks_bp.route('/api/toggle_task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task_api(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({'success': False, 'message': 'タスクが見つかりません。'}), 404

        data = request.get_json()
        if data is None or 'is_completed' not in data:
            return jsonify({'success': False, 'message': '無効なリクエストです。'}), 400

        task.is_completed = data['is_completed']
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'タスクの状態が正常に更新されました。',
            'task_id': task.id,
            'is_completed': task.is_completed
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500