# 手元の設定。config.sh に写して直す。

# Claude Code の実行ファイル
CLAUDE_BIN="claude"
CLAUDE_MODEL="claude-opus-5-5"

# Codex の実行ファイルとモデル（使うときだけ）
CODEX_BIN="codex"
CODEX_MODEL="gpt-6.1-sol"
# 個人の設定を混ぜないための別の置き場所（auth.json のリンクなどは自分で用意する）
CODEX_ISOLATED_HOME="$HOME/typeset-eval/_codex"

# DesignCraft の CLI（使うときだけ）
DESIGNCRAFT_CLI="/path/to/designcraft-cli"

# 作業フォルダと結果の置き場所
WORK_DIR="$HOME/typeset-eval/work"
RUNS_DIR="$HOME/typeset-eval/runs"

# 比べるスキル
CJK_LAYOUT_DIR="$HOME/typeset-eval/cjk-layout-skills"
BOOK_TYPESETTER_DIR="$HOME/typeset-eval/book-typesetter"

# 1 回の上限（秒）
TIME_LIMIT=1200
