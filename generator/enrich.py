"""Optional: enrich the newest business records via the Texas Comptroller public API.
Requires secret COMPTROLLER_API_KEY (register at https://api-doc.comptroller.texas.gov/). Without it, does nothing.
Caches results in data/enrich_cache.json; only stores entity-level fields (no officer data).
Usage: python enrich.py <csv> <cache.json>"""
import os, sys, json, time, urllib.request, datetime as dt, pandas as pd
KEY = os.environ.get("COMPTROLLER_API_KEY", "").strip()
CSV, CACHE = sys.argv[1], sys.argv[2]
BATCH = int(os.environ.get("ENRICH_BATCH", "5000"))   # match INDEX_BATCH in build.py
MAX_CALLS = int(os.environ.get("ENRICH_MAX", "1000"))  # per run, keeps the build short
DELAY = float(os.environ.get("ENRICH_DELAY", "0.5"))   # polite: at most 2 requests/second
TTL_DAYS = 30
FIELDS = ["rightToTransactTX","sosRegistrationStatus","effectiveSosRegistrationDate","registeredAgentName","stateOfFormation","lastUpdated","reportYear"]
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
if not KEY:
    print("enrich: no COMPTROLLER_API_KEY, skipping; cached records:", len(cache)); json.dump(cache, open(CACHE,"w")); sys.exit(0)
d = pd.read_csv(CSV, dtype=str, usecols=["Taxpayer Number","Taxpayer State","SOS Charter Date"]).fillna("")
d = d[d["Taxpayer State"].str.strip()=="TX"]
d["_d"] = pd.to_datetime(d["SOS Charter Date"], errors="coerce"); d = d[d["_d"] <= pd.Timestamp.today()]
ids = d.sort_values("_d", ascending=False)["Taxpayer Number"].str.strip().head(BATCH)
now = dt.datetime.utcnow(); calls = ok = 0
for tn in ids:
    c = cache.get(tn)
    if c and (now - dt.datetime.fromisoformat(c["_fetched"])).days < TTL_DAYS: continue
    if calls >= MAX_CALLS: break
    req = urllib.request.Request(f"https://api.comptroller.texas.gov/public-data/v1/public/franchise-tax/{tn}", headers={"x-api-key": KEY, "User-Agent": "texasllclookup.com build"})
    calls += 1
    try:
        j = json.load(urllib.request.urlopen(req, timeout=20))
        if j.get("success") and j.get("data"):
            cache[tn] = {k: j["data"].get(k) for k in FIELDS} | {"_fetched": now.isoformat()}; ok += 1
    except urllib.error.HTTPError as ex:
        if ex.code == 429: print("enrich: rate limited, stopping"); break
        if ex.code in (401, 403): print("enrich: key rejected", ex.code); break
    except Exception as ex: print("enrich error", tn, ex)
    time.sleep(DELAY)
json.dump(cache, open(CACHE, "w"))
print(f"enrich: calls {calls}, ok {ok}, cached {len(cache)}")
