# 開発の手引き

## ローカルで実行

プロジェクトルートに`.env`ファイルを置き、環境変数を設定してください。
その後、以下を実行します。

```sh
poetry install
poetry run python run.py
```

## 環境変数

- `HOLOCAL_YOUTUBE_KEY`: **必須**です。YouTube Data APIのAPIキーです。
- `HOLOCAL_PAGE`: 取得するホロジュールのページのURLです。「シンプル版」でなければなりません（例：[全体](https://schedule.hololive.tv/simple "hololive production")）。
- `HOLOCAL_DIR`: 結果の`ics`ファイルを置くディレクトリです。既定は`public`です。
- `HOLOCAL_LOGLEVEL`: `logging`モジュールのログ水準です。既定で`INFO`です。

## TODO

* 型検査
* ドキュメント
* テスト

## 参考資料

[ワークフローにスクリプトを追加する](https://docs.github.com/ja/actions/writing-workflows/choosing-what-your-workflow-does/adding-scripts-to-your-workflow "GitHub")

[GitHub Actions　のワークフロー構文](https://docs.github.com/ja/actions/writing-workflows/workflow-syntax-for-github-actions "GitHub")

[pipx - On Linux](https://github.com/pypa/pipx?tab=readme-ov-file#on-linux "GitHub")

[Python のビルドとテスト](https://docs.github.com/ja/actions/use-cases-and-examples/building-and-testing/building-and-testing-python "GitHub")

[deploy-pages](https://github.com/actions/deploy-pages "GitHub") and [Deploy GitHub Pages site](https://github.com/marketplace/actions/deploy-github-pages-site "GitHub").

[upload-pages-artifact](https://github.com/actions/upload-pages-artifact "GitHub")
