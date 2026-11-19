#  NTR 규정(2026-11-19 원문): ≤4,000단어, 구조 초록 ~250(Introduction/Methods/Results/Conclusions, 약어·인용 금지), Implications 50–100단어, 그림+표 ≤6, 참고 ≤50,
#  단독 저자·홍익대 단독 소속. 산출: out/Manuscript_NTR_SMOK.docx·pdf, out/Supplementary_NTR_SMOK.docx·pdf, out/Figures/.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING
from jkms_engine import JKMS
import content_smok as C
import pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
AN = os.path.normpath(os.path.join(MS, "..")); ROOT = os.path.normpath(os.path.join(AN, "..", ".."))
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_smok.json"), encoding="utf-8"))
rdf = lambda f, d: open(os.path.join(OUT, f)).read().strip() if os.path.exists(os.path.join(OUT, f)) else d
ZENODO = rdf("zenodo_doi.txt", "10.5281/zenodo.PENDING")
ORCID = "0000-0002-1525-0091"; TAG = "NTR_SMOK"
ADDR = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
AI_STATEMENT = ("During the preparation of this work the author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing. "
                "After using these tools, the author reviewed and edited the content as needed and takes full responsibility for the content of the publication.")
FUNDING = "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
COI = "None declared. The author has no financial relationships with the tobacco, e-cigarette, or pharmaceutical industries."
CONTRIB = "Seongdae Kim: conceptualization, methodology, software, formal analysis, data curation, visualization, writing (original draft), and writing (review and editing)."
def data_statement():
    return ("All source data are publicly available aggregate statistics from the Korea Disease Control and Prevention Agency, Statistics Korea, and the Ministry of the Interior and Safety, as cited in the Methods. "
            f"The analysis code that generates every number, table, and figure is openly available on Zenodo (https://doi.org/{ZENODO}) under the MIT license. The processed district-year analytic data are available from the author on reasonable request.")

def ama(k):
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. Published {r['year']}. Accessed {r['accessed']}. {r['url']}"
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al"
    t = r["title"].rstrip("."); end = "" if t.endswith(("?", "!")) else "."
    s = f"{a}. {t}{end} <i>{r['journal']}</i>. " + (f"{r['year']}" if r.get("vol") else f"Published online {r['year']}")
    if r.get("vol"): s += f";{r['vol']}" + (f"({r['issue']})" if r.get("issue") else "")
    if r.get("pages"): s += f":{r['pages']}"
    return s + "." + (f" doi:{r['doi']}" if r.get("doi") else "")
def render(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def strip(t): return re.sub(r"<[^>]+>", "", re.sub(r"\s*\[@[^\]]+\]", "", t))

class TX(JKMS):
    raw = False
    def head(self, text, level=1):
        p = super().head(text, level)
        if p is not None: p.paragraph_format.keep_with_next = True
        return p
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(;])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

TRANS = {C.BAR: "log1p"}
def f3(d): return f"{C.r3(d['OR'])} ({C.r3(d['lo'])}-{C.r3(d['hi'])})"
def st(d): return f"{C.r3(d['OR'])}{'*' if d['cred'] else ''}"
def table1():
    P = pd.read_csv(os.path.join(AN, "panel_SMOK_std3.csv"), encoding="utf-8-sig")
    FO = pd.read_csv(os.path.join(ROOT, "02_패널", "SMOK_fh_outcomes.csv"), encoding="utf-8-sig")
    P = P.drop(columns=[c for c in ["SR", "SR_SE", "N"] if c in P]).merge(FO[["year", "fbd_region", "SR", "SR_SE", "N", "male_SR"]], on=["year", "fbd_region"], validate="one_to_one")
    win = [("2011-2015", P.year <= 2015), ("2016-2019", P.year.between(2016, 2019)), ("2020-2024", P.year >= 2020), ("All years", P.year > 0)]
    def mi(x): x = x.dropna(); q = np.percentile(x, [50, 25, 75]); dg = 1 if np.median(np.abs(x)) >= 10 else 2; return f"{q[0]:.{dg}f} ({q[1]:.{dg}f}-{q[2]:.{dg}f})"
    rows = [["__H__", "Outcome"],
            ["  District-years (n)"] + [f"{int(m.sum()):,}" for _, m in win],
            ["  Survey responses (n)"] + [f"{int(P.loc[m, 'N'].sum()):,}" for _, m in win],
            ["  Current smoking, %a"] + [mi(P.loc[m, "SR"]) for _, m in win],
            ["  Standard error, percentage points"] + [mi(P.loc[m, "SR_SE"]) for _, m in win],
            ["  Current smoking in men, %"] + [mi(P.loc[m, "male_SR"]) for _, m in win]]
    for g, vs in C.GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            x = P[v + "_raw"]; x = np.expm1(x) if TRANS.get(v) == "log1p" else x
            rows.append([f"  {C.LABEL[v].replace(' (log)', '')}, {C.UNIT[v]}"] + [mi(x[m]) for _, m in win])
    foot = ("Values are medians (interquartile ranges) across district-years unless stated otherwise; covariates are shown before transformation and standardization. "
            "a Adults aged 19 years or older who had smoked at least 100 cigarettes and currently smoked daily or occasionally, age-sex-standardized to the 2005 projected population.")
    return ("Table 1. Current smoking and district covariates by calendar window, 229 Korean districts, 2011-2024", ["Characteristic", "2011-2015", "2016-2019", "2020-2024", "All years"], rows, foot)
