"""03_초안의 Slides 원본(deck.json + slides/*.html)을 docs/ 아래 단독 HTML 덱으로 변환.

사용: python3 tools/build_site.py
결과: docs/NN/slides.html, docs/index.html
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "03_초안"
DOCS = ROOT / "docs"

ARROW_SVG = (
    '<svg width="48" height="24" viewBox="0 0 48 24" style="flex:none" aria-hidden="true">'
    '<line x1="2" y1="12" x2="36" y2="12" stroke="#6B7280" stroke-width="3"/>'
    '<path d="M34 4 L46 12 L34 20 Z" fill="#6B7280"/></svg>'
)

TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{fonts}
<style>
html,body{{margin:0;height:100%;background:#0F1626;overflow:hidden;font-family:'Noto Sans KR',sans-serif}}
#stage{{position:fixed;left:0;right:0;top:0;bottom:56px;display:flex;align-items:center;justify-content:center}}
#deck{{width:1920px;height:1080px;position:relative;flex:none;transform-origin:center center;box-shadow:0 8px 40px rgba(0,0,0,.5)}}
#deck>section{{position:absolute;left:0;top:0;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden}}
#deck>section:not(.on){{display:none!important}}
#deck h1,#deck h2,#deck h3,#deck p,#deck ul,#deck ol,#deck table{{margin:0}}
#deck table{{border-collapse:collapse;width:100%}}
#deck th,#deck td{{padding:.35em .6em;border-bottom:1px solid #C9D3E3;text-align:left}}
#deck aside{{display:none}}
#bar{{position:fixed;left:0;right:0;bottom:0;height:56px;display:flex;align-items:center;justify-content:center;gap:12px;color:#C9D3E3;font-size:15px}}
#bar button,#bar a{{background:#1F2A44;color:#F7F5EF;border:1px solid #33415C;border-radius:8px;padding:8px 14px;font:inherit;cursor:pointer;text-decoration:none}}
#bar button:hover,#bar a:hover{{background:#2A3858}}
#notes{{position:fixed;left:16px;right:16px;bottom:64px;max-width:960px;margin:0 auto;background:#F7F5EF;color:#1F2A44;border-radius:12px;padding:16px 20px;font-size:16px;line-height:1.6;box-shadow:0 8px 30px rgba(0,0,0,.4);display:none}}
#notes.show{{display:block}}
</style>
</head>
<body>
<div id="stage"><div id="deck">
{slides}
</div></div>
<div id="notes"></div>
<div id="bar">
<a href="../index.html">목록</a>
<button id="prev" aria-label="이전">◀</button>
<span id="count"></span>
<button id="next" aria-label="다음">▶</button>
<button id="nt">노트</button>
<button id="fs">전체화면</button>
</div>
<script>
const slides=[...document.querySelectorAll('#deck>section')];
const deck=document.getElementById('deck'),notes=document.getElementById('notes');
let i=Math.max(0,Math.min(slides.length-1,(parseInt(location.hash.slice(1))||1)-1));
function fit(){{const s=Math.min(innerWidth/1920,(innerHeight-56)/1080);deck.style.transform='scale('+s+')';}}
function show(n){{i=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,k)=>s.classList.toggle('on',k===i));
document.getElementById('count').textContent=(i+1)+' / '+slides.length;
const a=slides[i].querySelector('aside');notes.textContent=a?a.textContent:'노트 없음';
history.replaceState(null,'','#'+(i+1));}}
document.getElementById('prev').onclick=()=>show(i-1);
document.getElementById('next').onclick=()=>show(i+1);
document.getElementById('nt').onclick=()=>notes.classList.toggle('show');
document.getElementById('fs').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
addEventListener('keydown',e=>{{if(['ArrowRight','PageDown',' '].includes(e.key)){{e.preventDefault();show(i+1)}}
else if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);else if(e.key==='n'||e.key==='N')notes.classList.toggle('show');
else if(e.key==='f'||e.key==='F')document.getElementById('fs').click();}});
let tx=null;addEventListener('touchstart',e=>tx=e.touches[0].clientX,{{passive:true}});
addEventListener('touchend',e=>{{if(tx===null)return;const d=e.changedTouches[0].clientX-tx;if(Math.abs(d)>40)show(d<0?i+1:i-1);tx=null}});
addEventListener('resize',fit);fit();show(i);
</script>
</body>
</html>
"""

