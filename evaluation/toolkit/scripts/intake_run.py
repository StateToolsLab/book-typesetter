#!/usr/bin/env python3
"""組む前の聞き取りの試し。実行役が聞き、答える役が答えの紙だけから返す。組まずに仕様の紙まで。
使い方: intake_run.py <A|B|C> <run_id> <答えの紙> <素材のフォルダ>
config.sh の値を使う。結果は RUNS_DIR/<run_id>/ に dialog.json と 組みの仕様.md。"""
import json, os, shlex, shutil, subprocess, sys, uuid

ARM, ID, SHEET_PATH, SOURCE = sys.argv[1:5]
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cmd = f'. {shlex.quote(T)}/config.sh; printf "%s\\n" "$CLAUDE_BIN" "$CLAUDE_MODEL" "$WORK_DIR" "$RUNS_DIR" "$CJK_LAYOUT_DIR" "$BOOK_TYPESETTER_DIR"'
CL, MODEL, WORK, RUNS, CJK, BT = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, check=True).stdout.splitlines()
W, OUT = f"{WORK}/{ID}", f"{RUNS}/{ID}"
MAX = 12
if os.path.exists(W):
    sys.exit("作業フォルダがすでにある")
os.makedirs(OUT)
shutil.copytree(SOURCE, W + "/source")
sk = W + "/.claude/skills"
if ARM == "B":
    shutil.copytree(CJK + "/cjk-layout", sk + "/cjk-layout")
    shutil.copytree(CJK + "/cjk-layout-audit", sk + "/cjk-layout-audit")
if ARM == "C":
    shutil.copytree(BT, sk + "/book-typesetter", ignore=shutil.ignore_patterns(".git", "CLAUDE.md", "evaluation"))
SHEET = open(SHEET_PATH, encoding="utf-8").read()
FIRST = ("source フォルダにあるものを本にしたいのですが、どう組めばいいか、どう頼めばいいのか分かりません。"
         "相談に乗ってください。聞きたいことがあれば聞いてください。私が答えます。"
         "決まったら `組みの仕様.md` に書いてください。今回はまだ組まないでください。")
ENV = dict(os.environ, CLAUDE_CODE_DISABLE_CLAUDE_MDS="1", CLAUDE_CODE_DISABLE_AUTO_MEMORY="1")
COMMON = ["--setting-sources", "project", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--no-chrome", "--output-format", "json"]


def run(prompt, args, cwd):
    # 依頼文は標準入力で渡す。「-」で始まる文をコマンドの指定と誤認させないため。
    r = subprocess.run([CL, "-p", *args, *COMMON], cwd=cwd, env=ENV, capture_output=True, text=True, timeout=600, input=prompt)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {"result": "", "error": r.stderr[-400:], "total_cost_usd": 0}


sid = str(uuid.uuid4())
ALLOW = ["Read", "Write", "Edit", "Skill", "Bash(python3:*)", "Bash(ls:*)", "Bash(cat:*)"]
log, cost, msg = [], 0.0, FIRST
for turn in range(1, MAX + 1):
    args = ["--model", MODEL, "--tools", "Bash,Read,Write,Edit,Skill", "--permission-mode", "acceptEdits", f"--allowedTools={','.join(ALLOW)}"]
    args += ["--session-id", sid] if turn == 1 else ["--resume", sid]
    o = run(msg, args, W)
    said = o.get("result", "") or o.get("error", "")
    cost += o.get("total_cost_usd") or 0
    log.append({"turn": turn, "who": "実行役", "text": said})
    # 注意: 仕様の紙ができた時点で止まる。実行役が確認の途中でも打ち切られる。
    if os.path.exists(W + "/組みの仕様.md"):
        break
    resp = ("あなたは本の依頼者の役です。組版の知識はありません。下の『答えの紙』に書いてあることだけを使って、相手の質問に短く答えてください。"
            "紙に書いていないことは『分からないので、おすすめでお願いします』と答えてください。自分から提案はしません。"
            "相手が質問せず確認だけを求めているなら『それでお願いします。仕様の紙に書いてください』と答えてください。"
            f"\n\n# 答えの紙\n{SHEET}\n\n# 相手の発言\n{said}")
    a = run(resp, ["--model", MODEL, "--tools", "", "--no-session-persistence"], OUT)
    msg = a.get("result", "") or "分からないので、おすすめでお願いします"
    cost += a.get("total_cost_usd") or 0
    log.append({"turn": turn, "who": "答える役", "text": msg})
json.dump({"arm": ARM, "cost": cost, "log": log}, open(OUT + "/dialog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if os.path.exists(W + "/組みの仕様.md"):
    shutil.copy(W + "/組みの仕様.md", OUT + "/組みの仕様.md")
print(ID, ARM, "往復", sum(1 for x in log if x["who"] == "答える役"), "換算", round(cost, 2), "仕様", os.path.exists(W + "/組みの仕様.md"))
