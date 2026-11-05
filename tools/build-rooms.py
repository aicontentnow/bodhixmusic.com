"""Build the era room pages for bodhixmusic.com.
python3 build-rooms.py <site root> <fonts dir> <covers dir> <icons.json>
Each room wears its own album's look. Every room keeps the BODHI X strip (home) at the top
and Back to BODHI X at the bottom. Text is Bodhi's history as he told it, plus the Bandcamp credits."""
import sys, os, json, shutil, html
from PIL import Image

ROOT, FONTS, COVERS, ICONS = sys.argv[1:5]
I = json.load(open(ICONS))
BC = "https://scottytuesday.bandcamp.com"
SPOTIFY = "https://open.spotify.com/artist/1jKYWx4scefBPx9Z6tCu8C"
YT_ST = "https://www.youtube.com/@ScottValentine1975"

def ico(k):
    return f'<svg class="ico" aria-hidden="true" focusable="false"><use href="#i-{k}"/></svg>'

def sprite(keys):
    syms = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24"><path d="{I[k]}"/></symbol>' for k in keys)
    return f'<svg class="icon-sprite" aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden" xmlns="http://www.w3.org/2000/svg">{syms}</svg>'

def font(fam, pkg, file, weight, style="normal"):
    return (pkg, file, f'@font-face{{font-family:"{fam}";src:url("/assets/rooms/fonts/{file}") format("woff2");font-weight:{weight};font-style:{style};font-display:swap}}')

def cover(src_name, slug, out_name):
    """Copy an album cover at up to 1200 and at 600; return (path1200, path600, w, h)."""
    im = Image.open(os.path.join(COVERS, src_name)).convert("RGB")
    d = os.path.join(ROOT, "assets/rooms", slug); os.makedirs(d, exist_ok=True)
    big = im if im.width <= 1200 else im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    big.save(os.path.join(d, f"{out_name}-1200.jpg"), quality=84, optimize=True, progressive=True)
    small = im.resize((600, round(im.height * 600 / im.width)), Image.LANCZOS) if im.width > 600 else im
    small.save(os.path.join(d, f"{out_name}-600.jpg"), quality=84, optimize=True, progressive=True)
    return (f"/assets/rooms/{slug}/{out_name}-1200.jpg", f"/assets/rooms/{slug}/{out_name}-600.jpg", big.width, big.height)

