"""
Reklam slaytı üretici.

~/Downloads altındaki kaynak fotoğraflardan, tek bir HTML şablonuyla
hem tam boy (ads/, 900x1280) hem yarım boy (ads_preview/, 900x380) PNG
üretir. Aynı foto, aynı crop_focus noktası merkez alınarak farklı
en-boy oranlarında kesilir (rastgele üstten kesme yok). Chrome
--force-device-scale-factor=2 ile render edilip Pillow/LANCZOS ile
hedef boyuta düşürülerek metin netliği artırılır.

Kullanım:
    python3 generate_ads.py
"""

import base64
import mimetypes
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

# ============================================================================
# 📁 YOLLAR
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent
PHOTOS_DIR = Path.home() / "Downloads"
ADS_DIR = BASE_DIR / "ads"
ADS_PREVIEW_DIR = BASE_DIR / "ads_preview"
FONTS_DIR = BASE_DIR / "fonts"

FULL_SIZE = (900, 1280)
STRIP_SIZE = (900, 380)
RENDER_SCALE = 2  # 2x süpersample edip hedef boyuta düşürülüyor (metin netliği)

# ============================================================================
# 🎨 KATEGORİ RENKLERİ (mevcut slide'lardaki renklere sadık)
# ============================================================================
ACCENT_COLORS = {
    "grip_asisi": "#4FA8FF",       # mavi
    "hpv_asisi": "#FF5C9A",        # pembe
    "zaturre_asisi": "#B98CFF",    # mor
    "yaz_1_gunes": "#FF9F45",      # turuncu
    "yaz_2_su": "#FF9F45",
    "yaz_3_sicak": "#FF9F45",
    "yaz_4_beslenme": "#FF9F45",
}
DEFAULT_ACCENT = "#FF9F45"

# ============================================================================
# 🎬 SLAYT İÇERİKLERİ
# ============================================================================
SLIDES = [
    {"out": "grip_asisi", "photo": "grip_foto.jpg",
     "category": "SONBAHAR SAĞLIĞI · İZMİR", "tag": "GRİP AŞISI",
     "title": "Sezonu Kaçırmayın",
     "body": "Grip sezonu başlamadan bağışıklığınızı güçlendirin. Özellikle 65 yaş üstü, kronik hastalığı olanlar ve sağlık çalışanları için önerilir.",
     "footer_left": "GRİP AŞISI MEVCUTTUR",
     "crop_focus": "50% 65%"},
    {"out": "hpv_asisi", "photo": "hpv_foto.jpg",
     "category": "KORUYUCU SAĞLIK · İZMİR", "tag": "HPV AŞISI",
     "title": "Erken Yaşta Koruma Sağlar",
     "body": "HPV aşısı, rahim ağzı kanseri başta olmak üzere birçok HPV kaynaklı kanser türüne karşı etkili koruma sunar. Doktorunuza danışabilirsiniz.",
     "footer_left": "HPV AŞISI HAKKINDA BİLGİ ALIN",
     "crop_focus": "50% 40%"},
    {"out": "zaturre_asisi", "photo": "zaturre_foto.jpg",
     "category": "SONBAHAR SAĞLIĞI · İZMİR", "tag": "ZATÜRRE AŞISI",
     "title": "65 Yaş Üstü İçin Önemli",
     "body": "Zatürre aşısı, özellikle 65 yaş üstü ve kronik hastalığı olan bireyleri ciddi solunum yolu enfeksiyonlarından korur.",
     "footer_left": "ZATÜRRE AŞISI MEVCUTTUR",
     "crop_focus": "70% 35%"},
    {"out": "yaz_1_gunes", "photo": "foto1.jpg",
     "category": "YAZ SAĞLIĞI · İZMİR", "tag": "01 / 04",
     "title": "Güneş Koruyucu",
     "body": "En az SPF 50 güneş kremi kullanın. Her 2 saatte bir yenileyin. Suya girdikten sonra mutlaka tekrarlayın.",
     "footer_left": "SAĞLIKLI YAZ",
     "crop_focus": "50% 50%"},
    {"out": "yaz_2_su", "photo": "foto2.jpg",
     "category": "YAZ SAĞLIĞI · İZMİR", "tag": "02 / 04",
     "title": "Yeterli Su",
     "body": "İzmir'de yaz sıcaklıkları 40°C'yi aşabilir. Susuzluk hissetmeden günde en az 3 litre su için.",
     "footer_left": "SAĞLIKLI YAZ",
     "crop_focus": "60% 45%"},
    {"out": "yaz_3_sicak", "photo": "foto3.jpg",
     "category": "YAZ SAĞLIĞI · İZMİR", "tag": "03 / 04",
     "title": "Sıcak Çarpması",
     "body": "11:00–16:00 arası dışarıda kalmaktan kaçının. Baş dönmesi veya bulantı hissinde hemen serin bir yere geçin.",
     "footer_left": "SAĞLIKLI YAZ",
     "crop_focus": "50% 60%"},
    {"out": "yaz_4_beslenme", "photo": "foto4.jpg",
     "category": "YAZ SAĞLIĞI · İZMİR", "tag": "04 / 04",
     "title": "Hafif Beslenin",
     "body": "Ağır ve yağlı yemeklerden kaçının. Taze meyve, sebze ve probiyotikleri tercih edin.",
     "footer_left": "SAĞLIKLI YAZ",
     "crop_focus": "70% 40%"},
]

