"""見る頁（ガイド線つきの HTML）を、組んだ版の PDF から作る。版を出すたびに回す。
使い方:
  python3 -I update_viewer.py 版.pdf 版面.json 出力フォルダ 題 [--note 一行] [--html viewer.html]
                              [--dpi 130] [--quality 70] [--light-pdf 軽いPDF]
- 頁の画像（灰色の JPEG）を 出力フォルダ/p/ に作る。あわせてスマホ用の軽い PDF も作る（light_pdf.py）。
  軽い PDF の置き場所は既定で 版.pdf の隣（名前の後ろに _スマホ用）。
- 文字の層から、頁ごと・行ごとの字数を数える（縦組。pdftotext -bbox）。
- viewer_template.html に、版面の値・頁・字数・題を入れて 出力フォルダ/viewer.html を書く。
  頁は 1 頁ずつ縦に並び、「見開きで見る」で偶数頁とその次の頁を並べる（綴じの向きは 版面.json の 綴じ）。
- 出力フォルダ/counts.json（字数）と files.json（Artifact などで頁と一緒に出す画像の一覧）も書く。
版面の値は本ごとの 版面.json から読む（形は references/review-guides.md）。いまは縦組だけ。
要るもの: poppler（pdftoppm、pdftotext、pdfinfo）
由来: 縦組の復刻本の組み直しで、ユーザーが頁を 1 頁ずつ確かめるために作った（2026-11-10〜25）。"""
import sys, os, re, json, subprocess, argparse, html

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from light_pdf import image_names  # noqa: E402


def load_grid(path):
    g = json.load(open(path, encoding='utf-8'))
    v = g['版面']
    if v.get('組み方向', '縦') != '縦':
        sys.exit('いまは縦組だけに対応しています（版面.json の 組み方向）')
    c = {
        'X1': float(v['1行目の字の左端_pt']),
        'LEAD': float(v['行送り_pt']),
        'FS': float(v['字の大きさ_pt']),
        'TOP': float(v['天_pt']),
        'NL': int(v['行数']),
        'NC': int(v['字数']),
    }
    lo, hi = g.get('数える範囲_pt', [c['TOP'] - c['FS'] / 2, c['TOP'] + (c['NC'] + 1) * c['FS']])
    c['range'] = (float(lo), float(hi))
    c['first'] = g.get('最初のノンブル', 1)
    c['labels'] = g.get('頁の呼び名', {})  # {"1": "扉"} のように、ノンブルの代わりに出す名
    lines = g.get('線', {})
    c['everyLine'] = int(lines.get('行ごと', 5))
    c['everyChar'] = int(lines.get('字ごと', 5))
    c['binding'] = g.get('綴じ', '右')  # 見開きの並べ方。右開き（縦組）は偶数頁が右、左開きは偶数頁が左
    if c['binding'] not in ('右', '左'):
        sys.exit('版面.json の 綴じ は「右」か「左」')
    return c


def count_lines(pdf, c):
    """頁ごとに、各行の字の数（文字の層の語の数。縦中横は 1 語＝1 字）"""
    h = subprocess.run(['pdftotext', '-bbox', pdf, '-'], capture_output=True, text=True, check=True).stdout
    lo, hi = c['range']
    out = []
    for pg in re.findall(r'<page width.*?</page>', h, re.S):
        cnt = [0] * c['NL']
        for x0, y0, x1, t in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="[\d.]+">([^<]*)<', pg):
            if not lo <= float(y0) <= hi:
                continue
            k = round((c['X1'] + c['FS'] / 2 - (float(x0) + float(x1)) / 2) / c['LEAD'])
            if 0 <= k < c['NL']:
                cnt[k] += 1
        out.append(cnt)
    return out


def main():
    ap = argparse.ArgumentParser(description='見る頁（ガイド線つき）を作る')
    ap.add_argument('pdf'); ap.add_argument('grid'); ap.add_argument('out'); ap.add_argument('title')
    ap.add_argument('--note', default='')
    ap.add_argument('--html', default='viewer.html')
    ap.add_argument('--dpi', default='130'); ap.add_argument('--quality', default='70')
    ap.add_argument('--light-pdf', default=None)
    a = ap.parse_args()

    c = load_grid(a.grid)
    info = subprocess.run(['pdfinfo', a.pdf], capture_output=True, text=True, check=True).stdout
    W, H = map(float, re.search(r'Page size:\s+([\d.]+) x ([\d.]+) pts', info).groups())
    n = int(re.search(r'Pages:\s+(\d+)', info).group(1))

    imgd = os.path.join(a.out, 'p')
    light = a.light_pdf or re.sub(r'\.pdf$', '', a.pdf) + '_スマホ用.pdf'
    subprocess.run([sys.executable, '-I', os.path.join(here, 'light_pdf.py'), a.pdf, light, imgd, a.dpi, a.quality], check=True)
    imgs = ['p/' + f for f in image_names(n)]

    counts = count_lines(a.pdf, c)
    labels = []
    for i in range(n):
        no = c['first'] + i
        labels.append(c['labels'].get(str(i + 1), f'{no} 頁'))
    note = a.note or f'{n} 頁（{labels[0]}〜{labels[-1]}）。上から順に頁が並びます。「見開きで見る」で 2 頁ずつ並べられます。指で広げると拡大できます。'
    cfg = {'W': W, 'H': H, 'X1': c['X1'], 'LEAD': c['LEAD'], 'FS': c['FS'], 'TOP': c['TOP'],
           'NL': c['NL'], 'NC': c['NC'], 'everyLine': c['everyLine'], 'everyChar': c['everyChar'],
           'title': a.title, 'note': note, 'counts': counts, 'binding': c['binding'],
           'pages': [{'img': im, 'label': lb, 'no': c['first'] + i} for i, (im, lb) in enumerate(zip(imgs, labels))]}

    s = open(os.path.join(here, 'viewer_template.html'), encoding='utf-8').read()
    s = s.replace('/*TITLE*/', html.escape(a.title))
    s = s.replace('/*CFG*/null', json.dumps(cfg, ensure_ascii=False).replace('</', '<\\/'))
    page = os.path.join(a.out, a.html)
    open(page, 'w', encoding='utf-8').write(s)
    json.dump(counts, open(os.path.join(a.out, 'counts.json'), 'w'))
    json.dump({im: im for im in imgs}, open(os.path.join(a.out, 'files.json'), 'w'), indent=0)
    print('見る頁を作った', page, n, '頁。頁と一緒に出す画像は files.json')


if __name__ == '__main__':
    main()
