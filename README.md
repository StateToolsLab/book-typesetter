# book-typesetter（組版の担当）

日本語の本を仕上げる、組版の相談役の Agent Skill です。実際の縦組の復刻本を組み直した経験から作りました。

> 文字は変えない。余白と空きで受け止める。

1 字だけはみ出した行、頁の頭に残る短い行、見出しの高さ、括弧の見え方、原本との見比べ。こうした相談に、頁を測って数字で答え、文字を変えずに解く方法を提案します。

## 中身
- `SKILL.md`: 役割、判断の順番、答え方、やらないこと
- `references/techniques.md`: 技の引き出し（軽い順、計算式と数字の例つき）
- `references/measuring.md`: 測り方
- `references/tools-designcraft.md`: DesignCraft で組むときの道具の例（スクリプトは含みません）
- `tests/acceptance-cases.md`: 受け入れの例

## 使い方
Claude Code なら、このフォルダを `~/.claude/skills/book-typesetter/` に置きます。

```bash
git clone https://github.com/StateToolsLab/book-typesetter.git ~/.claude/skills/book-typesetter
```

PDF を測るには、poppler（`pdftotext`、`pdftoppm`、`pdffonts`）があると進めやすくなります。

## 状態
0.1.0（下書き）。1 冊の縦組の本で作り、実際の頁を使った相談で 2 件試しました。本 1 冊を通して使った実績はまだありません。校閲（別の目での点検）は役目に含みません。

## English
An Agent Skill that acts as a typesetter for finishing Japanese books, mainly vertical text in print PDF and fixed-layout EPUB. Its principle: never change the words; solve layout problems with space. The skill measures the page, compares it with the source, and proposes the lightest fix, such as tightening punctuation to absorb a stray character. The documents are written in Japanese.

## License
MIT