def og_image(src_name, slug, bg):
    im = Image.open(os.path.join(COVERS, src_name)).convert("RGB")
    og = Image.new("RGB", (1200, 630), bg)
    s = 630 / im.height
    c = im.resize((round(im.width * s), 630), Image.LANCZOS)
    og.paste(c, ((1200 - c.width) // 2, 0))
    p = f"/assets/rooms/{slug}/og-{slug}.jpg"
    og.save(ROOT + p, quality=84)
    return p

def tracks_html(tracks, label, collapse_after=None):
    lis = "".join(f'<li><span class="t">{html.escape(t)}</span><span class="d">{d}</span></li>' for t, d in tracks)
    ol = f'<ol class="tracks" aria-label="{html.escape(label)} track list">{lis}</ol>'
    if collapse_after and len(tracks) > collapse_after:
        return f'<details class="more-tracks"><summary>All {len(tracks)} songs</summary>{ol}</details>'
    return ol

PLAY_ICO = '<svg class="ico" aria-hidden="true" focusable="false" viewBox="0 0 24 24"><path d="M7 4.5v15l13-7.5z" fill="currentColor"/></svg>'

def play_button(album_id, title, room, room_href, cover_src):
    return (f'<button type="button" class="btn hot play-album" data-album="{album_id}" data-title="{html.escape(title)}" '
            f'data-room="{html.escape(room)}" data-room-href="{room_href}" data-cover="{cover_src}">{PLAY_ICO}'
            f'<span class="pa-label">Play {html.escape(title)}</span></button>')

def btn(href, label, icon, hot=False):
    return f'<a class="btn{" hot" if hot else ""}" href="{href}" target="_blank" rel="me noopener">{ico(icon)}<span>{label}</span></a>'

def lineup(people):
    return '<ul class="lineup">' + "".join(f'<li><b>{html.escape(n)}</b><span>{html.escape(r)}</span></li>' for n, r in people) + '</ul>'

BASE_CSS = '''
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;min-height:100vh;color:var(--ink);font-family:var(--body-font);font-size:17px;line-height:1.65;background:var(--page-bg);-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{position:relative;z-index:1;max-width:940px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-left,0px))}
.spine{position:relative;z-index:2;display:flex;justify-content:space-between;align-items:center;padding:calc(env(safe-area-inset-top,0px) + 10px) max(16px,env(safe-area-inset-left,0px)) 10px;font-family:"Inter",system-ui,sans-serif}
.spine a{display:inline-flex;align-items:center;gap:10px;min-height:44px;text-decoration:none;color:var(--spine);font-size:11px;letter-spacing:.24em;text-transform:uppercase;font-variation-settings:"opsz" 32}
.spine .home span{font-size:12px;letter-spacing:.30em}
.spine img{display:block}
.hero{display:grid;gap:28px;align-items:center;padding:28px 0 8px}
@media (min-width:760px){.hero{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:48px;padding-top:44px}}
.cover{margin:0}
.cover img{display:block;width:100%;height:auto;box-shadow:var(--cover-shadow)}
.kicker{font-family:var(--label-font);font-size:13px;letter-spacing:.28em;text-transform:uppercase;color:var(--ink-2);margin:0 0 10px}
h1{font-family:var(--title-font);margin:0;line-height:.95;color:var(--title)}
.lede{font-size:19px;margin:18px 0 0}
section{padding:46px 0 0}
h2{font-family:var(--label-font);font-weight:var(--h2-weight,600);text-transform:uppercase;letter-spacing:.2em;font-size:14px;margin:0 0 18px;display:flex;align-items:center;gap:14px;color:var(--ink)}
h2::after{content:"";flex:1;height:2px;background:var(--rule)}
h3{font-family:var(--title-font);font-weight:400;margin:0 0 6px;font-size:28px;line-height:1.1;color:var(--title)}
.story p{margin:0 0 16px;max-width:64ch}
.album{display:grid;gap:22px;margin:0 0 34px}
@media (min-width:760px){.album{grid-template-columns:220px minmax(0,1fr);gap:32px;align-items:start}}
.album .cover img{box-shadow:var(--cover-shadow)}
.meta{color:var(--ink-2);font-size:14px;margin:0 0 14px;font-family:var(--label-font);letter-spacing:.12em;text-transform:uppercase}
.player{border:0;width:100%;max-width:640px;display:block;background:var(--player-bg);margin:0 0 6px}
.tracks{list-style:none;margin:0;padding:0;max-width:640px;counter-reset:t}
.tracks li{counter-increment:t;display:flex;align-items:baseline;gap:14px;padding:9px 0;border-bottom:1px solid var(--line)}
.tracks li::before{content:counter(t,decimal-leading-zero);font-family:var(--label-font);color:var(--accent);font-size:14px;min-width:2ch}
.tracks .t{flex:1}
.tracks .d{color:var(--ink-2);font-size:14px;font-variant-numeric:tabular-nums}
.more-tracks summary{cursor:pointer;min-height:44px;display:inline-flex;align-items:center;font-family:var(--label-font);letter-spacing:.18em;text-transform:uppercase;font-size:13px;color:var(--accent);border-bottom:1px solid currentColor}
.more-tracks[open] summary{margin-bottom:10px}
.note{color:var(--ink-2);font-size:15px;margin:14px 0 0;max-width:64ch}
.lineup{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(180px,100%),1fr));gap:10px;max-width:780px;margin:0;padding:0;list-style:none}
.lineup li{background:var(--card);border:1px solid var(--line);padding:14px 16px}
.lineup b{display:block;font-family:var(--label-font);font-weight:600;font-size:17px;letter-spacing:.04em;color:var(--ink)}
.lineup span{color:var(--ink-2);font-size:14px}
.btns{display:flex;flex-direction:column;gap:10px;max-width:420px}
.btn{display:flex;align-items:center;gap:12px;min-height:52px;padding:0 18px;text-decoration:none;font-family:var(--label-font);font-weight:600;font-size:14px;letter-spacing:.16em;text-transform:uppercase;border:2px solid var(--ink);color:var(--ink);background:transparent;transition:background .2s,color .2s,border-color .2s}
.btn .ico{width:20px;height:20px;fill:currentColor;flex:none}
.btn.hot{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
button.btn{font:inherit;font-family:var(--label-font);font-weight:600;font-size:14px;letter-spacing:.16em;text-transform:uppercase;width:100%;cursor:pointer;text-align:left}
.play-album.is-loaded{background:transparent;color:var(--ink);border-color:var(--ink)}
.play-row{margin:0 0 14px}
.cover-note{margin:8px 0 0;font-size:13px;color:var(--ink-2);font-style:italic;line-height:1.4}
h1[tabindex="-1"]:focus{outline:none}
.btn:hover,.btn:focus-visible{background:var(--ink);border-color:var(--ink);color:var(--bg)}
a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.foot{position:relative;z-index:1;margin-top:64px;padding:22px max(16px,env(safe-area-inset-left,0px)) calc(env(safe-area-inset-bottom,0px) + 26px);border-top:1px solid var(--line);display:flex;flex-wrap:wrap;gap:8px 24px;justify-content:space-between;align-items:center;font-family:"Inter",system-ui,sans-serif;font-size:12px;color:var(--ink-2)}
.foot a{text-decoration:none;letter-spacing:.24em;text-transform:uppercase;font-size:11px;min-height:44px;display:inline-flex;align-items:center}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
'''

def page(r):
    fonts_css = "\n".join(f[2] for f in r["fonts"])
    preload = "".join(f'<link rel="preload" href="/assets/rooms/fonts/{f[1]}" as="font" type="font/woff2" crossorigin>' for f in r["fonts"][:1])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{r["name_plain"]} | BODHI X</title>
<meta name="description" content="{html.escape(r["desc"])}">
<link rel="canonical" href="https://bodhixmusic.com/{r["slug"]}/">
<link rel="icon" type="image/svg+xml" href="/assets/marks/favicon.svg">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta name="theme-color" content="{r["theme_color"]}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="BODHI X">
<meta property="og:title" content="{r["name_plain"]} | BODHI X">
<meta property="og:description" content="{html.escape(r["desc"])}">
<meta property="og:url" content="https://bodhixmusic.com/{r["slug"]}/">
<meta property="og:image" content="https://bodhixmusic.com{r["og"]}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{preload}
<link rel="stylesheet" href="/assets/tokens/tokens.css">
<link rel="stylesheet" href="/assets/css/bodhix.css">
<script src="/assets/js/dock.js" defer></script>
<style>
{fonts_css}
:root{{{r["vars"]}}}
{BASE_CSS}
{r["css"]}
</style>
</head>
<body>
{sprite(r["icons"])}
<header class="spine">
  <a class="home" href="/" aria-label="BODHI X home"><img src="/assets/marks/ring-year.svg" alt="" width="20" height="20"><span>BODHI X</span></a>
  <a href="/#eras-title">All rooms</a>
</header>
<main class="wrap">
{r["body"]}
</main>
<footer class="foot">
  <span>{r["name_plain"]} is a room in the BODHI X house.</span>
  <a href="/">Back to BODHI X</a>
</footer>
</body>
</html>
'''

def copy_fonts(fonts):
    d = os.path.join(ROOT, "assets/rooms/fonts"); os.makedirs(d, exist_ok=True)
    for pkg, file, _ in fonts:
        shutil.copy(os.path.join(FONTS, pkg, "package/files", file), os.path.join(d, file))
        lic = os.path.join(FONTS, pkg, "package/LICENSE")
        if os.path.exists(lic):
            shutil.copy(lic, os.path.join(d, f"LICENSE-{pkg}.txt"))

NOT_ORIG = '<figcaption class="cover-note">The cover here is not the original album art.</figcaption>'

def album_block(cov, title_html, meta, pid, ptitle, bg, link, tracks, collapse=None, note="", btns="", room=None, not_original=False):
    c1200, c600, w, h = cov
    return f'''<div class="album">
  <figure class="cover"><img src="{c1200}" srcset="{c600} 600w, {c1200} {w}w" sizes="(min-width:760px) 220px, 92vw" width="{w}" height="{h}" alt="Cover of {html.escape(ptitle)}" loading="lazy">{NOT_ORIG if not_original else ""}</figure>
  <div>
    <h3>{title_html}</h3>
    <p class="meta">{meta}</p>
    <div class="btns play-row">{play_button(pid, ptitle, room[0], room[1], c600)}</div>
    {tracks_html(tracks, ptitle, collapse)}
    {f'<p class="note">{note}</p>' if note else ""}
    {f'<div class="btns" style="margin-top:16px">{btns}</div>' if btns else ""}
  </div>
</div>'''

rooms = []

# ---------------- HEAVY SUN ----------------
slug = "heavy-sun"
f_hs = [font("Permanent Marker", "permanent-marker", "permanent-marker-latin-400-normal.woff2", 400),
        font("Barlow Condensed", "barlow-condensed", "barlow-condensed-latin-400-normal.woff2", 400),
        font("Barlow Condensed", "barlow-condensed", "barlow-condensed-latin-600-normal.woff2", 600)]
cov = cover("heavy.jpg", slug, "greatest-hits")
gh_tracks = [("Lady Lucifer","4:38"),("Fall","4:39"),("Whose Gonna Tell Your Baby Boy You Think His Future Doesn't Matter?","5:58"),("Mourning Light","4:45"),("Vision","3:52"),("Save The World","3:53"),("Princess","3:32"),("Million Dollar Sweepstakes","3:24"),("Awake","5:42"),("Goodnight Gentle Soul","3:35"),("Gone","5:10"),("I Found Love In U","3:11"),("Caveman","5:23"),("Chicken","2:49"),("Mommy","4:04")]
rooms.append(dict(
    slug=slug, name_plain="Heavy Sun", theme_color="#FBF3E2", fonts=f_hs, icons=["bandcamp"],
    desc="Heavy Sun: the first band. Victoria to Vancouver, 1994 to 2002. Greatest Hits on Bandcamp.",
    og=og_image("heavy.jpg", slug, (251, 243, 226)),
    vars='--bg:#FBF3E2;--ink:#1D1A17;--ink-2:#6B5E50;--title:#1D1A17;--accent:#C8441C;--on-accent:#fff;--rule:linear-gradient(90deg,#E8892B,#C8441C,transparent);--line:rgba(29,26,23,.14);--card:rgba(255,255,255,.6);--player-bg:#fff;--spine:#1D1A17;--cover-shadow:0 18px 40px rgba(120,60,10,.25);--title-font:"Permanent Marker",cursive;--label-font:"Barlow Condensed",sans-serif;--body-font:"Barlow Condensed",sans-serif;--page-bg:radial-gradient(60% 50% at 50% 0%,rgba(242,176,53,.35),transparent 70%),repeating-conic-gradient(from 0deg at 50% -10%,rgba(232,137,43,.10) 0 6deg,transparent 6deg 12deg),#FBF3E2',
    css='body{font-size:19px;background-attachment:fixed}h1{font-size:clamp(56px,13vw,112px);color:#1D1A17;transform:rotate(-2deg);text-shadow:4px 4px 0 #F2B035}.lede{font-size:22px}.tracks .t{font-size:19px}.kicker{color:#C8441C}',
    body=f'''<div class="hero">
  <figure class="cover"><img src="{cov[0]}" srcset="{cov[1]} 600w, {cov[0]} {cov[2]}w" sizes="(min-width:760px) 440px, 92vw" width="{cov[2]}" height="{cov[3]}" alt="Heavy Sun Greatest Hits cover: a blazing orange sun with HEAVY SUN across it.">{NOT_ORIG}</figure>
  <div><p class="kicker">Victoria to Vancouver · 1994 to 2002</p><h1>Heavy Sun</h1><p class="lede">The first band. Started at 19.</p></div>
</div>
<section class="story" aria-labelledby="s1"><h2 id="s1">The story</h2>
<p>Heavy Sun started in Victoria in 1994, with Scott Valentine on vocals, lyrics and guitar. For eight years the band wrote its own songs and recorded them itself.</p>
<p>In 1998 Scott and guitarist Jason Jarvis moved to Vancouver to chase music full time. The search for a new drummer led to Clayton Wolsey, and that led to the next band, The Next T&#8209;Shirt.</p>
<p>Greatest Hits is an unofficial look back at those years: fifteen songs, no official artwork, no official release. Just where it all started.</p>
</section>
<section aria-labelledby="s2"><h2 id="s2">Listen</h2>
{album_block(cov, "Greatest Hits", "Recordings 1994 to 2002 · 15 songs", 3177103140, "Greatest Hits", "fbf3e2", "c8441c", gh_tracks, collapse=None, room=("Heavy Sun","/heavy-sun/"), not_original=True)}
</section>
<section aria-labelledby="s3"><h2 id="s3">The band</h2>
{lineup([("Scott Valentine","Vocals, lyrics, guitars"),("Jason Jarvis","Guitars, piano"),("Mike Boyenga","Bass"),("Steve MacMillan","Drums"),("Clayton Wolsey","Drums")])}
</section>
<section aria-labelledby="s4"><h2 id="s4">More</h2><div class="btns">
{btn(BC+"/album/greatest-hits","Greatest Hits on Bandcamp","bandcamp",hot=True)}
{btn(BC,"Every album on Bandcamp","bandcamp")}
</div></section>'''))

# ---------------- THE NEXT T-SHIRT ----------------
slug = "the-next-t-shirt"
f_nts = [font("Caveat", "caveat", "caveat-latin-700-normal.woff2", 700),
         font("Work Sans", "work-sans", "work-sans-latin-400-normal.woff2", 400),
         font("Work Sans", "work-sans", "work-sans-latin-600-normal.woff2", 600)]
cov_a = cover("nts.jpg", slug, "the-next-t-shirt")
cov_b = cover("fifth.jpg", slug, "the-fifth-floor")
nts_tracks = [("Blame The Day","5:46"),("Who Am I To Say?","1:31"),("Leisure Party","4:16"),("Don't Break My Heart","3:57"),("Graveyard Memories","4:05"),("The Next T-Shirt","5:56"),("Monsters","7:09"),("The New Frontiersmen","8:38")]
ff_tracks = [("The Truce","3:53"),("Put You Away","5:09"),("War Bride","5:09"),("Dead End Love","4:43"),("Valley of the Dolls","3:18")]
rooms.append(dict(
    slug=slug, name_plain="The Next T-Shirt", theme_color="#FFFFFF", fonts=f_nts, icons=["bandcamp"],
    desc="The Next T-Shirt: a Vancouver trio, 2003 to 2005. Two records, the next t-shirt and The Fifth Floor, on Bandcamp.",
    og=og_image("nts.jpg", slug, (255, 255, 255)),
    vars='--bg:#FFFFFF;--ink:#161616;--ink-2:#6A6A6A;--title:#161616;--accent:#A8201A;--on-accent:#fff;--rule:#161616;--line:rgba(0,0,0,.12);--card:#fff;--player-bg:#fff;--spine:#161616;--cover-shadow:0 0 0 1px rgba(0,0,0,.1),0 14px 30px rgba(0,0,0,.12);--title-font:"Caveat",cursive;--label-font:"Work Sans",sans-serif;--body-font:"Work Sans",sans-serif;--page-bg:repeating-linear-gradient(0deg,transparent 0 31px,rgba(70,110,200,.07) 31px 32px),#fff',
    css='h1{font-size:clamp(72px,17vw,150px);font-weight:700;line-height:.8;letter-spacing:-.01em}h1 .the{color:#A8201A;display:block;font-size:.55em;transform:rotate(-4deg);transform-origin:left}h3{font-size:44px;font-weight:700}h3 .the{color:#A8201A}h2::after{height:1px}.btn{border-radius:2px}',
    body=f'''<div class="hero">
  <figure class="cover"><img src="{cov_a[0]}" srcset="{cov_a[1]} 600w, {cov_a[0]} {cov_a[2]}w" sizes="(min-width:760px) 440px, 92vw" width="{cov_a[2]}" height="{cov_a[3]}" alt="the next t-shirt, written by hand in black marker with a red the.">{NOT_ORIG}</figure>
  <div><p class="kicker">Vancouver · 2003 to 2005</p><h1><span class="the">the</span>next t&#8209;shirt</h1><p class="lede">A Vancouver trio. Two records, made before YouTube and all of that.</p></div>
</div>
<section class="story" aria-labelledby="s1"><h2 id="s1">The story</h2>
<p>After Heavy Sun, the search for a drummer turned up Clayton Wolsey. With Keith Trusler on bass, the three of them became the next t&#8209;shirt.</p>
<p>The first record took ten months, made in the drummer's apartment on the Lower East Side of Vancouver. The Fifth Floor came two years later, five songs cut at the Warehouse Studios, and it was the last thing the three of them recorded together.</p>
</section>
<section aria-labelledby="s2"><h2 id="s2">Listen</h2>
{album_block(cov_a, '<span class="the">the</span> next t&#8209;shirt', "2003 · 8 songs", 2606593752, "the next t-shirt", "ffffff", "a8201a", nts_tracks, room=("The Next T-Shirt","/the-next-t-shirt/"), not_original=True, btns=btn(BC+"/album/the-next-t-shirt","the next t-shirt on Bandcamp","bandcamp",hot=True))}
{album_block(cov_b, "The Fifth Floor", "2005 · EP · 5 songs", 2177376273, "The Fifth Floor", "ffffff", "a8201a", ff_tracks, room=("The Next T-Shirt","/the-next-t-shirt/"), btns=btn(BC+"/album/the-fifth-floor","The Fifth Floor on Bandcamp","bandcamp",hot=True))}
</section>
<section aria-labelledby="s3"><h2 id="s3">The band</h2>
{lineup([("Scott Valentine","Vocals, lyrics, guitars"),("Keith Trusler","Bass"),("Clayton Wolsey","Drums, production")])}
</section>
<section aria-labelledby="s4"><h2 id="s4">More</h2><div class="btns">
{btn(BC,"Every album on Bandcamp","bandcamp")}
</div></section>'''))

# ---------------- THE ORIGINALS ----------------
slug = "the-originals"
f_or = [font("Libre Baskerville", "libre-baskerville", "libre-baskerville-latin-400-normal.woff2", 400),
        font("Libre Baskerville", "libre-baskerville", "libre-baskerville-latin-400-italic.woff2", 400, "italic"),
        font("Lora", "lora", "lora-latin-400-normal.woff2", 400),
        font("Lora", "lora", "lora-latin-600-normal.woff2", 600)]
cov_o = cover("seasons08.jpg", slug, "seasons-original-masters")
rem = {s: cover(f"{s}.jpg", slug, f"{s}-2019") for s in ["spring", "summer", "autumn", "winter"]}
om = [("Watch It Grow","4:07"),("Cheerleader","2:48"),("Jukebox","3:53"),("Freak In You","3:29"),("Rewind","3:11"),("Once Upon A Moment","4:31"),("Believe In This","4:43"),("You're A Star","2:19"),("Sweet Freedom","2:55"),
      ("Where Do We Belong?","3:17"),("Big City Welcome","1:15"),("Hang On","4:08"),("21st Century Animal Family Plan","2:32"),("Little Black Book","3:45"),("Cool Kids","2:52"),("This Crazy Behaviour","2:35"),("TV","1:56"),("The Watershed","2:56"),("Insomniac","3:58"),("Satyagraha","3:56"),("The Greatest Message of Hope","1:43"),("Man of Science, Leap of Faith","3:44"),("Home","1:57"),("Beautiful Accident","2:18"),("Don't Break My Heart","4:05"),
      ("Camouflage","4:29"),("Gone","3:02"),("Low Country Road","3:41"),("Dancing On The Rooftops","2:22"),("The Pill","2:54"),("This Ridicule","3:17"),("Everything & Anything","3:26"),("Lonely Killer","3:42"),("Forgotten","3:22"),("Bleeding Heart","4:03"),("A Way Out Of Here","3:36"),("Echoes of Light","3:16"),("Three Words","3:05"),("The Abyss","4:00"),
      ("Ain't That The Truth? (Part 1)","4:05"),("Living in New York","4:17"),("Our Finest Hour","4:34"),("Doves of Hiroshima","2:38"),("Seasons","4:03"),("A Truce","2:52"),("Inside Out","3:51"),("No Worries","2:08"),("Kisses","2:51"),("Warning Bells","2:55"),("Save The World","4:08"),("Green The New Black","4:00"),("Do It For Love","3:55"),("Someone","6:25"),("A Love Song","2:10"),("The Perfect Song","3:41"),("From Here To There","3:13"),("Ain't That The Truth? (Part 2)","4:47")]
groups = [("Spring", om[0:9], "#7DB46C"), ("Summer", om[9:25], "#E9A23B"), ("Autumn", om[25:39], "#D9704E"), ("Winter", om[39:57], "#7F99C9")]
grp_html = "".join(
    f'<details class="season-group" style="--sc:{c}"{" open" if n == "Spring" else ""}><summary><span class="dot"></span>{n}<span class="cnt">{len(t)} songs</span></summary>'
    + '<ol class="tracks" start="' + str(sum(len(g[1]) for g in groups[:k]) + 1) + '" style="counter-reset:t ' + str(sum(len(g[1]) for g in groups[:k])) + '">'
    + "".join(f'<li><span class="t">{html.escape(a)}</span><span class="d">{b}</span></li>' for a, b in t) + '</ol></details>'
    for k, (n, t, c) in enumerate(groups))
circles = "".join(f'<span style="--c:{c}">{l}</span>' for l, c in zip("SEASONS", ["#F2E68A", "#9DCB8A", "#EE9478", "#93A9D4", "#F1B27C", "#B5917A", "#7E7B78"]))
rem_ids = {"spring": (4205500080, 9), "summer": (3679891890, 16), "autumn": (3289881092, 14), "winter": (2102377207, 18)}
rem_html = "".join(
    f'<a class="rem" href="{BC}/album/{s}" target="_blank" rel="me noopener"><img src="{rem[s][1]}" width="600" height="600" alt="Cover of {s.title()} by Scotty Tuesday, the 2019 remaster" loading="lazy"><span class="rem-t">{ico("bandcamp")}{s.title()}<em>{rem_ids[s][1]} songs</em></span></a>'
    for s in ["spring", "summer", "autumn", "winter"])
rooms.append(dict(
    slug=slug, name_plain="The originals", theme_color="#FFFFFF", fonts=f_or, icons=["bandcamp", "spotify", "youtube"],
    desc="The originals: where SEASØNS began. Written and recorded alone in Vancouver, 2006 to 2008, released as a five-disc set with a short film. Remastered in 2019.",
    og=og_image("seasons08.jpg", slug, (255, 255, 255)),
    vars='--bg:#FFFFFF;--ink:#2A2724;--ink-2:#77706A;--title:#2A2724;--accent:#5E7FB8;--on-accent:#fff;--rule:linear-gradient(90deg,#F2E68A,#9DCB8A,#EE9478,#93A9D4,#F1B27C,#B5917A,transparent);--line:rgba(42,39,36,.12);--card:#FAF8F4;--player-bg:#fff;--spine:#2A2724;--cover-shadow:0 0 0 1px rgba(0,0,0,.06),0 16px 36px rgba(0,0,0,.10);--title-font:"Libre Baskerville",serif;--label-font:"Lora",serif;--body-font:"Lora",serif;--page-bg:#fff;--h2-weight:600',
    css='''.circles{display:flex;margin:6px 0 0;flex-wrap:nowrap}.circles span{--d:clamp(42px,11vw,72px);width:var(--d);height:var(--d);border-radius:50%;background:var(--c);opacity:.85;display:grid;place-items:center;font-family:"Libre Baskerville",serif;font-size:calc(var(--d)*.5);color:#1E1C1A;margin-left:calc(var(--d)*-.18);mix-blend-mode:multiply}.circles span:first-child{margin-left:0}
h1.orig{font-size:clamp(44px,9vw,76px);font-weight:400;line-height:1.05;margin-bottom:16px}.circles.small span{--d:30px}.lede{font-style:italic;font-family:"Libre Baskerville",serif}
.season-group{border-top:1px solid var(--line);max-width:640px}.season-group summary{list-style:none;cursor:pointer;min-height:52px;display:flex;align-items:center;gap:12px;font-family:"Libre Baskerville",serif;font-size:20px}.season-group summary::-webkit-details-marker{display:none}.season-group .dot{width:18px;height:18px;border-radius:50%;background:var(--sc);flex:none}.season-group .cnt{margin-left:auto;color:var(--ink-2);font-size:14px;font-family:"Lora",serif}.season-group summary::after{content:"+";color:var(--ink-2);font-size:20px;width:1ch}.season-group[open] summary::after{content:"−"}.season-group .tracks li::before{color:var(--sc)}
.rems{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;max-width:780px}@media (min-width:960px){.rems{grid-template-columns:repeat(4,minmax(0,1fr))}}.rem-t em{white-space:nowrap}
.rem{display:block;text-decoration:none;border:1px solid var(--line);background:#fff;transition:transform .2s,box-shadow .2s}.rem img{display:block;width:100%;height:auto}.rem-t{display:flex;align-items:center;gap:8px;padding:10px 12px;min-height:48px;font-family:"Libre Baskerville",serif}.rem-t .ico{width:16px;height:16px;fill:currentColor}.rem-t em{margin-left:auto;font-style:normal;color:var(--ink-2);font-size:13px;font-family:"Lora",serif}.rem:hover,.rem:focus-visible{transform:translateY(-2px);box-shadow:0 10px 24px rgba(0,0,0,.1)}
.credits{color:var(--ink-2);font-size:15px;max-width:64ch}.seed{background:#FAF8F4;border-left:4px solid #9DCB8A;padding:16px 18px;max-width:64ch}''',
    body=f'''<div class="hero">
  <figure class="cover"><img src="{cov_o[0]}" srcset="{cov_o[1]} 600w, {cov_o[0]} {cov_o[2]}w" sizes="(min-width:760px) 440px, 92vw" width="{cov_o[2]}" height="{cov_o[3]}" alt="The 2008 SEASONS cover: seven overlapping pastel circles, one letter in each."></figure>
  <div><p class="kicker">Vancouver · 2006 to 2008</p><h1 class="orig">The originals</h1><div class="circles small" aria-hidden="true">{circles}</div><p class="lede">Where SEASØNS began.</p></div>
</div>
<section class="story" aria-labelledby="s1"><h2 id="s1">The story</h2>
<p>SEASONS was written, played, produced, recorded, mixed and designed alone in a Vancouver apartment between 2006 and 2008, while falling in love. Fifty-seven songs across one year, in four seasons.</p>
<p>It came out in 2008 as Scott Valentine Presents: five discs, one CD for each season, plus a DVD short film, Seasons: A Film Journey, that told the story with one song from each season.</p>
<p class="seed">With a manager on board came a website and a song a week for a year. Free downloads went out on little cards embedded with seeds, each with a QR code: plant the card, keep the song. Radio stations picked it up, and the walk around Vancouver handing them out became a video.</p>
<p>In 2019 the four seasons were remastered and released as Scotty Tuesday. The five-disc sets are collector's items now. Today BODHI X is singing these songs again: <a href="/seasons/">enter SEASØNS</a>.</p>
</section>
<section aria-labelledby="s2"><h2 id="s2">The original masters</h2>
<div class="album">
  <figure class="cover"><img src="{cov_o[0]}" srcset="{cov_o[1]} 600w, {cov_o[0]} {cov_o[2]}w" sizes="(min-width:760px) 220px, 92vw" width="{cov_o[2]}" height="{cov_o[3]}" alt="Cover of Seasons (Original Masters)" loading="lazy"></figure>
  <div>
    <h3>Seasons</h3>
    <p class="meta">2008 · Original masters · 57 songs</p>
    <div class="btns play-row">{play_button(4245630316, "Seasons (Original Masters)", "The originals", "/the-originals/", cov_o[1])}</div>
    {grp_html}
    <div class="btns" style="margin-top:16px">{btn(BC+"/album/seasons-original-masters","Seasons on Bandcamp","bandcamp",hot=True)}</div>
  </div>
</div>
<p class="credits">Bass by Keith Trusler, who also played lead guitar on Autumn. Mastered by Jamie Sitar at Suite Sound Labs. The Greatest Message of Hope features author Daniel Quinn; Satyagraha samples Mahatma Gandhi. The short film was co-written, co-produced and directed by Lee Baran.</p>
</section>
<section aria-labelledby="s3"><h2 id="s3">The 2019 remasters</h2>
<div class="rems">{rem_html}</div>
</section>
<section aria-labelledby="s4"><h2 id="s4">Listen anywhere</h2><div class="btns">
{btn(SPOTIFY,"Scotty Tuesday on Spotify","spotify",hot=True)}
{btn(YT_ST,"Scotty Tuesday on YouTube","youtube")}
{btn(BC,"Every album on Bandcamp","bandcamp")}
</div></section>'''))

# ---------------- THE MARRIAGE YEARS ----------------
slug = "the-marriage-years"
f_my = [font("Josefin Sans", "josefin-sans", "josefin-sans-latin-300-normal.woff2", 300),
        font("Josefin Sans", "josefin-sans", "josefin-sans-latin-600-normal.woff2", 600),
        font("Lora", "lora", "lora-latin-400-normal.woff2", 400),
        font("Lora", "lora", "lora-latin-600-normal.woff2", 600)]
cov_g = cover("gems.jpg", slug, "unreleased-gems")
gems = [("Dirty Minds","3:09"),("Watch It Grow (earlier version)","4:08"),("Three Words (earlier version)","3:04"),("You're A Star (earlier version)","2:19"),("A Way Out Of Here (earlier version)","4:18"),("The Watershed (earlier version)","3:16"),("Warning Bells (earlier version 2)","2:52"),("Warning Bells (earlier version)","3:12"),("Versailles","2:27"),("This Ridicule","3:11"),("Rewind (earlier version)","3:33"),("The Perfect Song (earlier version)","3:46"),("The Password","2:54"),("Jukebox","3:56"),("Inside Out","3:38"),("Freak In You","3:42"),("Fashion Soldier","0:38"),("Echoes of Light (earlier version)","3:44"),("Cheerleader","2:24"),("Big Plans","3:10"),("Believe In This (earlier version)","5:37"),("Before You Go","2:36"),("Living In New York (earlier version)","4:46"),("Waiting","5:34"),("The Pill (earlier version)","3:31"),("The Perfect Song (earlier version 2)","3:32"),("Locust Queen","5:15"),("Insomniac (earlier version)","2:15"),("Black Gold","3:52"),("Psyche & Cupid (earlier version of Kisses)","4:57"),("Magnetic","5:01"),("In The Moment (earlier version of Once Upon A Moment)","4:11"),("Dancing On The Rooftops (earlier version)","2:41"),("Ain't That The Truth?","5:40"),("13 Days In London","3:25"),("Where The Cool Kids Are (earlier version)","2:48"),("21st Century Animal Family Plan (earlier version)","4:33"),("Engaged","4:19"),("Cheerleader (earlier version)","2:24"),("Someone (earlier version)","6:47"),("Head In The Crowd","1:40"),("The Perfect Song (earlier version)","3:28"),("The Pill (earlier version 2)","3:21"),("This Crazy Behaviour","6:38"),("Warning Bells (earlier version)","2:52"),("Fierce In The Tooth","5:27"),("Just A Sinner","1:42"),("Devil's Decree","1:43")]
rooms.append(dict(
    slug=slug, name_plain="The marriage years", theme_color="#DCEFFA", fonts=f_my, icons=["bandcamp"],
    desc="The marriage years: the songs that kept coming after the music was put away. Unreleased Gems on Bandcamp.",
    og=og_image("gems.jpg", slug, (220, 239, 250)),
    vars='--bg:#F3FAFE;--ink:#1F2A33;--ink-2:#5B6C78;--title:#1F2A33;--accent:#D9602A;--on-accent:#fff;--rule:linear-gradient(90deg,#D9602A,#5BB04B,transparent);--line:rgba(31,42,51,.12);--card:rgba(255,255,255,.75);--player-bg:#fff;--spine:#1F2A33;--cover-shadow:0 18px 40px rgba(30,80,120,.22);--title-font:"Josefin Sans",sans-serif;--label-font:"Josefin Sans",sans-serif;--body-font:"Lora",serif;--page-bg:linear-gradient(180deg,#8CC8EC 0,#CFE8F7 380px,#F3FAFE 760px) no-repeat,#F3FAFE',
    css='h1{font-weight:300;text-transform:uppercase;letter-spacing:.06em;font-size:clamp(44px,10vw,84px);line-height:1}h1 b{font-weight:600;color:#D9602A;display:block;font-size:.42em;letter-spacing:.22em;margin-bottom:10px}h3{font-weight:300;text-transform:uppercase;letter-spacing:.08em}.heart{color:#5BB04B}',
    body=f'''<div class="hero">
  <figure class="cover"><img src="{cov_g[0]}" srcset="{cov_g[1]} 600w, {cov_g[0]} {cov_g[2]}w" sizes="(min-width:760px) 440px, 92vw" width="{cov_g[2]}" height="{cov_g[3]}" alt="Unreleased Gems cover: four photos of Scott Valentine singing and smiling under a blue sky, with the words UNRELEASED GEMS.">{NOT_ORIG}</figure>
  <div><p class="kicker">The songs in the drawer</p><h1><b>Unreleased Gems</b>The marriage years</h1><p class="lede">The songs that kept coming after the music was put away. More to add.</p></div>
</div>
<section class="story" aria-labelledby="s1"><h2 id="s1">The story</h2>
<p>After Black Hat Villain came a move to Vancouver, a job in marketing, and a long stretch with the music packed away. The songs kept coming anyway.</p>
<p>Unreleased Gems gathers forty-eight of them: pre-production demos and songs that were lost, forgotten, cut from earlier records or never funded. Some were made in a studio, some were caught on the spot. Most are solo, with a few friends along the way.</p>
<p>Many are early takes of SEASØNS songs, the same ones BODHI X is singing again now: Watch It Grow, Cheerleader, Jukebox, Freak In You, Rewind, Believe In This. There are more still to add.</p>
</section>
<section aria-labelledby="s2"><h2 id="s2">Listen</h2>
{album_block(cov_g, "Unreleased Gems", "48 songs · and counting", 975750124, "Unreleased Gems", "ffffff", "d9602a", gems, collapse=12, room=("The marriage years","/the-marriage-years/"), not_original=True, btns=btn(BC+"/album/unreleased-gems","Unreleased Gems on Bandcamp","bandcamp",hot=True))}
</section>
<section aria-labelledby="s3"><h2 id="s3">Who played</h2>
{lineup([("Scott Valentine","Vocals, guitars, lyrics, other instruments"),("Clayton Wolsey","Drums, piano, guitar, production on several songs"),("Adam Sutherland","Guitars, bass, keys, production on Dirty Minds")])}
</section>
<section aria-labelledby="s4"><h2 id="s4">More</h2><div class="btns">
{btn(BC,"Every album on Bandcamp","bandcamp")}
</div></section>'''))

for r in rooms:
    copy_fonts(r["fonts"])
    d = os.path.join(ROOT, r["slug"]); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(r))
    print("built", r["slug"])
