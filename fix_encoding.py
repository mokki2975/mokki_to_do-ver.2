import os

def fix_js_encoding(file_path):
    try:
        with open(file_path, 'rb') as f:
            content_bytes = f.read()

        try:
            decoded_content = content_bytes.decode('shift_jis')
        except UnicodeDecodeError:
            try:
                decoded_content = content_bytes.decode('cp932')
            except UnicodeDecodeError:
                decoded_content = content_bytes.decode('utf-8')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(decoded_content)

        print(f"DEBUG: '{file_path}'のエンコーディングをUTF-8に修正しました。")
    except Exception as e:
        print(f"エラーが発生しました:{e}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    js_file_path = os.path.join(project_root, 'static', 'js', 'main.js')

    print(f"DEBUG: スクリプトが操作しようとしているファイルパス: '{js_file_path}'")

    simple_js_content = 'console.log("Hello from main.js!");'
    with open(js_file_path, 'w', encoding='utf-8') as f:
        f.write(simple_js_content)
    print(f"'{js_file_path}' の内容をシンプルな英語メッセージに書き換えました。")

    fix_js_encoding(js_file_path)

    try:
        with open(js_file_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        print(f"DEBUG: 書き換え後の '{js_file_path}' の内容:\n---START---\n{updated_content}\n---END---")
    except Exception as e:
        print(f"DEBUG: 書き換え後の内容読み込みでエラーが発生しました: {e}")
