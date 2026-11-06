# Test toolkit（テスト用のツールキット）

組版のスキルを、手元で同じ条件で試すための部品です。[レポート](../report.md)の試しに使ったものを、誰でも動かせる形に直しました。

結果を比べるときは、次のことに気をつけてください。

- 問題と判定は、スキルの作者側で作りました。問題作成者の注意は `problems/notes.md` にあります（合格の条件は字間の調整に有利、行の切れ目は手で数えた予想、など）。
- 1 回ずつの結果では、結論を出せません。
- 頁の画像や、実際の本は入っていません。原本から組む試しは、権利を確かめたうえで、手元の本で行ってください。

## 入っているもの

| 場所 | 中身 |
|---|---|
| `problems/` | 架空の原稿（縦組、横組）、`spec.md`、12 問（`problems.json`）、問題作成者の注意 |
| `prompts/` | 依頼文の例（指摘型と開放型） |
| `tool_sheet.md` | 実行役に渡す、道具の説明 |
| `answer_sheet_example.md` | 聞き取りの試しで答える役に渡す紙の例（架空の本） |
| `manifest.csv` | 問題と条件の割り当ての例 |
| `config.example.sh` | 手元の設定の見本 |
| `scripts/run_one.sh` | 1 回を動かす |
| `scripts/measure.py` | PDF を字の位置で測る |
| `scripts/intake_run.py` | 組む前の聞き取りを試す |

## 準備

1. `cp config.example.sh config.sh` として、`config.sh` を手元に合わせます。
2. `pdftotext`（poppler）を入れます。
3. 比べるスキルを手元に置きます。CJK Layout は同梱していません。試しに使った版は次のとおりです。

   ```bash
   git clone https://github.com/sichengchen/cjk-layout-skills.git
   ```

   ```bash
   git -C cjk-layout-skills checkout f366da8cae67ccb51cea05ceb7eaf491c89ba61e
   ```

## 1 回を動かす

`run_one.sh <実行役> <ソフト> <条件> <回の名前> <依頼文>` の形です。条件は A（スキルなし）、B（CJK Layout）、C（book-typesetter）です。

```bash
scripts/run_one.sh claude designcraft A p008 prompts/V-WIDOW-1_pointed.md
```

`DRY_RUN=1` を付けると、作業フォルダだけ作って止まります。

## 測る

`manifest.csv` の回と、`RUNS_DIR` の中の結果を突き合わせて測り、`RUNS_DIR/measure.csv` に出します。回の名前、問題、条件は `manifest.csv` に合わせてください。上の例の `p008` も、そこに載っている回です。

```bash
scripts/measure.py p008
```

字の位置は語の箱から求めるので、語の中は等分とみなします。縦中横の向きは分からないので、頁の画像で確かめてください。

## 聞き取りを試す

組まずに、組みの仕様の紙を作るところまでです。答える役は別の Claude で、答えの紙だけから答えます。答えの紙の項目は聞き取りと似た作りになるので、スキルに有利です。できれば人が答えてください。

```bash
scripts/intake_run.py C i001 answer_sheet_example.md path/to/source
```

## 動かす前に

- **InDesign の文書を保存して閉じてください。** `run_one.sh` は、文書が開いていると始めません。
- 実行役を時間切れで止めても、InDesign の中のスクリプトは止まりません。
- 実行役の作業は、OS の仕組みでは閉じ込められません。「フォルダの外に触らない」は指示と、記録の点検で見ているだけです。大事なファイルのない環境で動かしてください。
- 許可の回数を比べたいなら、押した回数を手で記録してください。Codex の記録からは正確に数えられませんでした。
