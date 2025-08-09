#!/usr/bin/env bash
set -e

# 出力ディレクトリ
BUILD_DIR="build"

echo "Building AsciiDoc files into $BUILD_DIR ..."

# 出力先初期化
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# .adoc → .html に変換（フォルダ構造を維持）
find source -name "*.adoc" | while read file; do
  outdir="$BUILD_DIR/$(dirname "${file#source/}")"
  mkdir -p "$outdir"
  asciidoctor -D "$outdir" "$file"
done

# 静的ファイル（画像・CSS・JSなど）をコピー
find source -type f ! -name "*.adoc" -exec bash -c '
  for f; do
    out="'"$BUILD_DIR"'/${f#source/}"
    mkdir -p "$(dirname "$out")"
    cp "$f" "$out"
  done
' bash {} +

# index.html 内の .adoc → .html 置換
INDEX_FILE="$BUILD_DIR/index.html"
if [ -f "$INDEX_FILE" ]; then
  echo "Replacing .adoc links with .html in $INDEX_FILE ..."
  # macOS と Linux 両対応の sed
  if sed --version >/dev/null 2>&1; then
    # GNU sed
    sed -i 's/\.adoc/.html/g' "$INDEX_FILE"
  else
    # BSD sed (macOS)
    sed -i '' 's/\.adoc/.html/g' "$INDEX_FILE"
  fi
else
  echo "Warning: $INDEX_FILE not found, skipping link replacement."
fi

echo "Build completed. Files are in $BUILD_DIR/"
