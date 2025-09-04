console.log('main.jsが読み込まれました！');

const checkboxes = document.querySelectorAll('input[type="checkbox"]');
const csrfToken = document.querySelector('input[name="csrf_token"]').value;
const deleteButtons = document.querySelectorAll('.delete-task-btn');

console.log('見つかった削除ボタン:', deleteButtons);  

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', (event) => {
        const taskId = event.target.dataset.taskId;
        const isCompleted = event.target.checked;

        fetch(`/api/toggle_task/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            body: JSON.stringify({is_completed: isCompleted}),
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            if(data.success) {
                const taskSpan  = event.target.parentElement.querySelector('span');
                if (data.is_completed) {
                    taskSpan.classList.add('task-done');
                } else {
                    taskSpan.classList.remove('task-done');
                }
                console.log(`タスクID: ${data.task_id}の完了状態が ${data.is_completed} に変更されました。`);
            } else {
                console.error('API呼び出しに失敗しました:', data.message);
            }
        })
        .catch(error => {
            console.error('通信エラー:', error);
        });
    });
});

deleteButtons.forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();
        
        // ログを追加して、取得したHTML要素とtaskIdを確認する
        console.log('クリックされたボタン:', this);
        console.log('親要素のli:', this.closest('li'));

        const taskId = this.closest('li').dataset.taskId;
        console.log('取得されたタスクID:', taskId);

        // taskIdがundefinedだった場合はここで処理を中断する
        if (!taskId) {
            console.error("タスクIDが取得できませんでした。");
            return;
        }
        if (confirm('本当にこのタスクを削除しますか?')) {
            fetch(`/api/delete_task/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRF-Token': csrfToken
                }
            })
            .then(response => {
                if(response.ok) {
                    this.closest('li').remove();
                    console.log(`タスクID: ${taskId} を削除しました。`);
                } else {
                    console.error(`削除失敗`);
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.message) {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('通信エラー:', error);
                alert('削除中にエラーが発生しました。');
            });
        }
    });
});