# 道具の例: DesignCraft の組み

DesignCraft CLI で 1 章を組むときに使った道具の例です。スクリプトはこの下書きにまだ含めていません。ほかの組版ソフトでも、同じ役目の道具をそろえると進めやすくなります。

| 道具 | 役目 |
|---|---|
| `build_chapter_pages.py 設定.json` | 設定から PDF・EPUB の部品・頁画像を作る |
| `fill_pages.py 設定.json 新しい頁割り.json 作業フォルダ [動かさない頁…]` | 頁を詰めて頁割りを出す。設定の no_folio_pages も書き換える |
| `merge_fixed_epub.py` | 固定レイアウトの EPUB にまとめる |
| `grid_check.py PDF 行送り 字の大きさ` | 本文の行が格子に乗っているかを見る |
| `ink_columns.py`・`ink_pitch.py` | 画像のインクの位置を測る |

## よく使う設定
| 設定 | 使い道 |
|---|---|
| `pushin_paras: [段落]` | その段落だけ追い込む |
| `para_space_before: {"Word の段落": pt}` | 引用の段落の前のあきを決める |
| `para_style: {"正本の段落": "スタイル"}` | その段落だけ別のスタイルにする（俳句など） |
| `page_frame_dx: {"頁": pt}` | 頁全体のずれを格子へ戻す |
| `quote_rule` | 引用の天・頭。`fixed` で例外を作る |
| `style_map` | 段落のスタイルをそのまま使う |
| `drop_paragraphs` | 本に入れない段落（空の段落など） |
| `folio_odd_mm` | 奇数頁のノンブルと柱の左端 |
| `no_folio_pages`・`running_head_add`・`running_head_remove` | ノンブルと柱を頁ごとに外す・足す |
| `page_figures`・`figures`・`inline_figures` | 写真の頁、写真だけの頁、文の中の写真 |

## 注意
- 版は上書きせず、`組み直しN` として分ける。設定と頁割りも版ごとに残す。
- `fill_pages.py` は頁割りの `first_line` を更新しない。組んだ後に正本から書き直す。
- 1 行目の「—」や縦中横があると、頁全体が約 2.74pt 左へずれる。`grid_check.py` で分かる。頁の頭が動くたびに見直す。
- 頁の頭の見出しは、前のあき 0 で組む。見出しの行送りと後のあきの合計を、本文の格子に合わせる。
