#!/usr/bin/env python3
#   basic_livelihood_rate·tertiary_educated_share 를 (year, fbd_region)으로 옮기고, 정본 풀 EXT_canonical_pool_261106.csv의 alcohol_venues_per10k
#   (유흥·단란주점 영업 업소 인구 1만 명당, 행안부 인허가)를 붙여 고정한다(결측은 시군구 안 선형 보간 → 시군구 평균). 공유 원본 수정 없음.
#  산출: 02_패널/EXT_canonical_pool_SMOK_261119.csv
import os, unicodedata
import pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
PAN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "02_패널")
d = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_STRS_261113.csv"), encoding="utf-8-sig"); d["fbd_region"] = d.fbd_region.map(NFC)
d = d[(d.year >= 2011) & (d.year <= 2024)][["year", "fbd_region", "basic_livelihood_rate", "tertiary_educated_share"]].sort_values(["fbd_region", "year"])
assert d.fbd_region.nunique() == 229 and d.groupby("fbd_region").year.nunique().eq(14).all() and not d.duplicated(["year", "fbd_region"]).any()
V = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_261106.csv"), encoding="utf-8-sig"); V["fbd_region"] = V.fbd_region.map(NFC)
d = d.merge(V[["year", "fbd_region", "alcohol_venues_per10k"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
n0 = int(d.alcohol_venues_per10k.isna().sum()); d["alcohol_venues_per10k"] = d.groupby("fbd_region").alcohol_venues_per10k.transform(lambda x: x.interpolate(limit_area="inside")); d["alcohol_venues_per10k"] = d.alcohol_venues_per10k.fillna(d.groupby("fbd_region").alcohol_venues_per10k.transform("mean"))
print(f"[99c-smok] 주점 밀도 결측 {n0} → {int(d.alcohol_venues_per10k.isna().sum())}"); assert d.notna().all().all()
cw = d[(d.fbd_region == NFC("경상남도창원시")) & d.year.isin([2021, 2022, 2023])].basic_livelihood_rate; assert cw.between(2.3, 2.4).all(), cw.tolist()
fp = os.path.join(PAN, "EXT_canonical_pool_SMOK_261119.csv"); d.to_csv(fp, index=False, encoding="utf-8-sig"); print("[99c-smok] 저장", fp, d.shape); print(d.describe().T[["min", "50%", "max"]].round(2))
