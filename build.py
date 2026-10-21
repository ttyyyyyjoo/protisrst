#!/usr/bin/env python3
"""Generátor webu protisrst.cz.

Zdroj dat: src/entries.json (pořadí v souboru = pořadí na webu).
Spuštění: python3 build.py  → vygeneruje index.html, vyrok/NNN/index.html,
proti-proudu/index.html, sitemap.xml, robots.txt, 404.html a preview.html
(náhled do jednoho souboru bez externího CSS).
"""
import html, json, os, re, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://protisrst.cz"
TODAY = datetime.date.today()

E = json.load(open(os.path.join(ROOT, "src/entries.json"), encoding="utf8"))
CSS = open(os.path.join(ROOT, "src/style.css"), encoding="utf8").read()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@500;600;700'
         '&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap">')

esc = lambda s: html.escape(s, quote=True)
num = lambda e: e["id"].split("/")[-1]
path_of = lambda e: f"/vyrok/{num(e)}/"
anchor = lambda e: e["id"].replace("/", "-")
def plain(s): return re.sub(r"<[^>]+>", " ", s).replace("  ", " ").strip()


def head(title, desc, path, og_type="website", ld=None, inline=False):
    url = SITE + path
    style = f"<style>\n{CSS}</style>" if inline else '<link rel="stylesheet" href="/style.css">'
    lds = "".join(f'\n<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    return f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Proti srsti">
<meta property="og:locale" content="cs_CZ">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{FONTS}
{style}{lds}
</head>
<body>
"""


def masthead(home=True):
    h1 = '<h1>Proti srsti</h1>' if home else '<p class="h1"><a href="/">Proti srsti</a></p>'
    return f"""  <header>
    <div class="office">Úřad pro evidenci výroků proti srsti · odbor koncepcí</div>
    {h1}"""


def card(e, h="h2", link=True):
    cj = f'<a href="{path_of(e)}">{e["id"]}</a>' if link else e["id"]
    src = (f'<a href="{esc(e["url"])}" rel="noopener" target="_blank">{esc(e["src"])}</a>' if e.get("url")
           else esc(e["src"]))
    if e.get("src2"):
        src += f'<br><a href="{esc(e["url2"])}" rel="noopener" target="_blank">{esc(e["src2"])}</a>'
    return f"""    <article class="card" id="{anchor(e)}" data-area="{esc(e['area'])}">
      <div class="head"><span>Č. j. <b>{cj}</b></span><span>Oblast: <b>{esc(e['area'])}</b></span><span>Datum: <b>{esc(e['date'])}</b></span></div>
      <div class="namerow"><{h} class="who">{esc(e['person'])}<small>{esc(e['role'])}</small></{h}><div class="stamp" aria-hidden="true">{e['stamp']}</div></div>
      <blockquote>{esc(e['quote'])}</blockquote>
      <dl>
        <dt>Kontext</dt><dd>{esc(e['context'])}</dd>
        <dt>Vyjádření úřadu</dt><dd class="office-note">{esc(e['office'])}</dd>
        <dt>Zdroj</dt><dd>{src}</dd>
      </dl>
    </article>"""


FOOTER = """  <footer>
    <p><b>Poučení:</b> Jde o satirický projekt. Výroky v uvozovkách jsou doslovné citace převzaté z uvedených zdrojů. Text v řádcích „Kontext“ a „Vyjádření úřadu“ je náš vlastní a nepředstavuje citaci. Úřad pro evidenci výroků proti srsti neexistuje, což ho odlišuje od některých jiných úřadů jen částečně.</p>
    <p>Jazyková příloha: <a href="/proti-proudu/">Proti proudu, nebo proti srsti?</a></p>
    <p>Našli jste chybu v citaci nebo zdroji? Opravíme ji.</p>
  </footer>
</div>
"""

FILTER_JS = """<script>
(function(){
  var cards=[].slice.call(document.querySelectorAll('.card')),nav=document.getElementById('filters');
  var areas=['Vše'];cards.forEach(function(c){var a=c.getAttribute('data-area');if(areas.indexOf(a)<0)areas.push(a)});
  areas.forEach(function(a){var b=document.createElement('button');b.type='button';b.textContent=a;b.setAttribute('aria-pressed',a==='Vše');
    b.onclick=function(){nav.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});
      cards.forEach(function(c){c.hidden=!(a==='Vše'||c.getAttribute('data-area')===a)})};nav.appendChild(b)});
})();
</script>
"""


def index(inline=False):
    desc = ("Úřední evidence výroků a kroků vládní koalice ANO, SPD a Motoristů, které jdou proti srsti odborným "
            "koncepcím. Satirický projekt, citace doslovně a se zdrojem.")
    title = "Proti srsti" if inline else "Proti srsti | Úřední evidence výroků vládní koalice"
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "Proti srsti", "url": SITE + "/",
           "inLanguage": "cs", "description": desc}]
    out = head(title, desc, "/", ld=ld, inline=inline)
    if inline:
        out = out.replace('<meta name="viewport"', '<meta name="claude:viewport-fit-sides" content="cover">\n<meta name="viewport"')
    out += '<div class="wrap">\n' + masthead() + f"""
    <p class="lede">Úřední evidence výroků a kroků vládní koalice, které jdou proti srsti odborným koncepcím, vědeckému konsenzu a dokumentům, na nichž se dřív shodly stovky lidí. Citace jsou doslovné, každá se zdrojem. Komentáře úřadu jsou satira.</p>
    <p class="defn"><b>proti srsti</b> <i>přísl. spojení</i> — směr, kterým se hladí, nikoli chodí. Chodí se proti proudu. Viz <a href="#PS-2026-008">PS/2026/008</a>, <a href="#PS-2026-014">PS/2026/014</a> a <a href="/proti-proudu/">jazykovou přílohu</a>.</p>
    <div class="meta"><span>Spisová značka: PS/2026</span><span>Evidováno záznamů: {len(E)}</span><span>Poslední zápis: {TODAY.day}. {TODAY.month}. {TODAY.year}</span></div>
  </header>

  <nav class="filters" aria-label="Filtr podle oblasti" id="filters"><span>Oblast</span></nav>

  <main class="list" id="list">
