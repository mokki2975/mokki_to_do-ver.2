from todo_app_package import create_app, init_db_command

# Flaskアプリケーションインスタンスの生成
app = create_app()

# Flask CLIにデータベース初期化コマンドを追加
app.cli.add_command(init_db_command)

if __name__ == "__main__":
    # ローカル起動用サーバー起動
    app.run(debug=True)