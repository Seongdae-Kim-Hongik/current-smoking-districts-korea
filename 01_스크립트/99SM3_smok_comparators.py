#!/usr/bin/env python3
import os, sqlite3, unicodedata
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DB = os.path.expandvars("$ST_GPT_DATASET/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
S = pd.read_sql("SELECT fbd_region, SUM(cases) O, SUM(E) E FROM disease_panel WHERE tag='SUIC' GROUP BY fbd_region", con); S["fbd_region"] = S.fbd_region.map(NFC); S["suic_smr"] = S.O / S.E
FO = pd.read_csv(os.path.join(ROOT, "02_패널", "SMOK_fh_outcomes.csv"), encoding="utf-8-sig"); FO["fbd_region"] = FO.fbd_region.map(NFC)
A = FO.groupby("fbd_region")[["SR", "hdrk_SR", "male_SR"]].mean().reset_index()
SP = pd.read_csv(os.path.join(ROOT, "04_분석", "SMOK", "results_std3", "S3_spatial_OR.csv")); SP["fbd_region"] = SP.fbd_region.map(NFC)
J = A.merge(S[["fbd_region", "suic_smr"]], on="fbd_region", how="left").merge(SP[["fbd_region", "OR", "class"]], on="fbd_region", how="left")
assert len(J) == 229 and J.suic_smr.notna().all() and J.OR.notna().all()
rows = []
for a, b in [("SR", "suic_smr"), ("SR", "hdrk_SR"), ("OR", "suic_smr"), ("OR", "hdrk_SR"), ("SR", "male_SR")]:
    rows.append(dict(x=a, y=b, spearman=round(J[a].corr(J[b], method="spearman"), 3)))
q = lambda s: s >= s.quantile(.75)
rows.append(dict(x="top_quartile_all_three(SR,suic_smr,hdrk_SR)", y="n_districts", spearman=int((q(J.SR) & q(J.suic_smr) & q(J.hdrk_SR)).sum())))
out = pd.DataFrame(rows); fp = os.path.join(ROOT, "04_분석", "SMOK", "results_std3", "S20_comparators.csv"); out.to_csv(fp, index=False); print(out.to_string()); print("저장", fp)
