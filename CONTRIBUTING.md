# Developing guide

## Clone repository

To avoid cloning numerous deploy histories in `public` and `gh-pages` branch,
make sure to clone with `--single-branch` option:

```
git clone -b master --single-branch https://github.com/sarisia/holodule-ics.git
```

## Run locally

Place `.env` with environment variables to project root, then run:

```sh
poetry install
poetry run python run.py
```

## Environment Variables

- `HOLODULE_PAGE`: **Required.** Holodule page URL to get. Must be a `シンプル版` (e.g. [全体](https://schedule.hololive.tv/simple "hololive production")).
- `HOLODULE_YOUTUBE_KEY`: **Required.** API key of YouTube Data API.
- `HOLODULE_PAGE`: Holodule page URL to get.  Must be a `シンプル版` (e.g. [全
  体](https://schedule.hololive.tv/simple "hololive production")).
- `HOLODULE_DIR`: Directory to place result `.ics` files.  Default to `public`.
- `HOLODULE_LOGLEVEL`: Loglevel of `logging` module. Default to `INFO`.

## TODO

* Type checking
* Documentation
* Tests

## References

[ワークフローにスクリプトを追加する](https://docs.github.com/ja/actions/writing-workflows/choosing-what-your-workflow-does/adding-scripts-to-your-workflow "GitHub")

[GitHub Actions　のワークフロー構文](https://docs.github.com/ja/actions/writing-workflows/workflow-syntax-for-github-actions "GitHub")

[pipx - On Linux](https://github.com/pypa/pipx?tab=readme-ov-file#on-linux "GitHub")

[Python のビルドとテスト](https://docs.github.com/ja/actions/use-cases-and-examples/building-and-testing/building-and-testing-python "GitHub")

[deploy-pages](https://github.com/actions/deploy-pages "GitHub") and [Deploy GitHub Pages site](https://github.com/marketplace/actions/deploy-github-pages-site "GitHub").

[upload-pages-artifact](https://github.com/actions/upload-pages-artifact "GitHub")