INDEX = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>확률과 통계 강의자료</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@500;700&family=Noto+Sans+KR:wght@400;700&display=swap">
<style>
body{{margin:0;background:#F7F5EF;color:#1F2A44;font-family:'Noto Sans KR',sans-serif;line-height:1.6}}
main{{max-width:880px;margin:0 auto;padding:48px 16px}}
h1{{font-family:'IBM Plex Sans KR',sans-serif;font-size:36px;margin:0 0 8px}}
.sub{{color:#4A5568;margin:0 0 32px}}
.card{{background:#FDFCF9;border:2px solid #C9D3E3;border-radius:16px;padding:24px;margin-bottom:20px}}
.card h2{{font-size:22px;margin:0 0 4px}}
.card p{{margin:0 0 16px;color:#4A5568}}
.links{{display:flex;flex-wrap:wrap;gap:10px}}
.links a{{background:#2F6DB5;color:#FDFCF9;text-decoration:none;border-radius:10px;padding:10px 16px;font-weight:700}}
.links a.q{{background:#B4531A}}
.links a.p{{background:#1F2A44}}
footer{{color:#6B7280;font-size:14px;margin-top:40px}}
</style>
</head>
<body>
<main>
<h1>확률과 통계 강의자료</h1>
<p class="sub">대학교 1학년 공대생 대상 · 동아출판 「확률과 통계」 Ⅲ단원 「통계」 기준</p>
{cards}
<footer>슬라이드: 방향키·스와이프로 이동, N 키로 발표자 노트, F 키로 전체화면</footer>
</main>
</body>
</html>
"""


def build_deck(folder: Path) -> dict:
    proj = folder / "project"
    deck = json.loads((proj / "deck.json").read_text(encoding="utf-8"))
    parts = []
    for sid in deck["order"]:
        f = proj / "slides" / f"{sid}.html"
        if not f.exists():
            continue
        s = f.read_text(encoding="utf-8")
        s = re.sub(r"<x-connector[^>]*>\s*</x-connector>", ARROW_SVG, s)
        parts.append(s.strip())
    fonts = "\n".join(
        f'<link rel="stylesheet" href="{html.escape(face["href"])}">'
        for face in deck.get("faces", {}).values()
        if face.get("href")
    )
    num = folder.name[:2]
    out = DOCS / num
    out.mkdir(parents=True, exist_ok=True)
    (out / "slides.html").write_text(
        TEMPLATE.format(title=html.escape(deck["title"]), fonts=fonts, slides="\n".join(parts)),
        encoding="utf-8",
    )
    return {"num": num, "title": deck["title"], "count": len(parts)}


def main():
    decks = [build_deck(d) for d in sorted(SRC.glob("[0-9][0-9]차시")) if (d / "project" / "deck.json").exists()]
    cards = []
    for d in decks:
        links = [f'<a href="{d["num"]}/slides.html">슬라이드 ({d["count"]}장)</a>']
        if (DOCS / d["num"] / "quiz.html").exists():
            links.append(f'<a class="q" href="{d["num"]}/quiz.html">웹 퀴즈</a>')
        if (DOCS / d["num"] / "playground.html").exists():
            links.append(f'<a class="p" href="{d["num"]}/playground.html">애니메이션 플레이그라운드</a>')
        cards.append(
            f'<div class="card"><h2>{html.escape(d["title"])}</h2>'
            f'<p>{int(d["num"])}차시</p><div class="links">{"".join(links)}</div></div>'
        )
    (DOCS / "index.html").write_text(INDEX.format(cards="\n".join(cards)), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    for d in decks:
        print(f'{d["num"]}: {d["title"]} ({d["count"]}장)')


if __name__ == "__main__":
    main()