def table2():
    rows = []
    for g, vs in C.GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            ctrl = g == "Controls"
            rows.append([f"  {C.LABEL[v]}" + ("†" if v in N["robust"] else ""), "NA" if ctrl else C.EXPECT[v], f3(N["main"][v]) + ("*" if N["main"][v]["cred"] else ""),
                         "NA" if ctrl else f"{100*N['mv'][v]['cred']:.0f}", st(N["kh"][f"KH_II|{v}"]), st(N["kh"][f"KH_IV|{v}"]),
                         st(N["rsr"][v]), st(N["splus"][v])])
    foot = (f"Odds ratios (ORs) of current smoking per 1 standard deviation with 95% credible intervals (CrIs), main spatiotemporal Fay-Herriot model (n = {N['n_cells']:,} district-years). "
            "* 95% CrI excludes 1. † Met all robustness criteria (Methods). NA, not applicable (controls entered every model). "
            "a Hypothesized direction: + higher, − lower prevalence. "
            f"b Share of the {N['n_specs']} covariate-subset models containing the covariate in which the 95% CrI excluded 1. "
            "c Knorr-Held space-time interaction models, type II and type IV. "
            "d Restricted spatial regression and Spatial+ adjustments for spatial confounding.")
    return ("Table 2. District covariates and current smoking, Korea, 2011-2024", ["Covariate", "Expecteda", "OR (95% CrI)", "Credible, %b", "KH IIc", "KH IVc", "RSRd", "Spatial+d"], rows, foot)
SUPS = ("Expecteda", "Credible, %b", "KH IIc", "KH IVc", "RSRd", "Spatial+d", "smoking, %a")
def sup_letters(J):
    for t in J.doc.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    for r in p.runs:
                        m = re.match(r"^(.*?)([abcd])$", r.text)
                        if m and r.text.endswith(SUPS):
                            r.text = m.group(1); n = p.add_run(m.group(2)); n.font.superscript = True; n.font.size = r.font.size; n.font.name = r.font.name; r._element.addnext(n._element)
def add_table(J, t, fs):
    J.page_break(); n0 = len(J.doc.paragraphs); J.table_fit(t[0], t[1], t[2], t[3], fs_max=fs, title_bold=True)
    for row in J.doc.tables[-1].rows:
        for c in row.cells:
            for p in c.paragraphs:
                sz = next((r.font.size.pt for r in p.runs if r.font.size), fs); p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(round(1.25 * sz, 1))
    for p in J.doc.paragraphs[n0:]:
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(13)
        if p.text.startswith(("Values are", "Odds ratios", "Estimates", "Spearman")):
            for r in p.runs: r.font.size = Pt(9.5)

def counts():
    aw = sum(len(strip(x).split()) for x in C.ABSTRACT.values()) + len(C.ABSTRACT)
    secs = C.METHODS + C.RESULTS + C.DISCUSSION
    bw = sum(len(strip(p).split()) for p in C.INTRO) + sum(len(h.split()) + sum(len(strip(p).split()) for p in ps) for h, *ps in secs) + len(C.CONCLUSION.split()) + 5
    return aw, bw, len(C.IMPLICATIONS.split())

