import os, re, json, time, urllib.request
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE)
OLD = json.load(open(os.path.join(HERE, "..", "..", "..", "HDRK", "MS", "build", "refs_hdrk.json"), encoding="utf-8"))
T = pd.read_csv(os.path.join(MS, "refs", "lit_candidates_smok.tsv"), sep="\t", dtype=str).fillna("").set_index("key")
src = open(os.path.join(HERE, "content_smok.py"), encoding="utf-8").read(); src = re.sub(r"(?m)^\s*#.*$", "", src)
keys = sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")})
EXTRA = {}   # 추가 PMID(검색 후 수동 지정) key -> pmid
WEB = {
 "web:kdca2026kchs": dict(type="web", authors="Korea Disease Control and Prevention Agency", title="Korea Community Health Survey: district current smoking prevalence (table DT_H_SM) and health behaviour indicators, 2011-2024. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="November 19, 2026"),
 "web:kosis2026": dict(type="web", authors="Statistics Korea", title="Population and housing census, vital statistics, and basic livelihood security recipients by district, 2011-2024. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="November 19, 2026"),
 "web:mois2026licensing": dict(type="web", authors="Ministry of the Interior and Safety", title="Local administrative licensing data: entertainment bars and singing bars, 2011-2024. Public Data Portal", url="https://www.data.go.kr", year=2026, accessed="November 19, 2026"),
 "web:rcore2026": dict(type="web", authors="R Core Team", title="R: a language and environment for statistical computing. Vienna: R Foundation for Statistical Computing", url="https://www.R-project.org", year=2026, accessed="November 19, 2026"),
}
out = {}; need = []
for k in keys:
    if k.startswith("web:"): out[k] = WEB[k]
    elif k in OLD: out[k] = OLD[k]
    elif k in T.index or k in EXTRA: need.append(k)
    else: raise SystemExit(f"키 없음: {k}")
pm = {k: (EXTRA.get(k) or T.loc[k, "pmid"]) for k in need}
if pm:
    d = json.load(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(pm.values()), timeout=60))["result"]
    for k, p in pm.items():
        r = d[p]; au = [a["name"] for a in r["authors"] if a.get("authtype", "Author") == "Author"] or [a["name"] for a in r["authors"]]
        doi = next((a["value"] for a in r["articleids"] if a["idtype"] == "doi"), "")
        pages = r.get("pages", "") or (r.get("elocationid", "").split("doi:")[0].replace("pii:", "").strip() if r.get("elocationid") else "")
        out[k] = dict(type="journal", authors=au, title=r["title"].rstrip("."), journal=r["source"].replace(".", ""), year=int(r["pubdate"][:4]), vol=r.get("volume", ""), issue=r.get("issue", ""), pages=pages, doi=doi, pmid=p, fulljournal=r.get("fulljournalname", ""), verified="PubMed esummary " + time.strftime("%Y-%m-%d"))
def fullp(p):
    m = re.match(r"^(\d+)-(\d+)$", str(p))
    if not m: return p
    a, b = m.groups(); return p if len(b) >= len(a) else f"{a}-{a[:len(a)-len(b)]+b}"
FIXP = {"jang2026living": "1251", "kim2016impact": "754", "lee2026trends": ""}   # 전자 논문 번호·온라인 선공개(PubMed esummary 쪽수 없음)
for k, v in out.items():
    if v.get("type") == "journal":
        if k in FIXP: v["pages"] = FIXP[k]
        v["pages"] = fullp(v.get("pages", ""))
        if v["title"].isupper(): v["title"] = v["title"].capitalize()
json.dump(out, open(os.path.join(HERE, "refs_smok.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("refs", len(out), "new", len(pm))
