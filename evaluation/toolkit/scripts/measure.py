#!/usr/bin/env python3
"""試運転の PDF を、problems.json の条件に沿って字の位置で測る。条件（A/B/C）は判定に使わず、表の列として出すだけ。

字の位置は pdftotext -bbox の語の箱から求める。語の中の字は等分とみなすので、字間は語ごとの平均。
縦中横の字の向きはこの方法では分からない。V-TCY-1 は箱の形だけ出し、合否は頁画像で見る。
使い方: measure.py [run_id ...]  結果は RUNS_DIR/measure.csv と標準出力。
"""
import csv, difflib, glob, html, json, os, re, subprocess, sys

N = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.environ.get("RUNS_DIR") or subprocess.run(["bash", "-c", f". {N}/config.sh; printf %s \"$RUNS_DIR\""], capture_output=True, text=True).stdout
SIZE = 9.5
TARGET = {"V-WIDOW-1": ("v", "p03"), "V-TCY-1": ("v", "p12"), "H-KINSOKU-1": ("h", "p13"), "H-MIXED-1": ("h", "p14")}
SKIP_NAME = re.compile(r"first|初回|shokai|initial|before|base|draft|probe|test|tmp|try|trial|old|原本|見本", re.I)
WS = re.compile(r"[\s  -​ 　﻿]+")
CJK = re.compile(r"^[ぁ-ゖァ-ヺ一-鿿]+$")


def paragraphs(kind):
    out = []
    for line in open(f"{N}/problems/manuscript_{kind}.txt", encoding="utf-8"):
        m = re.match(r"\[(p\d+)\]\s?(.*)", line.rstrip("\n"))
        if not m:
            continue
        t = re.sub(r"^(##?|>)\s", "", m.group(2))
        t = re.sub(r"｜([^《]*)《[^》]*》", r"\1", t)
        out.append((m.group(1), WS.sub("", t)))
    return out


def lines_of(pdf, kind):
    """頁ごとに行へまとめ、読む順に並べる。ルビは箱の厚みで除く。"""
    x = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
    pages = x.split("<page ")[1:]
    res = []
    for pno, pg in enumerate(pages, 1):
        words = []
        for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pg):
            x0, y0, x1, y1 = map(float, m.groups()[:4])
            t = WS.sub("", html.unescape(m.group(5)))
            if not t:
                continue
            thick, length = (x1 - x0, y1 - y0) if kind == "v" else (y1 - y0, x1 - x0)
            if thick < 8.0:
                continue
            c, s = ((x0 + x1) / 2, y0) if kind == "v" else ((y0 + y1) / 2, x0)
            words.append(dict(c=c, s=s, len=length, t=t, thick=thick))
        words.sort(key=lambda w: (-w["c"] if kind == "v" else w["c"]))
        cur = []
        for w in words:
            if cur and abs(w["c"] - cur[-1]["c"]) > 4:
                res.append((pno, sorted(cur, key=lambda a: a["s"])))
                cur = []
            cur.append(w)
        if cur:
            res.append((pno, sorted(cur, key=lambda a: a["s"])))
    return res, len(pages)


def advances(line):
    """和字の字送りの、字の大きさからのずれ（比）。"""
    d = []
    for w in line:
        if len(w["t"]) >= 2 and CJK.match(w["t"]):
            d.append(w["len"] / len(w["t"]) / SIZE - 1)
    for a, b in zip(line, line[1:]):
        if len(a["t"]) == 1 and len(b["t"]) == 1 and CJK.match(a["t"]) and CJK.match(b["t"]):
            d.append((b["s"] - a["s"]) / SIZE - 1)
    return d


def analyze(pdf, kind):
    ls, npages = lines_of(pdf, kind)
    texts = ["".join(w["t"] for w in l) for _, l in ls]
    whole = "".join(texts)
    starts, p = [], 0
    for t in texts:
        starts.append((p, p + len(t)))
        p += len(t)
    # 行末のハイフンは字の差に数えない。段落は頭と尾の 10 字で探し、中身の差は diffs に残す。
    keep = [k for k, ch in enumerate(whole) if ch not in "-‐"]
    plain = "".join(whole[k] for k in keep)
    keep.append(len(whole))
    paras, pos, missing, diffs = {}, 0, [], []
    for pid, t in paragraphs(kind):
        t = t.replace("-", "").replace("‐", "")
        n = min(10, len(t))
        i = plain.find(t[:n], pos)
        e = plain.find(t[-n:], i) if i >= 0 else -1
        if i < 0 or e < 0 or e + n - i > len(t) * 1.3:
            missing.append(pid)
            continue
        got = plain[i:e + n]
        if got != t:
            ops = [(tag, t[a:b], got[c:d]) for tag, a, b, c, d in difflib.SequenceMatcher(None, t, got, autojunk=False).get_opcodes() if tag != "equal"]
            diffs.append(f"{pid}:{ops[:3]}")
        a0, b0 = keep[i], keep[e + n - 1] + 1
        idx = [k for k, (a, b) in enumerate(starts) if a < b0 and b > a0]
        paras[pid] = dict(idx=idx, nlines=len(idx), last=min(starts[idx[-1]][1], b0) - max(starts[idx[-1]][0], a0), page=ls[idx[0]][0])
        pos = e + n
    missing = missing + diffs
    return dict(ls=ls, texts=texts, paras=paras, missing=missing, npages=npages)