def build_main(aw, bw, iw):
    J = TX(cite="bracket")
    J.para(f"<b>{C.TITLE}</b>")
    J.para("Seongdae Kim, PhD", before=12); J.para(ADDR)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDR}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para(f"<b>Running head:</b> {C.RUNNING}", before=6)
    J.para(f"<b>Word counts:</b> abstract {aw}; main text {bw:,}; implications {iw}. <b>Tables and figures:</b> 2 tables and 2 figures. <b>References:</b> {{NREF}}.", before=6)
    J.page_break()
    J.head("Abstract", 1)
    for h, t in C.ABSTRACT.items(): J.para(f"<b>{h}:</b> {t}")
    J.head("Implications", 1); J.para(C.IMPLICATIONS)
    J.para(f"<b>Keywords:</b> {'; '.join(C.KEYWORDS)}")
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in C.INTRO: J.para(render(p), indent=True)
    J.head("Methods", 1)
    for h, *ps in C.METHODS:
        J.head(h, 2)
        for p in ps: J.para(render(p), indent=True)
    J.head("Results", 1)
    for h, *ps in C.RESULTS:
        J.head(h, 2)
        for p in ps: J.para(render(p), indent=True)
    J.head("Discussion", 1)
    for h, *ps in C.DISCUSSION:
        J.head(h, 2)
        for p in ps: J.para(render(p), indent=True)
    J.head("Conclusions", 1); J.para(C.CONCLUSION, indent=True)
    J.counting = False
    J.head("Funding", 1); J.para(FUNDING)
    J.head("Declaration of Interests", 1); J.para(COI)
    J.head("Author Contributions", 1); J.raw = True; J.para(CONTRIB); J.raw = False
    J.head("Use of Artificial Intelligence Tools", 1); J.para(AI_STATEMENT)
    J.head("Acknowledgments", 1); J.para(C.ACK)
    J.head("Data Availability", 1); J.para(data_statement())
    J.page_break(); J.head("References", 1); J.raw = True
    for n, k in enumerate(J.cites, 1): J.para(f"{n}. " + ama(k))
    J.raw = False
    add_table(J, table1(), 9); add_table(J, table2(), 8); sup_letters(J)
    J.page_break(); J.head("Figure Legends", 1)
    for k in sorted(C.FIGCAP): J.para(f"<b>Figure {k}.</b> {C.FIGCAP[k]}")
    return J

# ── 보충 표(S1 사양 목록, S2–S6 민감도) ──
def sens_table(title, cols, getters, foot):
    rows = []
    for g, vs in C.GROUPS[:3]:
        rows.append(["__H__", g])
        for v in vs: rows.append([f"  {C.LABEL[v]}"] + [st(f(v)) if f(v) is not None else "NA" for f in getters])
    return (title, ["Covariate"] + cols, rows, foot)
