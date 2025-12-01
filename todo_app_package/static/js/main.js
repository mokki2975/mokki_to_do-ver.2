console.log('%cmain.js読み込み', 'color:green; font-weight:bold;');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMロード完了');

    // CSRFトークンを取得
    const csrfTokenElement = document.querySelector('input[name="csrf_token"]');
    const csrfToken = csrfTokenElement ? csrfTokenElement.value : null;

    // IDで主要なDOM要素を取得
    const taskForm = document.getElementById('add-task-form');   // タスク追加フォーム
    const taskContentInput = document.getElementById('task_content'); // タスク内容入力フィールド
    const taskPriorityInput = document.getElementById('task_priority'); // 優先度選択フィールド
    const taskList = document.querySelector('.space-y-3'); // タスクリストのコンテナ (UL要素)

    // トースト通知 (画面右上に表示される一時的なメッセージ) を表示する関数
    function showToast(msg, type="success") {
        const existingToast = document.querySelector('.todo-toast');
        if (existingToast) existingToast.remove(); // 既存のトーストがあれば即座に削除
        
        const toast = document.createElement("div");
        // Tailwind CSSでトーストのスタイル、位置、アニメーションを設定
        toast.className = `todo-toast fixed top-5 right-5 px-4 py-2 rounded-lg shadow-lg text-white z-50 transition-all transform duration-300 translate-x-full opacity-0 
            ${type==="success"?"bg-green-500":"bg-red-500"}`;
        toast.innerText = msg;
        document.body.appendChild(toast);

        // トーストを表示 (translate-x-fullからtranslate-x-0へ)
        setTimeout(() => {
            toast.classList.remove("translate-x-full", "opacity-0");
            toast.classList.add("translate-x-0", "opacity-100");
         }, 10); // ごくわずかな遅延

        // トーストを非表示にし、DOMから削除
        setTimeout(() => {
            // 1. 非表示アニメーションを開始 (translate-x-fullへ戻す)
            toast.classList.remove("translate-x-0", "opacity-100");
            toast.classList.add("translate-x-full", "opacity-0");
            
            // 2. アニメーション完了を待って、要素をDOMから完全に削除
            setTimeout(() => {
                toast.remove();
            }, 300); // CSSのduration-300msに合わせる
            
         }, 3000); // 3秒後に非表示アニメーションを開始
    }

    // 優先度 (1, 2, 3) に基づいて、色とラベルを含むHTMLバッジを生成する
    function getPriorityBadge(priority) {
        const colors={3:"bg-red-500",2:"bg-yellow-500",1:"bg-green-500"}; // 優先度3=高(赤), 1=低(緑)
        const labels={3:"高",2:"中",1:"低"}; // 優先度ラベル
        // 色とラベルを適用したspanタグを返す
        return `<span class="text-white text-xs font-bold px-2 py-1 rounded ${colors[priority]||"bg-gray-400"}">${labels[priority]||"不明"}</span>`;
    }

    // サーバーから受け取ったデータに基づいてタスクのHTML要素（<li>）を生成する
    function createTaskListItem(task) {
        const isCompleted = task.is_completed;
        const textClass = isCompleted ? 'line-through text-gray-400' : '';
        const badgeHtml = getPriorityBadge(task.priority); // バッジHTMLを生成

        const editUrl = `/edit/${task.id}`;

        // 生成したタスク要素を返す
        return `
            <li class="flex items-center justify-between p-3 bg-white rounded-md shadow border" data-task-id="${task.id}">
                <div class="flex items-center space-x-2">
                    <input type="checkbox" data-task-id="${task.id}" ${isCompleted ? 'checked' : ''} class="h-4 w-4 rounded border-gray-300 text-blue-600 cursor-pointer">
                    <span class="task-text text-lg ${textClass}">${task.content}</span>
                    ${badgeHtml}
                </div>
                <div class="flex items-center space-x-2">
                    <a href="${editUrl}" class="bg-gray-400 hover:bg-gray-500 text-white px-2 py-1 rounded-md text-sm">編集</a>
                    <a href="javascript:void(0)" class="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded-md text-sm delete-task-btn">削除</a>
                </div>
            </li>`;
    }

    // 指定された要素内のタスク操作ボタン/チェックボックスにイベントリスナーを設定する
    function setupEventListeners(element = document) {
        // 完了状態切り替えイベント (チェックボックス)
        element.querySelectorAll('input[type="checkbox"][data-task-id]').forEach(checkbox => {
            checkbox.removeEventListener('change', toggleTaskHandler); // 二重登録防止
            checkbox.addEventListener('change', toggleTaskHandler);
            });

            // 削除ボタンクリックイベント
            element.querySelectorAll('.delete-task-btn').forEach(btn => {
                btn.removeEventListener('click', deleteTaskHandler); // 二重登録防止
                btn.addEventListener('click', deleteTaskHandler);
            });
    };

    // タスクの完了状態をサーバー経由で切り替える非同期関数
    async function toggleTaskHandler(event) {
        const checkbox = event.target;
        const taskId = checkbox.dataset.taskId;
        if (!taskId) {showToast("タスクID不明", "error"); return;};

        try {
            // APIエンドポイントへPOSTリクエスト
            const response = await fetch(`/api/toggle_task/${taskId}`, {
                method: `POST`,
                headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken},
                body: JSON.stringify({ is_completed: event.target.checked})
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // 成功した場合、タスクテキストのスタイルを更新（打ち消し線）
                const span = event.target.closest('li').querySelector('span.task-text');
                if (data.is_completed) {
                    span.classList.add('Line-through', 'text-gray-400');
                    showToast("タスクを完了しました！", "success");
                } else {
                    span.classList.remove('line-through', 'text-gray-400');
                    showToast("タスクを未完了に戻しました", "success");
                }
            } else {
                // 失敗した場合、エラー通知とチェックボックスの状態を元に戻す
                showToast(data.message || "更新失敗", "error");
                checkbox.checked = !event.target.checked;
            }
        } catch (e) {
            // 通信エラーが発生した場合
            console.error("通信エラー:", e);
            showToast("サーバーとの通信に失敗しました", "error");
            checkbox.checked = !event.target.checked;
        }
    }

    // タスクを削除する非同期関数
    async function deleteTaskHandler(e) {
        e.preventDefault();
        const li = this.closest('li');
        const taskId = li.dataset.taskId;
        if (!taskId) { console.error("タスクID取得不可"); return; }

        if (confirm("本当に削除しますか？")) { // 削除確認ダイアログ
            try {
                // APIエンドポイントへDELETEリクエスト
                const response = await fetch(`/api/delete_task/${taskId}`, {
                    method: 'DELETE',
                    headers: { 'X-CSRF-Token': csrfToken }
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    li.remove(); // 成功した場合、DOMからタスク要素を削除
                    showToast("タスクを削除しました", "success");
                } else {
                    showToast(data.message || "削除失敗", "error");
                }
            } catch (e) {
                console.error("通信エラー:", e);
                showToast("サーバーとの通信に失敗しました", "error");
            }
        }
    }

    // タスク追加フォームの送信イベントハンドラ
    if (taskForm && taskContentInput && taskPriorityInput) {
        taskForm.addEventListener('submit', async function (e) {
            e.preventDefault(); // デフォルトのフォーム送信を停止
            const content = taskContentInput.value.trim();
            const priority = taskPriorityInput.value;

            if (!content) { showToast("タスクを入力してください", "error"); return; }
            
            try {
                // APIエンドポイントへ新しいタスクをPOST
                const response = await fetch('/api/add_task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
                    body: JSON.stringify({ task_content: content, priority: priority })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // 成功した場合、タスクHTMLを生成し、リストに追加
                    const newTaskHtml = createTaskListItem(data.task);
                    if (taskList) {
                        taskList.insertAdjacentHTML('beforeend', newTaskHtml);
                        taskContentInput.value = ""; // フォームをクリア

                        // 新しい要素にイベントリスナーを設定
                        const newLi = taskList.lastElementChild;
                        setupEventListeners(newLi); 
                        showToast("タスク追加成功", "success");
                    }
                } else {
                    showToast(data.message || "追加失敗", "error");
                }
            } catch (err) {
                console.error("追加エラー:", err);
                showToast("サーバーとの通信に失敗しました", "error");
            }
        }); 
    }

    // 初回ロード時に既存のタスク全てにイベントリスナーを設定
    setupEventListeners();
});