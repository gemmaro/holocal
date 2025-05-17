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

## 設計

イベントの動画のURLは、説明欄とURLフィールドの両方に出力しています。
一見すると重複しているようですが、これには理由があります。
基本的に、URLのフィールドは利用した方が良いです。
これは、もしカレンダーアプリが説明欄に含まれるURLを解析しない仕様のとき、リンクの遷移に手間が掛かる可能性があるためです。
一方で、URLのフィールドのみで、説明欄にURLが含まれていない場合も問題があります。
カレンダーアプリの中には、URLのフィールドを解釈しないものがあるためです。
一例ではMicrosoft Outlookのウェブ版がこれに該当します。

## TODO

* 型検査
* ドキュメント
* 翻訳を改善
* テスト

## 参考資料

[ワークフローにスクリプトを追加する](https://docs.github.com/ja/actions/writing-workflows/choosing-what-your-workflow-does/adding-scripts-to-your-workflow "GitHub")

[GitHub Actions　のワークフロー構文](https://docs.github.com/ja/actions/writing-workflows/workflow-syntax-for-github-actions "GitHub")

[pipx - On Linux](https://github.com/pypa/pipx?tab=readme-ov-file#on-linux "GitHub")

[Python のビルドとテスト](https://docs.github.com/ja/actions/use-cases-and-examples/building-and-testing/building-and-testing-python "GitHub")

[deploy-pages](https://github.com/actions/deploy-pages "GitHub") and [Deploy GitHub Pages site](https://github.com/marketplace/actions/deploy-github-pages-site "GitHub").

[upload-pages-artifact](https://github.com/actions/upload-pages-artifact "GitHub")
