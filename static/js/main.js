console.log("main.jsが読み込まれました！");

document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

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
                body: JSON.stringify({ is_completed: isCompleted}),
            })
            .then(response => {
                if (response.ok) {
                    return response.json()
                }
                throw new Error('Network response was not ok.');
            })
            .then(data => {
                if (data.success) {
                    const taskSpan = event.target.parentElement.querySelector('span');
                    if (data.is_completed) {
                        taskSpan.classList.add('task-done');
                    } else {
                        taskSpan.classList.remove('task-done');
                    }
                    console.log(`タスクID: ${data.task_id} の完了状態が ${data.is_completed} に変更されました。`);
                } else {
                    console.error('API呼び出しに失敗しました:', data.message);
                }  
            })
            .catch(error => {
                console.error('通信エラー:', error);
            });
        });
    });
});