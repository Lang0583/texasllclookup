"""Static site generator: Texas business lookup MVP. Usage: python3 build.py <csv> <outdir>"""
import sys, os, json, re, html, pandas as pd
CSV, OUT = sys.argv[1], sys.argv[2]
SITE = "https://texasllclookup.com"
NAME = "Texas LLC Lookup"
OPERATOR = "Matt Langston, 1530 Sun City Blvd, Ste 120 PMB 482, Georgetown, TX 78633"
CONTACT = "m.a.langston@agentmail.to"
ORG = {"CL":"LLC","CT":"Corporation","CN":"Nonprofit corporation","CI":"Foreign corporation","CF":"Foreign LLC","PL":"Limited partnership"}
RTB = {"A":"Active","N":"Not active (forfeited)","U":"Not established","D":"Inactive"}
NAICS2 = {"11":"Agriculture","21":"Mining and oil and gas","22":"Utilities","23":"Construction","31":"Manufacturing","32":"Manufacturing","33":"Manufacturing","42":"Wholesale","44":"Retail","45":"Retail","48":"Transportation","49":"Transportation","51":"Information","52":"Finance and insurance","53":"Real estate","54":"Professional services","55":"Management","56":"Admin and support","61":"Education","62":"Health care","71":"Arts and recreation","72":"Food and lodging","81":"Other services","92":"Public administration"}
SRC = '<p class="src">Sources: <a href="https://data.texas.gov/dataset/Active-Franchise-Taxpayers/9cir-efmm">Texas Comptroller Active Franchise Taxpayers (data.texas.gov)</a>; <a href="https://comptroller.texas.gov/taxes/franchise/">Texas Comptroller franchise tax</a>; <a href="https://www.sos.texas.gov/corp/index.shtml">Texas Secretary of State business filings</a>; <a href="https://www.sos.texas.gov/corp/forms/205_boc.pdf">Form 205 (filing fee $300)</a>.</p>'
slug = lambda s: re.sub(r'[^a-z0-9]+','-',str(s).lower()).strip('-')
e = html.escape
d = pd.read_csv(CSV, dtype=str).fillna("")
d.columns = [c.strip() for c in d.columns]
d = d.apply(lambda c: c.str.strip())
d["city"] = d["Taxpayer City"].str.title(); d["type"] = d["Taxpayer Organizational Type"].map(ORG).fillna("Other entity")
d["status"] = d["Right to Transact Business Code"].map(RTB).fillna("Unknown")
d["ind"] = d["NAICS Code"].str[:2].map(NAICS2).fillna("")
d["year"] = d["SOS Charter Date"].str[-4:]
TX = d[d["Taxpayer State"]=="TX"]
pages = []
def ld(o): return f'<script type="application/ld+json">{json.dumps(o)}</script>'
def crumbs(items): return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(n,u) in enumerate(items)]}
def faq(qas): return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qas]}
def faqhtml(qas): return "<h2>Questions</h2>"+"".join(f"<details open><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q,a in qas)
GHL_FORM = '''<iframe src="https://api.leadconnectorhq.com/widget/form/elTzcFu7m8XWNT0webYC" style="width:100%;height:434px;border:none;border-radius:8px" id="inline-elTzcFu7m8XWNT0webYC" data-layout="{'id':'INLINE'}" data-trigger-type="alwaysShow" data-trigger-value="" data-activation-type="alwaysActivated" data-activation-value="" data-deactivation-type="neverDeactivate" data-deactivation-value="" data-form-name="Texas LLC Lookup Signup" data-height="434" data-layout-iframe-id="inline-elTzcFu7m8XWNT0webYC" data-form-id="elTzcFu7m8XWNT0webYC" title="Texas LLC Lookup Signup" loading="lazy"></iframe>
<script src="https://link.msgsndr.com/js/form_embed.js" defer></script>'''
def optin(kind="checklist", city=""):
    return '<section class="optin"><h3>Free Texas LLC starter checklist</h3><p>Name check, filing, EIN, franchise tax, and registered agent steps in one page.</p>'+GHL_FORM+'</section>'
CTA = '''<aside class="cta"><h3>Starting a Texas LLC?</h3><p>Check the name first, then file a Certificate of Formation (Form 205) with the Texas SOS. The Texas SOS filing fee is $300 (per the Form 205 instructions).</p>
<!-- TODO affiliate slot: primary formation partner (Northwest Registered Agent, pending approval) --><a class="btn" href="#TODO-affiliate-formation" rel="sponsored nofollow">Start your LLC (partner link TODO)</a>
<!-- TODO affiliate slot: registered agent partner --><a class="btn2" href="#TODO-affiliate-registered-agent" rel="sponsored nofollow">Get a registered agent (TODO)</a>
<p class="disc">We may earn a commission from partner links. That does not change the price you pay.</p></aside>'''
NOTICE = '<p class="notice"><strong>Not a government agency.</strong> This is an independent reference built from public Texas Comptroller data. For official records and certificates, use the <a href="https://comptroller.texas.gov/taxes/franchise/account-status/search">Comptroller Taxable Entity Search</a> or <a href="https://www.sos.texas.gov/corp/sosda/index.shtml">Texas SOS</a>.</p>'
CSS = "body{font:16px/1.55 system-ui,sans-serif;max-width:960px;margin:auto;padding:0 16px;color:#1b1b1b}header,footer{padding:12px 0;border-bottom:1px solid #ddd}footer{border-top:1px solid #ddd;border-bottom:0;font-size:14px}a{color:#0b5cad}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #eee;padding:6px;text-align:left}.notice{background:#fff7e0;padding:10px;border-left:4px solid #e0a800}.cta,.optin{background:#eef5ff;padding:14px;margin:18px 0;border-radius:8px}.btn,.btn2,button{display:inline-block;background:#0b5cad;color:#fff;padding:8px 14px;border-radius:6px;border:0;margin:4px 4px 4px 0;text-decoration:none}.btn2{background:#444}.answer{font-size:18px;background:#f4f4f4;padding:12px}.src,.disc{font-size:13px;color:#555}input[type=email],#q{padding:8px;width:60%}"
def page(path, title, desc, body, schema=(), noindex=False, crumbitems=None, city_attr=""):
    url = SITE+path
    s = "".join(ld(x) for x in schema) + (ld(crumbs(crumbitems)) if crumbitems else "")
    bc = " &rsaquo; ".join(f'<a href="{u}">{e(n)}</a>' for n,u in crumbitems) if crumbitems else ""
    h = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website">
<style>{CSS}</style>{s}</head><body data-city="{e(city_attr)}"><header><a href="/"><strong>{NAME}</strong></a> &middot; <a href="/search/">Search</a> &middot; <a href="/cities/">Cities</a> &middot; <a href="/counties/">Counties</a> &middot; <a href="/start-an-llc/">Start an LLC</a></header>
<nav aria-label="breadcrumb">{bc}</nav><main>{body}</main>{NOTICE}<footer><a href="/privacy/">Privacy</a> &middot; <a href="/about/">About and data sources</a> &middot; <a href="/remove/">Request removal</a> &middot; Data from Texas Comptroller open data.<br>Operated by {OPERATOR} &middot; <a href="mailto:{CONTACT}">{CONTACT}</a></footer></body></html>'''
    fp = os.path.join(OUT, path.strip("/"), "index.html"); os.makedirs(os.path.dirname(fp), exist_ok=True); open(fp,"w").write(h)
    if not noindex: pages.append(path)
ORGLD = {"@context":"https://schema.org","@type":"Organization","name":NAME,"url":SITE,"description":"Independent Texas business lookup built on public Comptroller data. Not a government agency."}
DSLD = {"@context":"https://schema.org","@type":"Dataset","name":"Texas active franchise taxpayers (derived)","description":"Texas business entities registered for franchise tax, derived from Texas Comptroller open data.","license":"https://data.texas.gov/","isBasedOn":"https://data.texas.gov/dataset/Active-Franchise-Taxpayers/9cir-efmm","creator":{"@type":"GovernmentOrganization","name":"Texas Comptroller of Public Accounts"},"spatialCoverage":"Texas, US"}
cities = TX["city"].value_counts(); topc = cities[cities>=300].index[:60]
n, nllc, nact = len(d), (d["type"]=="LLC").sum(), (d["status"]=="Active").sum()
HOMEQA = [("How do I look up a Texas LLC for free?","Search the Texas Comptroller Taxable Entity Search, which is free and shows right to transact business status, or use our search built on the same public data. The Texas SOS search costs $1.00 per search."),
("What does 'right to transact business' mean?","It is the Comptroller's franchise tax status. Active means the entity is current; forfeited means it lost the right to do business in Texas, usually for unfiled franchise tax reports."),
("How much does it cost to form an LLC in Texas?","The Texas SOS filing fee for a Certificate of Formation (Form 205) for an LLC is $300."),
("Is this site the government?","No. It is an independent reference built from Texas Comptroller open data, with links to official sources.")]
page("/", "Texas Business Search: Free LLC and Corporation Lookup", "Free Texas business entity lookup. Check LLC and corporation status, charter date, and right to transact business, with links to official records.",
 f'''<h1>Free Texas business search</h1><p class="answer">Look up any Texas LLC, corporation, or partnership registered for franchise tax. Free, no account. This index covers {n:,} entities, {nllc:,} of them LLCs, and {nact:,} with an active right to transact business.</p>
<form action="/search/"><input id="q" name="q" placeholder="Business name, e.g. Lone Star"><button>Search</button></form>
<h2>Browse by city</h2><p>{" &middot; ".join(f'<a href="/tx/{slug(c)}/">{e(c)}</a>' for c in topc[:24])} &middot; <a href="/cities/">All cities</a></p>
{optin()}{CTA}<h2>How Texas business records work</h2><p>Texas entities file with the Secretary of State (formation documents) and register with the Comptroller (franchise tax). The Comptroller publishes active franchise taxpayers as open data, which is what this site uses.</p>{faqhtml(HOMEQA)}{SRC}''',
 [ORGLD, DSLD, faq(HOMEQA)], crumbitems=[("Home","/")])
# search index (compact) + UI
TX = TX.assign(_d=pd.to_datetime(TX["SOS Charter Date"], errors="coerce"))
idx = TX.sort_values("_d", ascending=False)[["Taxpayer Name","city","type","status","Taxpayer Number"]].head(100000).values.tolist()
os.makedirs(OUT+"/search", exist_ok=True); json.dump(idx, open(OUT+"/search/index.json","w"), separators=(",",":"))
page("/search/", "Search Texas Businesses by Name", "Search Texas LLCs and corporations by name, city, and status.",
 '''<h1>Search Texas businesses</h1><input id="q" placeholder="Type at least 3 letters" autofocus><p id="n"></p><table id="r"></table>
<p class="src">Covers the 100,000 most recently chartered Texas-addressed entities. For any other entity, use the free <a href=\'https://comptroller.texas.gov/taxes/franchise/account-status/search\'>Comptroller Taxable Entity Search</a>.</p>
<script>let D=[];fetch('/search/index.json').then(r=>r.json()).then(j=>{D=j;let q=new URLSearchParams(location.search).get('q');if(q){qi.value=q;go()}});const qi=document.getElementById('q');
function go(){let q=qi.value.toUpperCase();if(q.length<3)return;let m=D.filter(x=>x[0].includes(q)).slice(0,100);document.getElementById('n').textContent=m.length+' shown';
document.getElementById('r').innerHTML='<tr><th>Name</th><th>City</th><th>Type</th><th>Status</th></tr>'+m.map(x=>`<tr><td>${x[4]?`<a href="/b/${x[4]}/">${x[0]}</a>`:x[0]}</td><td>${x[1]}</td><td>${x[2]}</td><td>${x[3]}</td></tr>`).join('')}qi.oninput=go;</script>''', crumbitems=[("Home","/"),("Search","/search/")])
page("/cities/", "Texas Businesses by City", "Browse registered Texas businesses by city.", "<h1>Texas businesses by city</h1><ul>"+"".join(f'<li><a href="/tx/{slug(c)}/">{e(c)}</a> ({cities[c]:,})</li>' for c in topc)+"</ul>"+SRC, crumbitems=[("Home","/"),("Cities","/cities/")])
SAMPLE_BIZ = set()
# ---- long-tail precompute ----
INDEX_BATCH = 5000      # indexable business pages (newest by charter date); raise later
BIZ_TOTAL = 25000       # total business pages generated (rest noindex)
MIN_ROWS = 10           # never publish a list page with fewer entries
LIST_N = 100            # rows shown per list page
import datetime as _dt
TODAY = pd.Timestamp(_dt.date.today())
TX = TX.assign(_d=TX["_d"].where(TX["_d"]<=TODAY))
DMAX = TX["_d"].max(); D30 = DMAX - pd.Timedelta(days=30)
CN0 = {}
_cf0 = os.path.join(os.path.dirname(os.path.abspath(__file__)),"tx_counties.txt")
if not os.path.exists(_cf0): _cf0 = os.path.join(os.path.dirname(CSV),"tx_counties.txt")
for line in open(_cf0).read().splitlines()[1:]:
    p_=line.split("|"); CN0[str((int(p_[2])+1)//2)] = p_[4]
TX["county"] = TX["Taxpayer County Code"].str.lstrip("0").map(CN0).fillna("")
TYPES = ["LLC","Corporation","Nonprofit corporation","Foreign corporation","Foreign LLC","Limited partnership"]
TSLUG = {"LLC":"llcs","Corporation":"corporations","Nonprofit corporation":"nonprofits","Foreign corporation":"foreign-corporations","Foreign LLC":"foreign-llcs","Limited partnership":"limited-partnerships"}
TPLUR = {"LLC":"LLCs","Corporation":"Corporations","Nonprofit corporation":"Nonprofit Corporations","Foreign corporation":"Foreign Corporations","Foreign LLC":"Foreign LLCs","Limited partnership":"Limited Partnerships"}
LT = {}
_kc = TX[TX["county"]!=""]["county"].value_counts(); KHUB = set(_kc[_kc>=500].index)
LTJOBS = []
LISTED = set()
for c in topc:
    g = TX[TX["city"]==c]; cs = slug(c); LT[c] = []
    for t in TYPES:
        gt = g[g["type"]==t]
        if len(gt) >= MIN_ROWS:
            u=f"/tx/{cs}/{TSLUG[t]}/"; LT[c].append((f"{TPLUR[t]} in {c}",u)); LTJOBS.append(("type",c,t,u,gt))
    gn = g[g["_d"]>=D30]
    if len(gn) >= MIN_ROWS:
        u=f"/tx/{cs}/new/"; LT[c].append((f"New businesses in {c} (last 30 days)",u)); LTJOBS.append(("new",c,None,u,gn))
    for ind_,gi in g[g["ind"]!=""].groupby("ind"):
        if len(gi) >= MIN_ROWS:
            u=f"/tx/{cs}/industry/{slug(ind_)}/"; LT[c].append((f"{ind_} businesses in {c}",u)); LTJOBS.append(("ind",c,ind_,u,gi))
LTH={c:"".join(f'<li><a href="{u}">{e(l)}</a></li>' for l,u in v) for c,v in LT.items()}
KLH=lambda tc:"".join(f'<li><a href="{u}">{e(l)}</a></li>' for c2 in tc.index if c2 in LT for l,u in LT[c2][:4])
for j in LTJOBS: LISTED.update(j[4].sort_values("_d",ascending=False).head(LIST_N)["Taxpayer Number"])
for c in topc:
    g = TX[TX["city"]==c]; cs = slug(c)
    ty = g["type"].value_counts().head(6); ind = g[g["ind"]!=""]["ind"].value_counts().head(8)
    yr = g["year"].value_counts().sort_index().tail(6); recent = g.sort_values("SOS Charter Date", key=lambda s: pd.to_datetime(s, errors="coerce"), ascending=False).head(25)
    share = (g["status"]=="Active").mean()*100
    SAMPLE_BIZ.update(recent["Taxpayer Number"])
    qa = [(f"How many businesses are registered in {c}, TX?", f"This index lists {len(g):,} franchise tax entities with a {c} address, of which {share:.0f}% have an active right to transact business ."),
          (f"How do I start an LLC in {c}?", "File a Certificate of Formation (Form 205) with the Texas Secretary of State ($300 fee), get an EIN from the IRS, and register for franchise tax with the Comptroller."),
          (f"How do I check if a {c} business is in good standing?", "Use the Comptroller Taxable Entity Search for right to transact status, or order a certificate of fact from the Texas SOS.")]
    body = f'''<h1>{e(c)}, Texas business directory</h1><p class="answer">{len(g):,} registered entities with a {e(c)} address; {share:.0f}% active. Most common type: {e(ty.index[0])}.</p>
<h2>Entity types</h2><table>{"".join(f"<tr><td>{e(k)}</td><td>{v:,}</td></tr>" for k,v in ty.items())}</table>
{"<h2>Top industries (where NAICS reported)</h2><table>"+"".join(f"<tr><td>{e(k)}</td><td>{v:,}</td></tr>" for k,v in ind.items())+"</table>" if len(ind) else ""}
<h2>Formations by charter year (recent)</h2><table>{"".join(f"<tr><td>{k}</td><td>{v:,}</td></tr>" for k,v in yr.items())}</table>
{optin("alerts", c)}<h2>Recently chartered in {e(c)}</h2><table><tr><th>Name</th><th>Type</th><th>Chartered</th></tr>{"".join(f'<tr><td><a href="/b/{r["Taxpayer Number"]}/">{e(r["Taxpayer Name"])}</a></td><td>{e(r["type"])}</td><td>{r["SOS Charter Date"]}</td></tr>' for _,r in recent.iterrows())}</table>
<h2>Browse {e(c)} businesses</h2><ul>{LTH[c]}</ul>
{CTA}{faqhtml(qa)}<p>Nearby: {" &middot; ".join(f'<a href="/tx/{slug(x)}/">{e(x)}</a>' for x in topc[:10] if x!=c)}</p>{SRC}'''
    page(f"/tx/{cs}/", f"{c}, TX Business Search and New Businesses", f"{len(g):,} registered businesses in {c}, Texas: types, industries, and recent formations from Comptroller data.", body,
         [faq(qa), {"@context":"https://schema.org","@type":"Dataset","name":f"Registered businesses in {c}, TX","isBasedOn":DSLD["isBasedOn"],"spatialCoverage":f"{c}, Texas"}], crumbitems=[("Home","/"),("Cities","/cities/"),(c,f"/tx/{cs}/")], city_attr=c)

CN = {}
_cf = os.path.join(os.path.dirname(os.path.abspath(__file__)),"tx_counties.txt")
if not os.path.exists(_cf): _cf = os.path.join(os.path.dirname(CSV),"tx_counties.txt")
for line in open(_cf).read().splitlines()[1:]:
    p=line.split("|"); CN[str((int(p[2])+1)//2)] = p[4]
TX["county"] = TX["Taxpayer County Code"].str.lstrip("0").map(CN).fillna("")
cc = TX[TX["county"]!=""]["county"].value_counts(); topk = cc[cc>=500].index
page("/counties/", "Texas Businesses by County", "Browse registered Texas businesses by county.", "<h1>Texas businesses by county</h1><ul>"+"".join(f'<li><a href="/county/{slug(k)}/">{e(k)}</a> ({cc[k]:,})</li>' for k in topk)+"</ul>"+SRC, crumbitems=[("Home","/"),("Counties","/counties/")])
for k in topk:
    g = TX[TX["county"]==k]; ks=slug(k); share=(g["status"]=="Active").mean()*100
    ty = g["type"].value_counts().head(6); tc = g["city"].value_counts().head(15); yr = g["year"].value_counts().sort_index().tail(6)
    qa=[(f"How many businesses are registered in {k}, Texas?", f"{len(g):,} franchise tax entities list a {k} address; {share:.0f}% have an active right to transact business."),
        (f"Where do I file an assumed name (DBA) in {k}?", "Sole proprietors and general partnerships file assumed name certificates with the county clerk; LLCs and corporations file Form 503 with the Texas SOS.")]
    body=f'''<h1>{e(k)}, Texas business directory</h1><p class="answer">{len(g):,} registered entities in {e(k)}; {share:.0f}% active. Most common type: {e(ty.index[0])}.</p>
<h2>Top cities</h2><table>{"".join(f'<tr><td>{f"<a href=/tx/{slug(c)}/>{e(c)}</a>" if c in set(topc) else e(c)}</td><td>{v:,}</td></tr>' for c,v in tc.items())}</table>
<h2>Entity types</h2><table>{"".join(f"<tr><td>{e(a)}</td><td>{v:,}</td></tr>" for a,v in ty.items())}</table>
<h2>Formations by charter year (recent)</h2><table>{"".join(f"<tr><td>{a}</td><td>{v:,}</td></tr>" for a,v in yr.items())}</table>
<h2>Browse by city and type</h2><ul>{KLH(tc)}</ul>
{optin("alerts", k)}{CTA}{faqhtml(qa)}{SRC}'''
    page(f"/county/{ks}/", f"{k}, TX Business Search: Registered Businesses", f"{len(g):,} registered businesses in {k}, Texas by city, type, and year.", body, [faq(qa)], crumbitems=[("Home","/"),("Counties","/counties/"),(k,f"/county/{ks}/")], city_attr=k)
# ---- long-tail list pages ----
def bl(r): return f'<a href="/b/{r["Taxpayer Number"]}/">{e(r["Taxpayer Name"])}</a>' if r["Taxpayer Number"] in BIZ else e(r["Taxpayer Name"])
def listpage(kind,c,x,u,g):
    cs=slug(c); g=g.sort_values("_d",ascending=False); top=g.head(LIST_N); n_=len(g); act=(g["status"]=="Active").mean()*100
    newest=top["SOS Charter Date"].iloc[0] or "n/a"; county=g["county"].mode().iloc[0] if (g["county"]!="").any() else ""
    if county not in KHUB: county=""
    if kind=="type":
        h1=f"{TPLUR[x]} in {c}, Texas"; title=f"{TPLUR[x]} in {c}, TX: {n_:,} Registered ({DMAX:%Y})"; lbl=TPLUR[x]
        intro=f"{n_:,} {TPLUR[x].lower()} list a {c} mailing address in Texas Comptroller franchise tax data; {act:.0f}% have an active right to transact business. The most recent charter date on file is {newest}. Below are the {len(top)} most recently chartered."
    elif kind=="new":
        h1=f"New businesses in {c}, Texas (last 30 days)"; title=f"New {c}, TX Businesses: {n_:,} Chartered Since {D30:%b %d, %Y}"; lbl="New (last 30 days)"
        llc=(g["type"]=="LLC").sum()
        intro=f"{n_:,} entities with a {c} address show a Texas SOS charter date between {D30:%B %d, %Y} and {DMAX:%B %d, %Y}, the newest date in the current data file. {llc:,} of them are LLCs. Listed newest first."
    else:
        h1=f"{x} businesses in {c}, Texas"; title=f"{x} Businesses in {c}, TX: {n_:,} Registered"; lbl=x
        intro=f"{n_:,} entities in {c} report a NAICS code in the {x.lower()} sector to the Texas Comptroller; {act:.0f}% have an active right to transact business. NAICS is self-reported and missing for most Texas entities, so this list is not complete. Below are the {len(top)} most recently chartered."
    desc=intro[:155].rsplit(" ",1)[0]+"."
    rows="".join(f'<tr><td>{i+1}</td><td>{bl(r)}</td><td>{e(r["type"])}</td><td>{e(r["status"])}</td><td>{r["SOS Charter Date"]}</td></tr>' for i,(_,r) in enumerate(top.iterrows()))
    sib=" &middot; ".join(f'<a href="{uu}">{e(l)}</a>' for l,uu in LT[c] if uu!=u)
    il={"@context":"https://schema.org","@type":"ItemList","name":h1,"numberOfItems":len(top),"itemListElement":[{"@type":"ListItem","position":i+1,"name":nm,**({"url":f"{SITE}/b/{t}/"} if t in BIZ else {})} for i,(t,nm) in enumerate(zip(top["Taxpayer Number"],top["Taxpayer Name"]))]}
    cl = f' and <a href="/county/{slug(county)}/">{e(county)}</a>' if county else ""
    body=f'''<h1>{e(h1)}</h1><p class="answer">{e(intro)}</p>
<table><tr><th>#</th><th>Name</th><th>Type</th><th>Status</th><th>Chartered</th></tr>{rows}</table>
<p>See the <a href="/tx/{cs}/">{e(c)} business directory</a>{cl}.</p><h2>More {e(c)} lists</h2><p>{sib}</p>{optin("alerts",c)}{CTA}{SRC}'''
    page(u,title,desc,body,[il],crumbitems=[("Home","/"),("Cities","/cities/"),(c,f"/tx/{cs}/"),(lbl,u)],city_attr=c)
# ---- business pages ----
ENT = re.compile(r"\b(LLC|L\.L\.C|INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LP|L\.P|LTD|LLP|PLLC|PC|P\.C|TRUST|FOUNDATION|ASSOCIATION|ASSN|PARTNERS|PARTNERSHIP|GROUP|HOLDINGS|CHURCH|MINISTRIES|SERVICES|ENTERPRISES|VENTURES|PROPERTIES|INVESTMENTS)\b")
ranked = TX.sort_values("_d",ascending=False)
IDX = set(ranked["Taxpayer Number"].head(INDEX_BATCH))
BIZ = set(ranked["Taxpayer Number"].head(BIZ_TOTAL)) | SAMPLE_BIZ
json.dump([x[:4]+[x[4] if x[4] in BIZ else ""] for x in idx], open(OUT+"/search/index.json","w"), separators=(",",":"))
LTC={}
for j in LTJOBS: listpage(*j); LTC[j[0]]=LTC.get(j[0],0)+1
for r in TX[TX["Taxpayer Number"].isin(BIZ)].to_dict("records"):
    cs = slug(r["city"]); tn=r["Taxpayer Number"]; ent=bool(ENT.search(r["Taxpayer Name"]))
    addr = f'{e(r["Taxpayer Address"])}, {e(r["city"])}, TX {r["Taxpayer Zip"]}' if ent else f'{e(r["city"])}, TX (street address withheld)'
    hub = r["city"] in LT; cu = f"/tx/{cs}/" if hub else "/cities/"
    rel=([(f"{r['city']} business directory",cu)] if hub else [])+[(l,u) for l,u in LT.get(r["city"],[]) if (r["type"] in TSLUG and u.endswith(f"/{TSLUG[r['type']]}/")) or (r["ind"] and u.endswith(f"/industry/{slug(r['ind'])}/"))]
    if r["county"] in KHUB: rel.append((f"{r['county']} businesses",f"/county/{slug(r['county'])}/"))
    para=f"{r['Taxpayer Name']} is a {r['type'].lower()} whose Texas Comptroller franchise tax record lists a mailing address in {r['city']}{', '+r['county'] if r['county'] else ''}, Texas. "+(f"Its Texas SOS charter date is {r['SOS Charter Date']}. " if r["SOS Charter Date"] else "No SOS charter date is on file. ")+f"Its right to transact business status is {r['status'].lower()}."+(f" It reports a NAICS industry code in the {r['ind'].lower()} sector." if r["ind"] else "")
    lb = {"@context":"https://schema.org","@type":"Organization","name":r["Taxpayer Name"],"address":{"@type":"PostalAddress","addressLocality":r["city"],"addressRegion":"TX"}}
    cty = ", "+e(r["county"]) if r["county"] else ""
    relh = "".join(f'<li><a href="{u}">{e(l)}</a></li>' for l,u in rel)
    body = f'''<h1>{e(r["Taxpayer Name"])}</h1><p class="answer">{e(para)}</p>
<table><tr><td>Entity type</td><td>{e(r["type"])}</td></tr><tr><td>Right to transact (status)</td><td>{e(r["status"])}</td></tr><tr><td>SOS charter (registration) date</td><td>{r["SOS Charter Date"] or "n/a"}</td></tr><tr><td>City / county</td><td>{e(r["city"])}{cty}</td></tr><tr><td>Mailing address</td><td>{addr}</td></tr><tr><td>Taxpayer number</td><td>{tn}</td></tr><tr><td>SOS file number</td><td>{r["Secretary of State (SOS) or COA File Number"] or "n/a"}</td></tr><tr><td>Industry (NAICS)</td><td>{e(r["ind"] or "Not reported")}</td></tr><tr><td>Registered agent</td><td>Not in Comptroller data; see <a href="https://www.sos.texas.gov/corp/sosda/index.shtml">Texas SOS</a></td></tr></table>
<p><a href="https://comptroller.texas.gov/taxes/franchise/account-status/search">Verify on the official Comptroller search</a>.</p><h2>Related</h2><ul>{relh}</ul>{optin("alerts", r["city"])}{CTA}{SRC}'''
    page(f"/b/{tn}/", f"{r['Taxpayer Name']}: {r['city']}, TX {r['type']} Record", f"{r['type']} in {r['city']}, Texas. Status {r['status'].lower()}, chartered {r['SOS Charter Date'] or 'n/a'}. Free record from Comptroller data.", body, [lb], noindex=tn not in IDX, crumbitems=[("Home","/"),(r["city"] if hub else "Cities",cu),(r["Taxpayer Name"],f"/b/{tn}/")])
LLCQA = [("What does a Texas LLC cost to form?","$300 SOS filing fee for Form 205, plus optional registered agent and service costs."),("Do Texas LLCs pay franchise tax?","Yes, LLCs are taxable entities. Many owe no tax below the no-tax-due threshold but must still file reports. Check current thresholds at comptroller.texas.gov.")]
page("/start-an-llc/", "How to Start an LLC in Texas (Step by Step)", "Steps, costs, and forms to start a Texas LLC.", f'''<h1>How to start an LLC in Texas</h1><p class="answer">Check name availability, appoint a registered agent, file Form 205 with the Texas SOS ($300), get an EIN, and register for franchise tax.</p>
<ol><li>Search the name (our <a href="/search/">search</a> or Texas SOS).</li><li>Choose a registered agent with a Texas address.</li><li>File Certificate of Formation (Form 205).</li><li>Get an EIN from the IRS (free).</li><li>Set up franchise tax with the Comptroller.</li></ol>{CTA}{optin()}{faqhtml(LLCQA)}{SRC}''', [faq(LLCQA)], crumbitems=[("Home","/"),("Start an LLC","/start-an-llc/")])
page("/privacy/", "Privacy Policy", "How we handle data and email.", f'''<h1>Privacy</h1><p>Business records here come from public Texas Comptroller open data. We do not sell personal information. If you subscribe, we store your email only to send what you asked for; every email has an unsubscribe link. Partner links may use cookies to credit referrals. To remove or correct a record, use the <a href="/remove/">removal request</a>. Operator: {OPERATOR}. Contact: <a href="mailto:{CONTACT}">{CONTACT}</a>. Email sign-ups are stored in our CRM (GoHighLevel). We do not use third-party advertising trackers.</p>''', crumbitems=[("Home","/"),("Privacy","/privacy/")])
page("/about/", "About and Data Sources", "Where our Texas business data comes from.", f"<h1>About</h1><p>Independent reference. Not affiliated with the State of Texas.</p>{SRC}", [ORGLD], crumbitems=[("Home","/"),("About","/about/")])
page("/remove/", "Request Record Removal", "Request removal or correction of a listing.", f'<h1>Request removal</h1><form method="post" action="mailto:m.a.langston@agentmail.to" enctype="text/plain"><input name="taxpayer" placeholder="Taxpayer number"><input type="email" name="email" placeholder="Your email"><button>Submit</button></form><p>Or email <a href="mailto:{CONTACT}">{CONTACT}</a> with the taxpayer number.</p>', noindex=True)
import glob as _g
for f in _g.glob(OUT+"/sitemap*.xml"): os.remove(f)
SMN=10000; chunks=[pages[i:i+SMN] for i in range(0,len(pages),SMN)]
for i,ch in enumerate(chunks): open(f"{OUT}/sitemap-{i+1}.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{SITE}{p}</loc></url>" for p in ch)+"</urlset>")
open(OUT+"/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<sitemap><loc>{SITE}/sitemap-{i+1}.xml</loc></sitemap>" for i in range(len(chunks)))+"</sitemapindex>")
open(OUT+"/robots.txt","w").write("User-agent: *\nAllow: /\n\n"+"".join(f"User-agent: {b}\nAllow: /\n\n" for b in ["GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","PerplexityBot","Google-Extended","Applebot-Extended","CCBot"])+f"Sitemap: {SITE}/sitemap.xml\n")
open(OUT+"/llms.txt","w").write(f"# {NAME}\n\n> Independent, free Texas business entity lookup built on Texas Comptroller open data. Not a government agency.\n\n## Key pages\n- [Texas business search]({SITE}/search/)\n- [Businesses by city]({SITE}/cities/)\n- [How to start an LLC in Texas]({SITE}/start-an-llc/)\n- [Data sources]({SITE}/about/)\n- City lists: /tx/<city>/llcs/, /tx/<city>/corporations/, /tx/<city>/new/ (last 30 days), /tx/<city>/industry/<sector>/\n- Business records: /b/<taxpayer-number>/ (first batch indexable)\n- [Sitemap index]({SITE}/sitemap.xml)\n\n## Facts\n- Texas SOS online search costs $1.00 per search; Comptroller Taxable Entity Search is free.\n- Texas LLC formation (Form 205) SOS filing fee: $300.\n")
print("pages indexed", len(pages), "list pages", LTC, "business pages", len(BIZ), "indexable biz", len(IDX & BIZ))

open(OUT+"/CNAME","w").write("texasllclookup.com\n")
open(OUT+"/.nojekyll","w").write("")
