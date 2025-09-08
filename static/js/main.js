console.log('main.jsが読み込まれました！');  //コンソールを開いたときに出力

let taskList; //グローバル変数宣言

//一連の動作をイベントリスナーとして管理
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMコンテンツが読み込まれました。');

    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    const taskForm = document.getElementById('add-task-form');
    const taskContentInput = document.querySelector('#task_content');

    taskList = document.querySelector('.space-y-3')  //タスクリストの表示
    console.log('taskList:', taskList);

    //タスク完了のイベントリスナー
    function setupEventListeners() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
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
                    body: JSON.stringify({ is_completed: isCompleted }),
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
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
        
        // 削除ボタンのイベントリスナー
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                
                console.log('クリックされたボタン:', this);
                console.log('親要素のli:', this.closest('li'));

                const taskId = this.closest('li').dataset.taskId;
                console.log('取得されたタスクID:', taskId);

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
    }
    //タスク追加のイベントリスナー
    taskForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const taskContent = taskContentInput.value;
        if (!taskContent) {
            alert('タスクを入力してください。');
            return;
        }

        fetch('/api/add_task', {
            method: 'POST',

            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            body: JSON.stringify({ task_content: taskContent }),
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('APIリクエストに失敗しました。');
        })
        .then(data => {
            if (data.success) {
                try{
                    const newTaskHtml = `
                    <li class="flex items-center justify-between p-3 bg-gray-50 rounded-md shadow-sm border border-gray-200" data-task-id="${data.task.id}">
                        <div class="flex items-center space-x-2">
                            <input type="checkbox" data-task-id="${data.task.id}" class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer">
                            <span class="text-lg">${data.task.content}</span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <a href="/edit/${data.task.id}" class="bg-gray-400 hover:bg-gray-500 text-white text-sm font-bold py-1 px-3 rounded-md transition duration-300">
                                編集
                            </a>
                            <a href="/delete/${data.task.id}" class="bg-red-500 hover:bg-red-600 text-white text-sm font-bold py-1 px-3 rounded-md transition duration-300 delete-task-btn">
                                削除
                            </a>
                        </div>
                    </li>
                `;
                taskList.insertAdjacentHTML('beforeend', newTaskHtml);

                taskContentInput.value = '';

                setupEventListeners();

                console.log('タスクが正常に画面に追加されました。');
                } catch (error) {
                    console.error('HTML生成またはDOM操作中にエラーが発生しました:', error);
                } 
            } else {
                console.error('タスクの追加に失敗:', data.message);
            } 
        })
        .catch(error => {
            console.error('通信エラー:', error);
        });
    });
});