# ============================================================================
# 🔤 FONT — Plus Jakarta Sans gerçek Regular/Medium/Bold ağırlıkları
# (sentetik kalınlaştırma yerine gerçek glifler; body >=500 şartı için gerekli)
# ============================================================================
FONT_SOURCES = {
    400: (
        "PlusJakartaSans-Regular.ttf",
        "https://github.com/tokotype/PlusJakartaSans/raw/master/fonts/ttf/PlusJakartaSans-Regular.ttf",
    ),
    500: (
        "PlusJakartaSans-Medium.ttf",
        "https://github.com/tokotype/PlusJakartaSans/raw/master/fonts/ttf/PlusJakartaSans-Medium.ttf",
    ),
    700: (
        "PlusJakartaSans-Bold.ttf",
        "https://github.com/tokotype/PlusJakartaSans/raw/master/fonts/ttf/PlusJakartaSans-Bold.ttf",
    ),
}


def ensure_fonts():
    """Regular/Medium/Bold ttf dosyalarını fonts/ altına indirir (yoksa)."""
    import urllib.request

    FONTS_DIR.mkdir(exist_ok=True)
    weight_paths = {}
    for weight, (filename, url) in FONT_SOURCES.items():
        path = FONTS_DIR / filename
        if not path.exists():
            try:
                print(f"⬇️  {filename} indiriliyor...")
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"⚠️  {filename} indirilemedi ({e}), bu ağırlık atlanacak")
                continue
        weight_paths[weight] = path
    return weight_paths


def build_font_face_css(weight_paths):
    faces = []
    for weight, path in weight_paths.items():
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        faces.append(f"""
        @font-face {{
            font-family: 'Plus Jakarta Sans';
            src: url(data:font/ttf;base64,{b64}) format('truetype');
            font-weight: {weight};
            font-style: normal;
        }}""")
    return "\n".join(faces)


def photo_data_uri(filename):
    path = PHOTOS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Kaynak fotoğraf bulunamadı: {path}")
    mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


# ============================================================================
# 🌐 CHROME
# ============================================================================
def find_chrome():
    import os

    env_path = os.environ.get("CHROME_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c

    raise RuntimeError(
        "Chrome/Chromium bulunamadı. CHROME_PATH ortam değişkenini Chrome "
        "binary'sinin tam yoluna ayarlayın."
    )


def render_html_to_png(html_str, size, output_path, scale=RENDER_SCALE):
    """HTML'i headless Chrome ile scale× render edip Pillow ile size'a düşürür (lossless PNG)."""
    width, height = size
    chrome_bin = find_chrome()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        html_path = tmp_dir / "slide.html"
        html_path.write_text(html_str, encoding="utf-8")

        shot_path = tmp_dir / "shot.png"

        cmd = [
            chrome_bin,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--disable-extensions",
            f"--force-device-scale-factor={scale}",
            f"--window-size={width},{height}",
            f"--screenshot={shot_path}",
            html_path.as_uri(),
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)

        with Image.open(shot_path) as shot:
            shot = shot.convert("RGB")
            resized = shot.resize((width, height), Image.LANCZOS)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            resized.save(output_path, format="PNG", optimize=True)


# ============================================================================
# 🎨 TEK HTML ŞABLONU (tam boy / yarım boy aynı şablon, sadece boyut + ölçek)
# ============================================================================
def build_slide_html(slide, size, font_face_css, font_scale=1.0):
    """
    size: (width, height) — (900,1280) tam boy ya da (900,380) yarım boy.
    font_scale: yarım boy için ~0.42 gibi bir küçültme oranı (title/body orantılı küçülür,
                satır sayısı aynı kalsın diye satır yüksekliği/max-width de orantılı ayarlanır).
    """
    width, height = size
    accent = ACCENT_COLORS.get(slide["out"], DEFAULT_ACCENT)
    photo_src = photo_data_uri(slide["photo"])

    title_size = round(64 * font_scale, 1)
    body_size = round(22 * font_scale, 1)
    category_size = round(15 * font_scale, 1)
    tag_size = round(15 * font_scale, 1)
    footer_left_size = round(13 * font_scale, 1)
    brand_size = round(17 * font_scale, 1)
    sub_size = round(12 * font_scale, 1)

    pad_h = round(56 * font_scale, 1)
    pad_top = round(48 * font_scale, 1)
    pad_bottom = round(40 * font_scale, 1)
    gap = round(10 * font_scale, 1)

    # Alt koyu taban fotoğrafın alt %35-45'i; yarım boy düşük olduğu için
    # oransal olarak biraz daha yüksek bir yüzdeye ihtiyaç duyar (metin bloğu sığsın diye).
    scrim_height_pct = 42 if height >= 900 else 78

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{font_face_css}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {width}px; height: {height}px; overflow: hidden; }}
body {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
}}
.stage {{
    position: relative; width: {width}px; height: {height}px; overflow: hidden; background: #000;
}}
.bg {{
    position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: {slide['crop_focus']};
}}
.top-category {{
    position: absolute; top: {pad_top}px; left: {pad_h}px;
    font-weight: 600; font-size: {category_size}px; letter-spacing: 0.12em;
    color: {accent};
    text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased;
}}
.bottom-scrim {{
    position: absolute; left: 0; right: 0; bottom: 0; height: {scrim_height_pct}%;
    background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.75) 40%, rgba(0,0,0,0) 100%);
}}
.bottom-content {{
    position: absolute; left: 0; right: 0; bottom: 0;
    padding: 0 {pad_h}px {pad_bottom}px;
}}
.tag {{
    display: inline-block; font-weight: 600; font-size: {tag_size}px; letter-spacing: 0.1em;
    color: {accent}; margin-bottom: {gap}px;
    text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased;
}}
.title {{
    font-weight: 700; font-size: {title_size}px; line-height: 1.12; color: #ffffff;
    margin-bottom: {gap}px;
    text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased;
}}
.body {{
    font-weight: 500; font-size: {body_size}px; line-height: 1.42; color: rgba(235,235,240,0.92);
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
    margin-bottom: {gap * 1.6}px;
    text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased;
}}
.divider {{
    height: 1px; background: rgba(255,255,255,0.18); margin-bottom: {gap * 1.4}px;
}}
.bottom-row {{
    display: flex; align-items: flex-end; justify-content: space-between;
}}
.footer-left {{
    font-weight: 600; font-size: {footer_left_size}px; letter-spacing: 0.08em; color: {accent};
    text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased;
}}
.footer-right {{
    position: relative;
    text-align: right;
    padding: {gap * 0.8}px {gap * 1.4}px;
}}
/* KRİTİK: sağ alttaki "Kuşdemir Eczanesi" yazısının arkasına, fotoğraf o
   bölgede açık renkli olsa bile okunaklılığı garanti eden lokal bir scrim. */
