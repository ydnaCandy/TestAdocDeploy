#!/bin/bash

set -e

# プロジェクト名（指定しなければ "my-adoc-docs"）
PROJECT_NAME=${1:-my-adoc-docs}

echo "Creating project: $PROJECT_NAME"

# ディレクトリ作成
mkdir -p "$PROJECT_NAME/source/_partial"
mkdir -p "$PROJECT_NAME/.github/workflows"

# メインドキュメント
cat > "$PROJECT_NAME/source/index.adoc" <<'EOF'
= サンプルドキュメント
:doctype: article
:toc: left
:toclevels: 2

include::_partial/intro.adoc[]
EOF

# インクルードされる部分ファイル
cat > "$PROJECT_NAME/source/_partial/intro.adoc" <<'EOF'
== はじめに

これはインクルードされた内容です。
EOF

# GitHub Actions ワークフロー
cat > "$PROJECT_NAME/.github/workflows/deploy.yml" <<'EOF'
name: Build and Deploy AsciiDoc

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: 3.1

      - name: Install Asciidoctor
        run: gem install asciidoctor

      - name: Build AsciiDoc (resolve includes)
        run: |
          mkdir -p build
          asciidoctor -D build source/index.adoc

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
EOF

echo "✅ 完了: $PROJECT_NAME のフォルダとテンプレートファイルを作成しました。"