""" + "\n".join(card(e) for e in E) + "\n  </main>\n\n" + FOOTER + FILTER_JS + "</body>\n</html>\n"
    return out


def entry_page(i, e):
    q = e["quote"]
    title = f"„{q[:70]}{'…' if len(q) > 70 else ''}“ – {e['person']} | Proti srsti"
    desc = f"{e['person']} ({e['date']}): „{q}“ Kontext, zdroj a vyjádření úřadu. Č. j. {e['id']}."
    ld = [{"@context": "https://schema.org", "@type": "Quotation", "text": q, "inLanguage": "cs",
           "spokenByCharacter": {"@type": "Person", "name": e["person"]},
           "url": SITE + path_of(e), **({"isBasedOn": e["url"]} if e.get("url") else {})}]
    prev_e, next_e = (E[i - 1] if i > 0 else None), (E[i + 1] if i + 1 < len(E) else None)
    nav = '  <nav class="pager">'
    nav += f'<a href="{path_of(prev_e)}">← {prev_e["id"]}</a>' if prev_e else '<span></span>'
    nav += '<a href="/">Celá evidence</a>'
    nav += f'<a href="{path_of(next_e)}">{next_e["id"]} →</a>' if next_e else '<span></span>'
    nav += '</nav>\n'
    return (head(title, desc, path_of(e), og_type="article", ld=ld) + '<div class="wrap">\n' + masthead(False)
            + "\n  </header>\n  <main class=\"list\">\n" + card(e, h="h1", link=False) + "\n  </main>\n" + nav
            + FOOTER + "</body>\n</html>\n")


PROTI_PROUDU = """  <main class="article">
    <h1>Proti proudu, nebo proti srsti?</h1>
    <p class="lede">Výklad úřadu k dvěma ustáleným spojením, která se v roce 2026 začala v politice zaměňovat. Vydáno pro potřeby voličů, kandidátů a grafiků billboardů.</p>

    <section>
      <h2>Jít proti proudu</h2>
      <p>Znamená jednat jinak než většina, vzdorovat převládajícímu směru, nenechat se unášet. Obraz pochází z vody: ryba nebo plavec, který místo pohodlného splutí s proudem plave opačným směrem a vynakládá na to úsilí.</p>
      <p class="ex">Příklad správného užití: <i>Šel proti proudu a koncepci, na které se shodly stovky odborníků, nezrušil.</i></p>
    </section>

    <section>
      <h2>Proti srsti</h2>
      <p>Užívá se ve dvou podobách. Je-li něco <b>komu proti srsti</b>, je mu to nepříjemné a odporuje to jeho povaze. <b>Hladit někoho proti srsti</b> znamená dráždit ho. Obraz pochází ze zvířecí srsti, která se při hlazení opačným směrem čepýří a zvíře se ohradí.</p>
      <p class="ex">Příklad správného užití: <i>„Upřímně řečeno, dotace všeho druhu jsou mi proti srsti.“</i> Ministr kultury Oto Klempíř, 21. 10. 2026. Jazykově bezvadné, viz <a href="/vyrok/014/">PS/2026/014</a>. Věcnou stránku výroku úřad hodnotí odděleně.</p>
    </section>

    <section>
      <h2>Jít proti srsti</h2>
      <p>Spojení vzniklé sloučením obou předchozích. Jazykověda takový jev nazývá kontaminací. Srst nemá směr, kterým by se dalo jít. Kdo se o to přesto pokusí, nedosáhne ničeho kromě zcuchaného kožichu.</p>
      <p class="ex">Doložený výskyt: billboard Motoristů sobě <i>„Odvaha jít proti srsti“</i>, srpen 2026, viz <a href="/vyrok/008/">PS/2026/008</a>.</p>
    </section>

    <section class="ruling">
      <h2>Rozhodnutí úřadu</h2>
      <ol>
        <li>Proti proudu se chodí.</li>
        <li>Proti srsti se hladí.</li>
        <li>Kdo jde proti srsti, zcuchá kožich. Obvykle cizí.</li>
      </ol>
    </section>

    <p class="note">Tato stránka nesouvisí s webem Protiproud.cz ani s žádným jiným projektem podobného jména. Úřad pro evidenci výroků proti srsti je satirický projekt.</p>
  </main>
