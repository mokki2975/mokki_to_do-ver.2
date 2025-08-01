import os

def regenerate_index_html():
    # index.htmlのパス
    html_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'todo_app_package', 'templates', 'index.html'
    )

    # 現在のindex.htmlの内容を読み込む
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"エラー: {html_file_path} の読み込みに失敗しました: {e}")
        return

    # 既存の </script>...</body> の部分を特定して削除
    # これは最後の </script> タグを想定しています
    body_end_tag_index = html_content.rfind('</body>')
    if body_end_tag_index != -1:
        # 最後の script タグの開始を探す
        last_script_tag_start = html_content.rfind('<script', 0, body_end_tag_index)
        if last_script_tag_start != -1:
            # scriptタグとそれ以降のbodyの終わりまでを一旦削除
            html_content_cleaned = html_content[:last_script_tag_start]
        else:
            # scriptタグが見つからない場合はbodyタグの直前までをそのまま利用
            html_content_cleaned = html_content[:body_end_tag_index]
    else:
        print("エラー: </body> タグが見つかりませんでした。HTML構造を確認してください。")
        return

    # 新しい <script> タグと </body>, </html> を追加する
    # Jinja2のurl_forはそのまま文字列として記述します
    new_script_tag = '    <script src="{{ url_for(\'static\', filename=\'js/main.js\') }}"></script>\n'

    final_html_content = (
        html_content_cleaned.strip() + '\n' + # 行末の余計な空白を削除
        new_script_tag +
        '</body>\n' +
        '</html>\n'
    )

    # 新しい内容でindex.htmlを上書き保存する
    try:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(final_html_content)
        print(f"'{html_file_path}' をJavaScriptタグ付きで再生成しました。")
        print("これでブラウザのコンソールに 'Hello from main.js!' が表示されるはずです。")
    except Exception as e:
        print(f"エラー: '{html_file_path}' の書き込みに失敗しました: {e}")

if __name__ == "__main__":
    regenerate_index_html()