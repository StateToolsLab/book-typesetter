#!/bin/bash
# 1 回分の実行。使い方: run_one.sh <claude|codex> <indesign|designcraft> <A|B|C> <run_id> <依頼文ファイル>
# 条件 A=スキルなし、B=CJK Layout、C=book-typesetter。作業場所の名前には条件を入れない。
set -u
EXE=$1; TOOL=$2; ARM=$3; ID=$4; PROMPT_FILE=$5
T="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$T/config.sh" ] || { echo "config.sh がない。config.example.sh を写して直す"; exit 2; }
. "$T/config.sh"
W="$WORK_DIR/$ID"; OUT="$RUNS_DIR/$ID"
[ -e "$W" ] && { echo "中止 $ID: 作業フォルダがすでにある"; exit 3; }
# InDesign は、文書が 1 つでも開いていたら始めない
if [ "$TOOL" = indesign ] && [ "${DRY_RUN:-}" != 1 ]; then
  DOCS=$(osascript -e 'tell application id "com.adobe.InDesign" to count documents' 2>&1)
  if [ "$DOCS" != 0 ]; then echo "中止 $ID: InDesign の文書数が 0 ではない ($DOCS)"; exit 3; fi
fi
mkdir -p "$W" "$OUT"
sed "s#{{DESIGNCRAFT_CLI}}#$DESIGNCRAFT_CLI#g" "$T/tool_sheet.md" > "$W/道具の紙.md"
cp "$T/problems/manuscript_v.txt" "$T/problems/manuscript_h.txt" "$T/problems/spec.md" "$W/"
case $EXE in
  claude) SK="$W/.claude/skills";;
  codex) SK="$W/.agents/skills"; git -C "$W" init -q;;
  *) echo "実行役は claude か codex"; exit 2;;
esac
case $ARM in
  A) ;;
  B) mkdir -p "$SK"; cp -R "$CJK_LAYOUT_DIR/cjk-layout" "$CJK_LAYOUT_DIR/cjk-layout-audit" "$SK/";;
  C) mkdir -p "$SK"; rsync -a --exclude .git --exclude CLAUDE.md --exclude evaluation "$BOOK_TYPESETTER_DIR/" "$SK/book-typesetter/";;
  *) echo "条件は A か B か C"; exit 2;;
esac
if [ "$EXE" = codex ]; then
  PROMPT="$(cat "$PROMPT_FILE")

使う組版ソフトは ${TOOL} です。操作の説明は『道具の紙.md』にあります。途中でユーザーに質問しても返事は来ません。
確認や計画の報告だけで終えず、依頼を最後まで実行し、成果の PDF を残してから返答を終えてください。"
else
  PROMPT="使う組版ソフトは ${TOOL} です。操作の説明は『道具の紙.md』を読んでください。
途中でユーザーに質問しても返事は来ません。最後まで自分で進めてください。

$(cat "$PROMPT_FILE")"
fi
if [ "${DRY_RUN:-}" = 1 ]; then echo "用意だけ: $W"; printf '%s\n' "$PROMPT"; exit 0; fi
cd "$W"
START=$(date +%s)
if [ "$EXE" = claude ]; then
  ALLOW=("Read" "Write" "Edit" "Skill" "Bash(osascript:*)" "Bash($DESIGNCRAFT_CLI:*)" "Bash(python3:*)" "Bash(pdftotext:*)" "Bash(pdftoppm:*)" "Bash(pdffonts:*)" "Bash(pdfinfo:*)" "Bash(ls:*)" "Bash(cat:*)" "Bash(mkdir:*)" "Bash(cp:*)" "Bash(mv:*)" "Bash(grep:*)" "Bash(sed:*)" "Bash(awk:*)" "Bash(head:*)" "Bash(tail:*)" "Bash(wc:*)" "Bash(diff:*)" "Bash(sleep:*)")
  CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 timeout "$TIME_LIMIT" "$CLAUDE_BIN" -p "$PROMPT" --model "$CLAUDE_MODEL" \
    --setting-sources project --strict-mcp-config --mcp-config '{"mcpServers":{}}' --no-chrome --no-session-persistence \
    --tools "Bash,Read,Write,Edit,Skill" --permission-mode acceptEdits --allowedTools "${ALLOW[@]}" --output-format stream-json --verbose \
    </dev/null > "$OUT/transcript.jsonl" 2> "$OUT/stderr.txt"
else
  HOME="$CODEX_ISOLATED_HOME/home" CODEX_HOME="$CODEX_ISOLATED_HOME/ch" timeout "$TIME_LIMIT" "$CODEX_BIN" exec --json --ephemeral --ignore-user-config --ignore-rules \
    --skip-git-repo-check -m "$CODEX_MODEL" -s workspace-write "$PROMPT" </dev/null > "$OUT/transcript.jsonl" 2> "$OUT/stderr.txt"
fi
RC=$?
END=$(date +%s)
echo "exe=$EXE tool=$TOOL arm=$ARM rc=$RC seconds=$((END-START))" > "$OUT/meta.txt"
rsync -a --exclude .git --exclude .claude --exclude .agents "$W/" "$OUT/work/"
if [ "$TOOL" = indesign ]; then
  osascript -e "tell application id \"com.adobe.InDesign\" to do script (POSIX file \"$T/scripts/cleanup.jsx\") language javascript" > "$OUT/cleanup.txt" 2>&1
fi
cat "$OUT/meta.txt"