"""


def proti_proudu():
    title = "Proti proudu, nebo proti srsti? Význam a správné užití | Proti srsti"
    desc = ("Jít proti proudu, nebo proti srsti? Úřední výklad obou spojení, jejich významu a správného užití, "
            "s doloženými příklady z české politiky roku 2026.")
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": "Proti proudu, nebo proti srsti?",
           "inLanguage": "cs", "datePublished": "2026-10-21", "dateModified": TODAY.isoformat(),
           "author": {"@type": "Organization", "name": "Proti srsti"}, "url": SITE + "/proti-proudu/"}]
    return (head(title, desc, "/proti-proudu/", og_type="article", ld=ld) + '<div class="wrap">\n' + masthead(False)
            + "\n  </header>\n" + PROTI_PROUDU + FOOTER + "</body>\n</html>\n")


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf8").write(text)


write("index.html", index())
full = index(inline=True)
preview = full.split("<head>\n", 1)[1].split("</head>")[0] + full.split("<body>\n", 1)[1].rsplit("</body>", 1)[0]
open(os.path.join(ROOT, "..", "protisrst", "index.html"), "w", encoding="utf8").write(preview)  # náhled mimo web
for i, e in enumerate(E):
    write(f"vyrok/{num(e)}/index.html", entry_page(i, e))
write("proti-proudu/index.html", proti_proudu())
write("style.css", CSS)
write("404.html", head("Nenalezeno | Proti srsti", "Záznam nenalezen.", "/404.html") + '<div class="wrap">\n'
      + masthead(False) + '\n  </header>\n  <main class="article"><h1>Záznam nenalezen</h1><p>Spis byl pravděpodobně '
      'odideologizován. <a href="/">Zpět do evidence</a>.</p></main>\n' + FOOTER + "</body>\n</html>\n")
urls = ["/", "/proti-proudu/"] + [path_of(e) for e in E]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print(f"OK: {len(E)} záznamů, {len(urls)} URL v sitemap")
