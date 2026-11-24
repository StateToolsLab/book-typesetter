"""スマホで見るための軽い PDF を、頁の画像（灰色の JPEG）から作る。
使い方: python3 -I light_pdf.py 元.pdf 出力.pdf 画像のフォルダ [dpi=130] [品質=70] [--ltr]
- 画像のフォルダに p-01.jpg… を作り、それを並べた PDF を書く。文字の層は無い（見るだけ）。製品の PDF は別に残す。
- 頁の大きさは元の PDF から読む。右開き（縦組）として書く。左開きの本は --ltr。
- 要るもの: poppler（pdftoppm、pdfinfo）
由来: 縦組の復刻本の組み直しで、スマホで PDF が開けなかったときに作った（2026-11-06）。"""
import sys, subprocess, os, re, struct

args = [a for a in sys.argv[1:] if a != '--ltr']
ltr = '--ltr' in sys.argv[1:]
src, dst, imgd = args[:3]
dpi = args[3] if len(args) > 3 else '130'
q = args[4] if len(args) > 4 else '70'


def page_info(pdf):
    """頁数と、1 頁目の大きさ（pt）"""
    out = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True, check=True).stdout
    n = int(re.search(r'Pages:\s+(\d+)', out).group(1))
    w, h = map(float, re.search(r'Page size:\s+([\d.]+) x ([\d.]+) pts', out).groups())
    return n, w, h


def image_names(n):
    """pdftoppm が付ける名前（桁は最後の頁の番号の桁にそろう）"""
    d = len(str(n))
    return ['p-%0*d.jpg' % (d, i) for i in range(1, n + 1)]


def jpeg_size(b):
    i = 2
    while i < len(b):
        assert b[i] == 0xFF
        m = b[i + 1]
        n = struct.unpack('>H', b[i + 2:i + 4])[0]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack('>HH', b[i + 5:i + 9])
            return w, h, b[i + 9]
        i += 2 + n


def main():
    n, PW, PH = page_info(src)
    os.makedirs(imgd, exist_ok=True)
    subprocess.run(['pdftoppm', '-r', dpi, '-gray', '-jpeg', '-jpegopt', f'quality={q},optimize=y',
                    src, os.path.join(imgd, 'p')], check=True)
    files = [os.path.join(imgd, f) for f in image_names(n)]
    objs, kids = [], []

    def add(b):
        objs.append(b)
        return len(objs)

    add(b''); add(b'')  # 1 Catalog, 2 Pages
    for f in files:
        b = open(f, 'rb').read()
        w, h, c = jpeg_size(b)
        cs = b'/DeviceGray' if c == 1 else b'/DeviceRGB'
        im = add(b'<</Type/XObject/Subtype/Image/Width %d/Height %d/ColorSpace %s/BitsPerComponent 8/Filter/DCTDecode/Length %d>>\nstream\n' % (w, h, cs, len(b)) + b + b'\nendstream')
        s = b'q %.2f 0 0 %.2f 0 0 cm /I Do Q' % (PW, PH)
        ct = add(b'<</Length %d>>\nstream\n' % len(s) + s + b'\nendstream')
        kids.append(add(b'<</Type/Page/Parent 2 0 R/MediaBox[0 0 %.2f %.2f]/Resources<</XObject<</I %d 0 R>>>>/Contents %d 0 R>>' % (PW, PH, im, ct)))
    direction = b'/L2R' if ltr else b'/R2L'
    objs[0] = b'<</Type/Catalog/Pages 2 0 R/ViewerPreferences<</Direction%s>>/PageLayout/SinglePage>>' % direction
    objs[1] = b'<</Type/Pages/Count %d/Kids[%s]>>' % (len(kids), b' '.join(b'%d 0 R' % k for k in kids))
    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    off = []
    for i, o in enumerate(objs):
        off.append(len(out))
        out += b'%d 0 obj\n' % (i + 1) + o + b'\nendobj\n'
    x = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1)
    for o in off:
        out += b'%010d 00000 n \n' % o
    out += b'trailer\n<</Size %d/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, x)
    open(dst, 'wb').write(out)
    print(len(files), '頁', round(len(out) / 1e6, 1), 'MB')


if __name__ == '__main__':
    main()
