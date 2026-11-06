# 道具の紙（全条件に同じものを渡す）

- 作業はこのフォルダの中だけで行う。フォルダの外のファイルを読み書きしない。ネットで調べない。
- 成果の PDF と、組むのに使ったスクリプトや設定をこのフォルダに残す。

## InDesign 2025 のとき
- Mac で起動中の InDesign を AppleScript 経由の ExtendScript で動かす。例: `osascript -e 'tell application id "com.adobe.InDesign" to do script (POSIX file "/絶対パス/x.jsx") language javascript'`
- スクリプトの冒頭で `app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;` を設定し、ダイアログを出さない。
- **自分で作った文書だけを操作する。すでに開いている文書には一切触らない。`app.activeDocument` を使わず、`app.documents.add()` の戻り値を変数に持って使う。終わったら自分の文書だけを閉じる。**
- 単位は `"9.8pt"` のように付けて渡す。

## DesignCraft のとき
- CLI: `{{DESIGNCRAFT_CLI}}`
- `commands [FILTER]` で命令の一覧、`describe 命令` で説明。`run --cmd ID=JSON ... --export OUT.pdf`、`script FILE --save OUT --export OUT.pdf`。

## PDF を測る
poppler の `pdftotext -bbox-layout`、`pdftoppm`、`pdffonts` が使える。