.footer-right::before {{
    content: "";
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at bottom right, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 75%);
    border-radius: 12px;
}}
.brand {{
    position: relative;
    font-weight: 700; font-size: {brand_size}px; color: #ffffff;
    text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased;
}}
.sub {{
    position: relative;
    font-weight: 500; font-size: {sub_size}px; color: rgba(220,220,225,0.85); margin-top: 2px;
    text-rendering: optimizeLegibility; -webkit-font-smoothing: antialiased;
}}
</style>
</head>
<body>
    <div class="stage">
        <img class="bg" src="{photo_src}">
        <div class="top-category">{slide['category']}</div>
        <div class="bottom-scrim"></div>
        <div class="bottom-content">
            <div class="tag">{slide['tag']}</div>
            <div class="title">{slide['title']}</div>
            <div class="body">{slide['body']}</div>
            <div class="divider"></div>
            <div class="bottom-row">
                <div class="footer-left">{slide['footer_left']}</div>
                <div class="footer-right">
                    <div class="brand">KUŞDEMİR ECZANESİ</div>
                    <div class="sub">Karşıyaka · İzmir</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_content


# ============================================================================
# 🚀 ANA AKIŞ
# ============================================================================
def main():
    weight_paths = ensure_fonts()
    font_face_css = build_font_face_css(weight_paths)

    ADS_DIR.mkdir(exist_ok=True)
    ADS_PREVIEW_DIR.mkdir(exist_ok=True)

    total = len(SLIDES) * 2
    done = 0

    for slide in SLIDES:
        out = slide["out"]
        print(f"🎬 {out} üretiliyor...")

        try:
            full_html = build_slide_html(slide, FULL_SIZE, font_face_css, font_scale=1.0)
            render_html_to_png(full_html, FULL_SIZE, ADS_DIR / f"{out}.png")
            done += 1
            print(f"  ✅ ads/{out}.png")
        except Exception as e:
            print(f"  ❌ ads/{out}.png üretilemedi: {e}")

        try:
            # Yarım boy: aynı başlık/gövde, oransal küçültülmüş font.
            # STRIP_SIZE.height / FULL_SIZE.height ~ 0.297 iken okunabilirlik için
            # biraz daha büyük tutulan sabit bir ölçek kullanılıyor (satır sayısı korunuyor).
            strip_html = build_slide_html(slide, STRIP_SIZE, font_face_css, font_scale=0.42)
            render_html_to_png(strip_html, STRIP_SIZE, ADS_PREVIEW_DIR / f"{out}.png")
            done += 1
            print(f"  ✅ ads_preview/{out}.png")
        except Exception as e:
            print(f"  ❌ ads_preview/{out}.png üretilemedi: {e}")

    print(f"🏁 {done}/{total} üretildi.")


if __name__ == "__main__":
    main()