def judge(a, prob):
    kind, pid = TARGET[prob]
    r = {"text_ok": not any(m.split(":")[0] == pid for m in a["missing"]), "missing": " ".join(a["missing"][:6]), "pages": a["npages"]}
    p = a["paras"].get(pid)
    if not p:
        r["verdict"] = "段落が見つからない"
        return r
    r.update(page=p["page"], nlines=p["nlines"], last=p["last"])
    adv = [d for k in p["idx"] for d in advances(a["ls"][k][1])]
    r["adv_min"], r["adv_max"] = (round(min(adv) * 100, 1), round(max(adv) * 100, 1)) if adv else ("", "")
    in_range = bool(adv) and min(adv) >= -0.03 - 1e-3 and max(adv) <= 0.07 + 1e-3
    tl = [a["texts"][k] for k in p["idx"]]
    if prob == "V-WIDOW-1":
        ok = p["last"] >= 3
        r["detail"] = f"最終行 {p['last']} 字"
    elif prob == "H-KINSOKU-1":
        ok = any("3.5kg" in t for t in tl)
        r["detail"] = "3.5 と kg が同じ行" if ok else "分かれている"
    elif prob == "H-MIXED-1":
        word = "internationalization"
        same = any(word in t for t in tl)
        hy = any(re.search(r"[a-z]+-$", t) for t in tl)
        ok = same or hy
        r["detail"] = "同じ行" if same else ("ハイフンで分割（区切りは未確認）" if hy else "分割（ハイフンなし）")
    else:
        ds = [(w["t"], round(w["len"], 1), round(w["thick"], 1)) for k in p["idx"] for w in a["ls"][k][1] if re.fullmatch(r"[0-9０-９]+", w["t"])]
        ok = None
        r["detail"] = "数字の箱 " + str(ds[:6])
    r["goal"] = ok
    r["in_range"] = in_range
    if ok is None:
        r["verdict"] = "画像で判定"
    else:
        r["verdict"] = "合格" if ok and in_range and r["text_ok"] else ("目標は解消、条件の外" if ok else "未解消")
    return r


def choose(run, kind, target):
    cands = [p for p in glob.glob(f"{RUNS}/{run}/work/**/*.pdf", recursive=True)]
    good = []
    for p in cands:
        try:
            a = analyze(p, kind)
        except Exception:
            continue
        if target in a["paras"]:
            good.append((p, a))
    final = [g for g in good if not SKIP_NAME.search(os.path.basename(g[0]))] or good
    final.sort(key=lambda g: os.path.getmtime(g[0]))
    first = [g for g in good if SKIP_NAME.search(os.path.basename(g[0]))]
    return (final[-1] if final else None), (first[0] if first else None), len(cands)


def main():
    rows = [r for r in csv.DictReader(open(f"{N}/manifest.csv"))]
    only = set(sys.argv[1:])
    out = []
    for r in rows:
        ids = [r["run"] + "r", r["run"]] if r["exe"] == "codex" else [r["run"]]
        for run in ids:
            if not os.path.exists(f"{RUNS}/{run}/meta.txt") or (only and run not in only):
                continue
            kind, pid = TARGET[r["problem"]]
            f, base, n = choose(run, kind, pid)
            m = open(f"{RUNS}/{run}/meta.txt").read()
            row = dict(run=run, exe=r["exe"], tool=r["tool"], arm=r["arm"], problem=r["problem"], mode=r["mode"],
                       rc=re.search(r"rc=(\d+)", m).group(1), sec=re.search(r"seconds=(\d+)", m).group(1), npdf=n)
            if not f:
                row["verdict"] = "PDF なし"
            else:
                row["pdf"] = os.path.relpath(f[0], f"{RUNS}/{run}/work")
                row.update(judge(f[1], r["problem"]))
                if base:
                    b = judge(base[1], r["problem"])
                    row["base"] = f"{os.path.basename(base[0])}: {b.get('nlines')}行 最終{b.get('last')}字 {b.get('pages')}頁 {b.get('detail','')[:30]}"
            out.append(row)
    cols = ["run", "exe", "tool", "arm", "problem", "mode", "rc", "sec", "npdf", "pdf", "verdict", "detail", "text_ok", "in_range", "adv_min", "adv_max", "page", "nlines", "last", "pages", "missing", "base"]
    with open(f"{RUNS}/measure.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    out.sort(key=lambda x: (x["exe"], x["tool"], x["problem"], x["arm"], x["run"]))
    for x in out:
        print(x["exe"][:2], x["tool"][:2], x["problem"], x["arm"], x["run"], "rc" + x["rc"], x["sec"] + "s", "|", x.get("verdict"), "|", x.get("detail", "")[:60], "| text", x.get("text_ok"), "| adv", x.get("adv_min"), x.get("adv_max"), "| 頁", x.get("page"), "全", x.get("pages"), "| 行", x.get("nlines"), "末", x.get("last"), "|", x.get("pdf", "")[:28], "| 欠", x.get("missing", "")[:70], "| 初:", x.get("base", "")[:60])


main()
