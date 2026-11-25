# 見る頁の見本

`viewer.png` は、架空の文章（`sample.html`）を A5 縦組で PDF にし、`tools/viewer/update_viewer.py` で見る頁にしたものの画面です。文章はこのリポジトリのために書いたもので、公開して差し支えありません。

| ファイル | 中身 |
|---|---|
| `sample.html` | 見本の文章と組みの指定（A5 縦組、本文 10pt、行送り 18pt、1 行 40 字、1 頁 15 行） |
| `sample.pdf` | `sample.html` を Chrome で PDF にしたもの（2 頁） |
| `page-grid.json` | 見本の版面の値（本のフォルダでは `版面.json` にあたる）。見開きの見本になるよう、最初のノンブルを 2 にした（右開きなので 2 頁が右、3 頁が左） |
| `out/` | できた見る頁（`viewer.html` と頁の画像） |
| `viewer.png` | `out/viewer.html` を「見開きで見る」にした画面（幅 1100、1.5 倍） |

## 作り直し方
1. 源ノ明朝（Source Han Serif JP、SIL Open Font License）の `SourceHanSerifJP-Medium.otf` を、Adobe の配布から取って `fonts/` に置く（書体はリポジトリに入れていない）。
2. Chrome で PDF にする:
   ```
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --allow-file-access-from-files --no-pdf-header-footer --print-to-pdf=sample.pdf "file://$PWD/sample.html"
   ```
3. 見る頁を作る:
   ```
   python3 -I ../../tools/viewer/update_viewer.py sample.pdf page-grid.json out "町の製本所（見本）" --light-pdf /tmp/sample_light.pdf
   ```

## 版面の値の測り方
- 1 行目の字の左端（330.9pt）と天（97.64pt）は、頁の画像のインクで確かめた。行送り 18pt、字の大きさ 10pt、1 頁 15 行、1 行 40 字は組みの指定のとおり。
- Chrome が書き出した PDF は、文字の層の箱が字より約 10pt 上に出る。そのため `数える範囲_pt` を `[80, 490]` に広げて、行ごとの字数を数えている。組みの道具が変わったら、文字の層と画像の両方で測り直す。
- 最初の頁は見出しが 2 行分を取り、本文は 12 行。15 行目は空いて、次の段落の行は次の頁へ送られた（Chrome の頁の切り方）。字数は 577 字で、元の文章の字数と同じ。