def supplement():
    S = TX(cite="bracket"); S.para(f"<b>Supplementary Material</b>"); S.para(f"<b>{C.TITLE}</b>", before=6); S.para("Seongdae Kim", before=6)
    FT = "Odds ratios per 1 standard deviation; * 95% credible interval excludes 1. NA, covariate not in the model."
    tabs = []
    W = ["W1_2011-15", "W2_2016-19", "W3_2020-24"]
    tabs.append(sens_table("Supplementary Table S1. Calendar windows, post-2020 interaction, and lags", ["2011-2015", "2016-2019", "2020-2024", "Post-2020 × covariatea", "Lag 1 year", "Lag 2 years"],
        [lambda v, w=w: N["win"][f"{w}|{v}"] for w in W] + [lambda v: N["covid"][v], lambda v: N["lag"][f"1|{v}"], lambda v: N["lag"][f"2|{v}"]], FT + " a Ratio of odds ratios after versus before 2020."))
    tabs.append(sens_table("Supplementary Table S2. Space-time interaction, spatial confounding, and decomposition", ["KH II", "KH III", "KH IV", "RSR", "Spatial+", "Between", "Within"],
        [lambda v: N["kh"][f"KH_II|{v}"], lambda v: N["kh"][f"KH_III|{v}"], lambda v: N["kh"][f"KH_IV|{v}"], lambda v: N["rsr"][v], lambda v: N["splus"][v], lambda v: N["bw"][f"{v}|between"], lambda v: N["bw"][f"{v}|within"]],
        FT + f" WAIC: main {N['waic_main']:.1f}; KH II {N['kh_waic']['KH_II']:.1f}; KH III {N['kh_waic']['KH_III']:.1f}; KH IV {N['kh_waic']['KH_IV']:.1f}. RSR, restricted spatial regression."))
    L = ["binom", "beta", "gfree", "crude_rate_FH_plus_old65"]
    tabs.append(sens_table("Supplementary Table S3. Alternative likelihoods, graph, prior, and influential observations", ["Binomial", "Beta", "Unweighted Gaussian", "Crude prevalence + aged 65+", "Queen graph", "Alternative prior", "Influential removed"],
        [lambda v, l=l: N["lik"].get(f"{l}|{v}") for l in L] + [lambda v: N["gp"][f"queen_graph|{v}"], lambda v: N["gp"][f"pc_prior_alt|{v}"], lambda v: N["infl"][v]], FT))
    SV = ["sido_year_iid", "plus_dmkid", "plus_kchs_index", "all_three"]
    tabs.append(sens_table("Supplementary Table S4. Survey-based covariates and survey-operation effects", ["Without survey covariates", "+ High-risk drinking only", "+ Stress only", "Province × year", "+ Unrelated item", "+ Item index", "All"],
        [lambda v: N["same"].get(f"non_survey_covariates_only|{v}"), lambda v: N["same"].get(f"non_survey_plus_high_risk_drinking_rate_drinkers|{v}"), lambda v: N["same"].get(f"non_survey_plus_perceived_stress_rate|{v}")]
        + [lambda v, s=s: N["svy"][f"{s}|{v}"] for s in SV],
        FT + " Unrelated item, diabetic kidney test uptake (KCHS); item index, mean of standardized diabetic kidney testing, rear-seat belt use, and nutrition label use (KCHS)."))
    loo = [["__H__", "Leave one province out"]] + [[f"  {C.LABEL[v]}", f"{N['loo'][v]['n_cred']}/{N['loo'][v]['n']}", f"{N['loo'][v]['n_sign']}/{N['loo'][v]['n']}", f"{C.r3(N['loo'][v]['mn'])}-{C.r3(N['loo'][v]['mx'])}"] for v in N["hyp"]]
    tabs.append(("Supplementary Table S5. Leaving out each of 17 provinces", ["Covariate", "Credible", "Same sign", "OR range"], loo, "Counts of the 17 refits in which the 95% credible interval excluded 1 and in which the sign matched the main model."))
    tabs.append(sens_table("Supplementary Table S6. Male smoking and manufacturing share", ["Male smoking, 2011-2024", "Main model, 2017-2024", "+ Manufacturing share, 2017-2024"],
        [lambda v: N["male"][v], lambda v: N["mfg"][f"main_2017_2024|{v}"], lambda v: N["mfg"][f"plus_manufacturing_2017_2024|{v}"]],
        FT + f" Manufacturing share OR {f3(N['mfg']['plus_manufacturing_2017_2024|mfg'])}. Spearman correlation of district spatial odds ratios, male vs total smoking: {N['male_sum']['spearman_spatialOR_male_vs_total']:.2f}."))
    mvr = [["__H__", f"{N['n_specs']} covariate-subset models"]] + [[f"  {C.LABEL[v]}", str(N['mv'][v]['n']), f"{100*N['mv'][v]['cred']:.0f}", f"{100*N['mv'][v]['sign']:.0f}", f"{C.r3(N['mv'][v]['med'])} ({C.r3(N['mv'][v]['mn'])}-{C.r3(N['mv'][v]['mx'])})"] for v in N["hyp"]]
    tabs.append(("Supplementary Table S7. Multiverse of covariate subsets", ["Covariate", "Models (n)", "Credible, %", "Sign agreement, %", "Median OR (range)"], mvr, "Each model contained the five structural controls and one non-empty subset of the seven covariates."))
    tabs.append(sens_table("Supplementary Table S8. Between-district and within-district components, 2015-2024", ["Between", "Within"],
        [lambda v: N["bw15"][f"{v}|between"], lambda v: N["bw15"][f"{v}|within"]], FT + " Restricted to 2015-2024, when single-person household shares were observed annually."))
    ng = [[f"  {k.replace('_', ' ')}", f3(d) + ("*" if d["cred"] else "")] for k, d in N["neg"].items()]
    tabs.append(("Supplementary Table S9. Negative-control exposures", ["Exposure", "OR (95% CrI)"], [["__H__", "Added one at a time to the main model"]] + ng, "Odds ratios per 1 standard deviation; * 95% credible interval excludes 1."))
    for t in tabs: add_table(S, t, 9)
    sup_letters(S)
    S.page_break(); S.head("Supplementary Figure S1", 1); S.para("Annual Moran's I of logit current smoking prevalence, 2011-2024: " + "; ".join(f"{y} {v:.2f}" for y, v in N["moran_year"].items()) + ".")
    S.doc_title = "Supplementary Material"; p = os.path.join(OUT, f"Supplementary_{TAG}.docx"); S.save(p); return p

def to_pdf(p):
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_smok", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)

if __name__ == "__main__":
    aw, bw, iw = counts()
    assert aw <= 250, aw; assert bw <= 4000, bw; assert 50 <= iw <= 100, iw; assert ":" not in C.TITLE
    J = build_main(aw, bw, iw); nref = len(J.cites); assert nref <= 50, nref; assert all(k in REFS for k in J.cites)
    for p in J.doc.paragraphs:
        for r in p.runs:
            if "{NREF}" in r.text: r.text = r.text.replace("{NREF}", str(nref))
    mp = os.path.join(OUT, f"Manuscript_{TAG}.docx"); J.doc_title = C.TITLE; J.save(mp); to_pdf(mp)
    sp = supplement(); to_pdf(sp)
    open(os.path.join(OUT, "wordcount_ntr.txt"), "w").write(f"abstract_words={aw}\nbody_words={bw}\nimplications_words={iw}\nrefs={nref}\ntables=2\nfigures=2\n")
    print(f"abstract {aw} | body {bw} | implications {iw} | refs {nref}")
