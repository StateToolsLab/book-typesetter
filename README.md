# book-typesetter

**v0.1.1**

An Agent Skill that acts as the typesetter who finishes a Japanese book. It measures the page, compares it with the source, and solves layout problems without touching the author's words.

> Change no words. Absorb the problem with space.

日本語は下にあります / Japanese follows below.

---

## Before and after

![The same sample page before and after applying the skill's techniques](examples/before-after.png)

*Vertical text reads from right to left, so read the right page first. The text is a fictional sample written for this repository, typeset twice with the same software and settings except for the four changes below. A person applied the techniques by hand following the skill; this is not the raw output of a skill run.*

| # | Before | After | Technique |
|---|---|---|---|
| 1 | The haiku sits between paragraphs and does not stand out | One blank line before and after | Space in whole-line units |
| 2 | 「る。」 spills onto its own line | No stray line; the paragraph is one line shorter | Tighten two punctuation marks by half an em (9.8pt → 4.9pt) to pull in one character |
| 3 | The heading looks low because a full-width 〔 is empty in its upper half | The ink of 〔 lines up with the top of the quotation | Raise the box by half its size (0.55 em) |
| 4 | Wrapped lines stick out one character above the numbered heads | Heads and wrapped lines start at the same height | Remove the first-line indent from numbered items |

More samples and the numbers are in [examples/](examples/).

## What it does

The skill follows the same order every time:

1. Look at the finished page, not the settings.
2. Measure character positions. Never quote a number by eye.
3. Compare with the source, if there is one.
4. Find the cause: this line, this page, the flow from an earlier page, or a book-wide rule.
5. Try the lightest technique first, and calculate whether it will work before trying it.
6. Check the side effects: later pages, and anything the author or editor has already approved.
7. Recommend one option, with its cost.
8. Compare with the previous version mechanically, then hand over to a separate proofreader.

It never proposes rewriting the text to make a page fit.

## Getting started

Copy this folder to your skills directory. For Claude Code:

```sh
git clone https://github.com/StateToolsLab/book-typesetter.git ~/.claude/skills/book-typesetter
```

Then ask about the layout in your own words, for example 「この 1 字、詰められない？」 or 「この見出しの高さ、原本と比べて」. Measuring PDFs works best with poppler (`pdftotext`, `pdftoppm`, `pdffonts`).

```
SKILL.md                      role, order of judgment, how to answer, what not to do
references/techniques.md      techniques from lightest to heaviest, with formulas and numbers
references/measuring.md       how to measure PDFs and scans
references/tools-designcraft.md  example tools and settings for DesignCraft (scripts not included)
tests/acceptance-cases.md     what a good answer looks like
examples/                     the before-and-after sample
```

The documents are written in Japanese.

## How this was built

book-typesetter is made by StateToolsLab with AI assistance. It was drafted with Claude (Anthropic) from the decisions made while resetting one vertical-text reprint, where a person pointed out each problem, chose among the options, and checked every version. AI proposes; people review and decide.

## Status and verification

Version 0.1.1 is an early draft. It comes from one A5 vertical-text book and was tried on two real layout questions, one of them also run without the skill. On that question the answer without the skill was also good; the skill added another option (expanding a line to absorb a short one), and its main value so far is a repeatable order and written-down techniques. It has not yet been used through a whole book, and horizontal text, reflowable EPUB, and other typesetting software were not tested.

## License

[MIT License](LICENSE). Copyright (c) 2026 StateToolsLab.

---

# book-typesetter（日本語）

日本語の本を仕上げる、組版の担当の Agent Skill です。頁を測り、原本と見比べ、作家の言葉に手を入れずに頁の問題を解きます。

> 文字は変えない。余白と空きで受け止める。

## ビフォーアフター

上の画像が、同じ文章を組んだ比較です。縦組なので、右の頁（適用前）から読んでください。文章はこのリポジトリのために書いた架空のサンプルで、組版ソフトも設定も、下の 4 点のほかは同じです。スキルの手順に沿って人が技を当てて組んだもので、スキルの実行結果をそのまま載せたものではありません。

| # | 適用前 | 適用後 | 技 |
|---|---|---|---|
| 1 | 俳句が地の文に埋もれている | 前後を 1 行ずつあける | 行単位のあき |
| 2 | 「る。」だけの行が出る | 短い行が消え、段落が 1 行減る | 約物 2 か所を半字ずつ詰めて（9.8pt → 4.9pt）、1 字を前の行へ入れる |
| 3 | 全角の「〔」は上半分が空くので、見出しが下がって見える | 「〔」の字の頭が引用の天にそろう | 箱を字の半分（0.55 字）上げる |
| 4 | 番号の折り返しが 1 字上に出て、はみ出して見える | 番号の頭と折り返しが同じ高さ | 番号の項目の段落頭の下げを外す |

詳しくは [examples/](examples/) を見てください。

## 何をするか

毎回、同じ順番で進めます。

1. 設定ではなく、出来上がった頁を見る。
2. 字の位置を測る。目測で数字を言わない。
3. 原本があれば見比べる。
4. 原因を切り分ける（その行、その頁、前の頁からの流れ、本全体の決まり）。
5. 軽い技から当てる。効くかどうかを先に計算する。
6. 影響を調べる（後ろの頁、すでに「良い」と言われた所）。
7. おすすめを 1 つ、代償と一緒に出す。
8. 前の版と機械で比べ、別の担当の校閲へ回す。

頁に収めるために文を書き換える案は出しません。

## 使い方

スキルのフォルダに置きます。Claude Code の場合:

```sh
git clone https://github.com/StateToolsLab/book-typesetter.git ~/.claude/skills/book-typesetter
```

あとは「この 1 字、詰められない？」「この見出しの高さ、原本と比べて」のように、ふだんの言葉で相談してください。PDF を測るには poppler（`pdftotext`、`pdftoppm`、`pdffonts`）があると進めやすくなります。

## 作り方について

StateToolsLab が AI の支援を受けて作りました。縦組の復刻本を 1 冊組み直したときの判断をもとに、Claude（Anthropic）と下書きしました。その本では、人が問題を指摘し、案を選び、版ごとに確かめました。

## 状態と検証

0.1.1 は初期の下書きです。A5 縦組の本 1 冊から作り、実際の相談 2 件で試しました。そのうち 1 件はスキルなしでも試し、スキルなしでも答えはよいものでした。スキルで増えたのは別の案（行を広げて短い行を解く案）で、今のところの主な価値は、手順が毎回そろうことと、技が文書に残ることです。本 1 冊を通して使った実績はまだありません。横組、リフロー型の EPUB、ほかの組版ソフトでは試していません。

## ライセンス

[MIT License](LICENSE). Copyright (c) 2026 StateToolsLab.
