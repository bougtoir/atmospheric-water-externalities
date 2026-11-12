"""Gate 0: fetch Crossref metadata for every cited DOI; raw JSON kept, ledger + verified CSV written."""
import json, hashlib, datetime as dt, pathlib, urllib.parse, urllib.request, csv, time
KEYS = dict(l.split(",", 1) for l in pathlib.Path("references/doi_list.csv").read_text().split("\n")[1:] if l.strip())
RAW = pathlib.Path("references/crossref_raw"); rows = []; led = []
for k, doi in KEYS.items():
    doi = doi.strip(); f = RAW / f"{k}.json"
    if not f.exists():
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi) + "?mailto=bougtoir@gmail.com"
        b = urllib.request.urlopen(url, timeout=60).read(); f.write_bytes(b); time.sleep(0.5)
        led.append([f.name, url, dt.datetime.utcnow().isoformat(timespec="seconds"), len(b), hashlib.sha256(b).hexdigest(), "Crossref metadata (CC0)"])
    m = json.loads(f.read_text())["message"]
    au = "; ".join(f"{a.get('family','')} {''.join(x[0]+'.' for x in a.get('given','').replace('-',' ').split())}".strip() for a in m.get("author", []))
    yr = (m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0][0]
    rows.append(dict(key=k, doi=m["DOI"].lower(), year=yr, authors=au, title=m["title"][0], journal=(m.get("container-title") or [""])[0],
                     volume=m.get("volume", ""), pages=m.get("page", m.get("article-number", "")), type=m["type"]))
with open("references/references_verified.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, rows[0].keys()); w.writeheader(); w.writerows(rows)
lp = RAW / "LEDGER.csv"; new = not lp.exists()
with open(lp, "a", newline="") as fh:
    w = csv.writer(fh)
    if new: w.writerow(["file", "url", "retrieved_utc", "bytes", "sha256", "terms"])
    w.writerows(led)
for r in rows: print(r["key"], r["year"], r["journal"][:30], "|", r["title"][:70], "|", r["authors"][:40])
