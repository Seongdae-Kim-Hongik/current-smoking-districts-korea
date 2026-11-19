#  NTR: 본문 ≤4,000, 구조 초록 ≤250(Introduction/Methods/Results/Conclusions), Implications 50–100, 그림+표 ≤6, 참고 ≤50.
import os, json, math
from decimal import Decimal, ROUND_HALF_UP
HERE = os.path.dirname(os.path.abspath(__file__))
N = json.load(open(os.path.join(HERE, "numbers_smok.json"), encoding="utf-8"))
M = N["main"]
def r3(x):
    s = str(Decimal(repr(float(x))).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
    return str(Decimal(repr(float(x))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)) if s == "1.000" and abs(float(x) - 1) >= 0.00005 else s
def o(v, d=None):
    d = d or M[v]; return f"OR {r3(d['OR'])}, 95% CrI {r3(d['lo'])}-{r3(d['hi'])}"
def oa(d): return f"{r3(d['OR'])}; {r3(d['lo'])}-{r3(d['hi'])}"
def pct(x): return f"{100*x:.0f}%"
def pp(v, d=None):   # 1 SD당 OR → 평균 유병률에서 퍼센트포인트
    p = N["sr_mean_all"] / 100; return abs(100 * p * (1 - p) * math.log((d or M[v])["OR"]))
ST, DR, BAR, ED, LIV, ONE, DIV = N["hyp"]
LABEL = {ST: "Perceived stress", DR: "High-risk drinking among drinkers", BAR: "Entertainment and singing bars (log)", ED: "University-educated adults", LIV: "Basic livelihood recipients",
         ONE: "Single-person households", DIV: "Crude divorce rate",
         "urban_population_share": "Urban-zoned population share", "clinics_per_100k": "Clinics per 100,000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged 80+ years"}
UNIT = {ST: "%", DR: "%", BAR: "per 10,000", ED: "%", LIV: "%", ONE: "%", DIV: "per 1,000", "urban_population_share": "%", "clinics_per_100k": "per 100,000", "sex_ratio": "men per 100 women",
        "fiscal_independence": "%", "pop80_share": "%"}
EXPECT = {ST: "+", DR: "+", BAR: "+", ED: "−", LIV: "+", ONE: "+", DIV: "+"}
GROUPS = [("Psychological stress and co-use", [ST, DR, BAR]), ("Socioeconomic position", [ED, LIV]), ("Household and family", [ONE, DIV]),
          ("Controls", ["urban_population_share", "clinics_per_100k", "sex_ratio", "fiscal_independence", "pop80_share"])]
KH = lambda m, v: N["kh"][f"KH_{m}|{v}"]
BW = lambda v, c: N["bw"][f"{v}|{c}"]
SAME = lambda var, v: N["same"][f"{var}|{v}"]
SVY = lambda var, v: N["svy"][f"{var}|{v}"]
MV = N["mv"]; SR = N["sr"]; SRM = N["sr_male"]; C = N["comp"]
SIDO = {"강원도": "Gangwon", "경기도": "Gyeonggi", "서울시": "Seoul", "전라남도": "South Jeolla", "인천시": "Incheon", "경상남도": "South Gyeongsang", "경상북도": "North Gyeongsang", "대구시": "Daegu", "제주도": "Jeju",
        "충청남도": "South Chungcheong", "충청북도": "North Chungcheong", "전라북도": "North Jeolla", "대전시": "Daejeon", "울산시": "Ulsan", "광주시": "Gwangju", "부산시": "Busan", "세종시": "Sejong"}
def sido_list(d, k): return ", ".join(f"{SIDO[a]} ({b})" for a, b in list(d.items())[:k])
ROB = N["robust"]; NSPEC = N["n_specs"]
assert set([ST, DR, ED, ONE, DIV]) <= set(ROB) and BAR not in ROB, ROB
LIVROB = LIV in ROB
NEGC = [k for k, d in N["neg"].items() if d["cred"]]
SAMEN = "non_survey_covariates_only"

TITLE = "Smoking stayed higher in Korean districts with fewer university-educated adults, 2011-2024"
RUNNING = "District smoking in Korea, 2011-2024"
KEYWORDS = ["smoking prevalence", "education", "small-area estimation", "spatial epidemiology", "Korea"]

ABSTRACT = {
 "Introduction": "Adult smoking in Korea has fallen, but whether the fall reached all districts equally, and which local conditions accompany the remaining differences, is unclear.",
 "Methods": (f"Age-sex-standardized current smoking prevalence from the Korea Community Health Survey ({N['n_resp_total']/1e6:.1f} million responses) was modeled for 229 districts, 2011-2024, "
             "with a spatiotemporal Fay-Herriot model that used the published sampling variances and included spatial and temporal random effects. Seven district covariates (stress, high-risk drinking, entertainment-bar density, university education, welfare receipt, single-person households, divorce) were tested with "
             f"all {NSPEC} covariate-subset models, space-time interaction models, and spatial-confounding checks."),
 "Results": (f"Mean district prevalence fell from {SR['2011']}% to {SR['2024']}% and declined in {N['n_decline']} of 229 districts. Smoking clustered (Moran's I {N['moran']:.2f}) and district ranks persisted (Spearman {N['persist']:.2f}), but the 90th/10th percentile ratio was {N['p9010']:.2f}. "
             f"Per standard deviation, university education ({oa(M[ED])}) was associated with lower district smoking prevalence, and high-risk drinking ({oa(M[DR])}), divorce ({oa(M[DIV])}), single-person households ({oa(M[ONE])}), and stress ({oa(M[ST])}) with higher odds. "
             f"These five associations met all robustness criteria. Associations are odds ratios with 95% credible intervals. Welfare receipt ({oa(M[LIV])}) and entertainment-bar density were not robust."),
 "Conclusions": "District smoking in Korea declined almost everywhere but remained patterned by education and, more weakly, by drinking, stress, and household circumstances. Districts with fewer university graduates may warrant priority in cessation services and monitoring.",
}
IMPLICATIONS = ("This study shows that, over 14 years of national decline, district smoking prevalence in Korea stayed patterned by the educational composition of districts and, more weakly, by drinking, divorce, living alone, and stress. "
                "These are district-level, not individual, associations. They identify districts where prevalence remains comparatively high and where the need for and access to cessation services merit further assessment.")

INTRO = [
 ("Tobacco use remains a leading preventable cause of death in Korea. Before 2015, cigarette prices had not risen for a decade and pack warnings were text-only [@cho2014status]. Male smoking prevalence has since fallen markedly, with a pronounced drop after the 2015 price increase, "
  "and the share of adults smoking conventional cigarettes continued to decline into the 2020s [@chang2018trends; @lee2021effects; @kim2021trends; @yang2026trends]. "
  "Heated tobacco products and liquid e-cigarettes have, however, taken up part of the market, and overall tobacco use has declined more slowly than cigarette smoking [@kim2024changes; @yang2026trends]."),
 ("National averages hide social and geographic differences. Educational, occupational, and income inequalities in smoking widened in Korea while prevalence fell [@khang2009impact; @chang2019long], and income-related relative inequality persisted after the 2015 price increase [@chang2018trends]. "
  "Multilevel studies have shown that area deprivation and area income are related to smoking beyond individual characteristics, with patterns that differ by sex, occupation, and urbanicity [@duncan1999smoking; @park2010area; @yun2015household]. "
  "Small-area estimation studies elsewhere have documented several-fold differences in smoking prevalence between counties and cities, uneven declines over time, and local areas of elevated prevalence [@dwyerlindgren2014cigarette; @cui2012small; @seliske2016estimating]."),
 ("In Korea, the Korea Community Health Survey (KCHS) has measured smoking in every district each year since 2008 [@kang2015korea]. District estimates from this survey have been used to describe regional differences in health behaviors among people with chronic diseases or in combined lifestyle scores "
  "[@jeon2020health; @bui2024determinants], but, to the author's knowledge, the space-time structure of district smoking prevalence over the period of rapid national decline, and its relation to local social conditions, have not been modeled jointly. "
  "Individual-level studies suggest candidate correlates: psychological distress, heavy drinking, living alone, and marital status are each associated with smoking "
  "[@kassel2003smoking; @fujiwara2018smoking; @cheon2020factors; @lee2020associations; @jang2026living; @cho2008marital; @nystedt2006marital]."),
 ("This study therefore asked three questions. First, does age-sex-standardized smoking prevalence cluster among Korean districts, and are district ranks stable over 14 years? "
  "Second, which district conditions (psychological stress, drinking and its venues, education and deprivation, household composition) are associated with district smoking after structural controls? "
  "Third, are these associations robust to model specification, space-time interaction, spatial confounding, and the fact that several covariates come from the same survey as the outcome?"),
]

METHODS = [
 ("Design and data",
  ("This was an ecological panel study of all 229 Korean municipal districts (si, gun, and gu) from 2011 to 2024. The outcome was the KCHS current smoking prevalence: the percentage of adults aged 19 years or older who had smoked at least 100 cigarettes in their lifetime and currently smoked daily or occasionally "
   f"[@kang2015korea; @web:kdca2026kchs]. The Korea Disease Control and Prevention Agency publishes, for each district and year, a prevalence directly standardized for age and sex to the 2005 projected population, its standard error, and the number of respondents. "
   f"Published district estimates were linked by administrative code to the 229 districts used by Statistics Korea. All {N['n_cells']:,} district-years were observed ({N['n_resp_total']:,} responses; median {N['n_resp_median']:,} per district-year). Male current smoking prevalence was used as a secondary outcome."),
  ("Seven district covariates were selected for the analysis. Perceived stress prevalence and high-risk drinking prevalence among current drinkers came from the same KCHS district tables [@web:kdca2026kchs]. "
   "The density of operating entertainment and singing bars per 10,000 residents (transformed as log[1 + x]) came from local licensing records [@web:mois2026licensing]. The share of adults with a university degree, the basic livelihood security recipient rate, the share of single-person households, "
   "and the crude divorce rate came from Statistics Korea [@web:kosis2026]. The university-educated share came from the 2010, 2015, and 2020 population and housing censuses, linearly interpolated between census years and carried forward from 2020 for 2021-2024. Recipient rates for 33 district-years in 2021-2023 that were implausibly low because of reporting changes were treated as missing and interpolated within districts. "
   "Single-person household shares, available from 2015, were filled with district means for 2011-2014. Five structural controls entered every model: the urban-zoned population share, clinics per 100,000 residents, the sex ratio, fiscal autonomy, and the share of residents aged 80 years or older. "
   "All covariates were standardized, so effects are expressed per 1 standard deviation (SD)."),
  ("Variables that are the outcome itself or its components were excluded: the same current smoking indicator republished in a second official database, male smoking prevalence (used only as a secondary outcome), quit attempts, and secondhand smoke exposure. "
   "Three negative-control exposures with no expected direct link to smoking were included: fires per 10,000 residents, the share of multicultural marriages, and rear-seat belt use."),
 ),
 ("Statistical analysis",
  ("A spatiotemporal Fay-Herriot model was fitted [@fay1979estimates; @mercer2015space]. The logit of each district-year prevalence p was treated as normally distributed around a linear predictor with known sampling variance (SE/100)<sup>2</sup>/[p(1 − p)]<sup>2</sup>, derived from the published standard error (in percentage points) by the delta method, with the observation precision fixed. "
   "The linear predictor contained the covariates, a BYM2 spatial effect on a 593-edge contiguity graph (islands linked to their nearest mainland district) with penalized-complexity priors (P[σ > 0.5] = 0.01; P[φ < 0.5] = 2/3) [@riebler2016intuitive; @simpson2017penalising], a first-order random walk and an unstructured effect for year, and an unstructured district-year effect for model error. "
   "Models were fitted with integrated nested Laplace approximation in R [@rue2009approximate; @web:rcore2026]. An association was described as credible when its 95% credible interval (CrI) excluded 1."),
  ("Spatial structure was summarized by Moran's I of the 14-year district mean logit prevalence, the 90th/10th percentile ratio of 14-year district mean prevalences, the Spearman correlation of district ranks between 2011-2015 and 2020-2024, Kendall's W across years, the BYM2 mixing parameter, and district hotspots and coldspots (posterior probability that the spatial odds ratio exceeded 1 above 0.95 or below 0.05). "
   "Residual spatial autocorrelation was tested with a two-sided Moran permutation test."),
  (f"Robustness was assessed in several steps. (1) A multiverse of all {NSPEC} non-empty subsets of the seven covariates, each with the controls [@steegen2016increasing]; a covariate was called robust if its CrI excluded 1 in at least 75% of the models containing it, with at least 95% sign agreement, "
   "and if it remained credible in the Knorr-Held type II and type IV space-time interaction models [@knorrheld2000bayesian]. (2) Sensitivity to spatial confounding was assessed with restricted spatial regression and Spatial+ [@hodges2010adding; @khan2022restricted; @dupont2022spatial]. "
   "(3) Between-district and within-district components were separated by entering district means and annual deviations [@bell2015explaining]. (4) Further checks were calendar windows (2011-2015, 2016-2019, 2020-2024), a post-2020 interaction, 1-year and 2-year lags, leaving out each province, "
   "alternative likelihoods (binomial with effective sample size, beta, unweighted Gaussian, and crude prevalence with an age-65 control), a queen contiguity graph, alternative priors, and removal of influential district-years. "
   "(5) Because stress and drinking were measured in the same survey respondents as smoking, the main model was refitted without these two covariates and with each added back alone, and survey-operation effects were examined by adding province-by-year random effects and, separately, other KCHS items (diabetic kidney testing alone, or an index that also included rear-seat belt use and nutrition label use). "
   "(6) The share of manufacturing workers, available only from 2017, was added in a 2017-2024 model. Variance inflation factors were below 5 for all covariates in the main model. Reporting followed STROBE [@vonelm2007strengthening]."),
  ("For context, district mean smoking prevalence was compared descriptively with district suicide mortality ratios and high-risk drinking prevalence; these comparisons were not part of the inferential models. "
   "The institutional review board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent because only published aggregate statistics were used."),
 ),
]

def _vy(y): return N["moran_year"][str(y)]
RESULTS = [
 ("Smoking prevalence and its geography",
  (f"The unweighted mean of district prevalences fell from {SR['2011']}% in 2011 to {SR['2024']}% in 2024, with a rise from {SR['2022']}% to {SR['2023']}% in 2023; male prevalence fell from {SRM['2011']}% to {SRM['2024']}%. Between 2011-2015 and 2020-2024, prevalence declined in {N['n_decline']} of 229 districts (median change {N['chg_median']} percentage points; the only increase was {N['chg_max']} points) (Table 1). "
   f"Over 2011-2024, 14-year district means ranged from {N['sr_dist_min']}% to {N['sr_dist_max']}%, and the 90th/10th percentile ratio was {N['p9010']:.2f}. "
   f"Smoking clustered spatially (pooled Moran's I {N['moran']:.2f}; annual values {N['moran_ymin']:.2f}-{N['moran_ymax']:.2f}, all p ≤ 0.001), and district ranks persisted (Spearman {N['persist']:.2f} between 2011-2015 and 2020-2024; Kendall's W {N['kendallW']:.2f})."),
  (f"In the model with structural controls only, {N['hot_forced0']} districts were hotspots and {N['cold_forced0']} were coldspots (Figure 1C). In the main model, {N['n_hot']} hotspots remained, mainly in {sido_list(N['hot_sido'], 6)}, "
   f"and {N['n_cold']} coldspots, mainly in {sido_list(N['cold_sido'], 3)} (Figure 1D). The BYM2 mixing parameter was {N['phi_main']:.2f}. "
   f"Residual Moran's I was {N['resid_moran']:.2f} (two-sided p = {N['resid_moran_p']:.2f})."),
 ),
 ("District covariates",
  (f"In the main model, university education was associated with lower odds of smoking ({o(ED)}), and high-risk drinking ({o(DR)}), the crude divorce rate ({o(DIV)}), single-person households ({o(ONE)}), stress ({o(ST)}), and basic livelihood receipt ({o(LIV)}) with higher odds (Table 2, Figure 2). "
   f"Bar density had a small positive estimate whose interval included 1 in the full model ({o(BAR)}); it was credible in {pct(MV[BAR]['cred'])} of covariate-subset models and in several alternative specifications, but not in any Knorr-Held model, so it did not meet the robustness criteria. At the overall mean district prevalence ({N['sr_mean_all']}%), 1 SD of university education corresponded to about {pp(ED):.1f} percentage points lower prevalence, and 1 SD of each positively associated covariate to {min(pp(v) for v in (ST, DR, LIV, ONE, DIV)):.1f}-{max(pp(v) for v in (ST, DR, LIV, ONE, DIV)):.1f} points. "
   f"Adding the covariates improved fit over the controls alone (WAIC {N['waic_main']:.0f} vs {N['waic_forced']:.0f})."),
  (f"All sensitivity estimates are given in Supplementary Tables S1-S9. University education, high-risk drinking, divorce, single-person households, and stress met every robustness criterion: credible in {', '.join(pct(MV[v]['cred']) for v in (ED, DR, DIV, ONE, ST))} of the multiverse models containing them, respectively, with full sign agreement, "
   f"and credible in Knorr-Held type II, III, and IV models (type IV had the lowest WAIC; university education {oa(KH('IV', ED))}). "
   + (f"Basic livelihood receipt was credible in {pct(MV[LIV]['cred'])} of multiverse models but not in the type II model ({oa(KH('II', LIV))})." if not LIVROB else f"Basic livelihood receipt was also robust (multiverse {pct(MV[LIV]['cred'])}).")),
  (f"Associations persisted with restricted spatial regression (university education {oa(N['rsr'][ED])}) and Spatial+ ({oa(N['splus'][ED])}). University education was associated with smoking both between districts ({oa(BW(ED, 'between'))}) and within districts over time ({oa(BW(ED, 'within'))}); "
   f"drinking, stress, and divorce likewise had credible between and within components, whereas single-person households had a between-district component only ({oa(BW(ONE, 'between'))} vs {oa(BW(ONE, 'within'))}). Because household shares for 2011-2014 were filled with district means, the decomposition was repeated for 2015-2024: the between-district component of single-person households remained positive ({oa(N['bw15'][ONE+'|between'])}), whereas the within-district component was inverse ({oa(N['bw15'][ONE+'|within'])}); education had credible between and within components in this period as well (Supplementary Table S8). "
   f"The education association was somewhat stronger in 2020-2024 than in 2011-2015, with overlapping intervals (2011-2015, {oa(N['win']['W1_2011-15|' + ED])}; 2020-2024, {oa(N['win']['W3_2020-24|' + ED])}), and the post-2020 interaction terms for education, stress, drinking, and single-person households were credible."),
  (f"Without the two survey-based covariates, university education ({oa(SAME(SAMEN, ED))}), divorce ({oa(SAME(SAMEN, DIV))}), and single-person households ({oa(SAME(SAMEN, ONE))}) retained their direction and credibility, and the spatial effects correlated {N['same_sum']['spearman_spatialOR_vs_main']:.2f} with those of the main model. "
   f"Adding province-by-year effects or the other KCHS items left all estimates within 0.005 of the main model. "
   f"With 1-year lagged covariates, high-risk drinking ({oa(N['lag']['1|'+DR])}) and stress ({oa(N['lag']['1|'+ST])}) were attenuated, whereas university education ({oa(N['lag']['1|'+ED])}) was unchanged. The divorce association was not credible in 2020-2024 ({oa(N['win']['W3_2020-24|'+DIV])}). "
   f"Results were similar across provinces left out, likelihoods, graphs, priors, and influential observations (Supplementary Tables S1-S6), and the manufacturing share was not associated in 2017-2024 ({oa(N['mfg']['plus_manufacturing_2017_2024|mfg'])}). "
   f"For male smoking, university education ({oa(N['male'][ED])}), drinking ({oa(N['male'][DR])}), and divorce ({oa(N['male'][DIV])}) showed the same directions."),
  (f"Two of three negative controls had small credible associations: multicultural marriages ({oa(N['neg']['multicultural_marriage_share'])}) and rear-seat belt use ({oa(N['neg']['rear_seatbelt_wearing_rate'])}); fires were not associated ({oa(N['neg']['fires_per_10000'])}) (Supplementary Table S9). "
   f"Descriptively, district mean smoking prevalence correlated with suicide mortality ratios (Spearman {C['SR|suic_smr']:.2f}) and high-risk drinking prevalence ({C['SR|hdrk_SR']:.2f}), but the residual spatial effects of the main model did not ({C['OR|suic_smr']:.2f} and {C['OR|hdrk_SR']:.2f})."),
 ),
]

DISCUSSION = [
 ("Main findings",
  ("Across 229 Korean districts and 14 years, adult smoking prevalence fell in almost every district, yet the map of where smoking was relatively high changed little. "
   "Districts with fewer university-educated adults kept higher prevalence, and this educational pattern was the strongest and most stable district correlate, present between districts, within districts over time, and in every sensitivity analysis. "
   "Drinking, divorce, living alone, and stress were weaker correlates that met the robustness criteria, whereas the density of bars showed at most a small and unstable association. "
   "The overall spread between high-prevalence and low-prevalence districts was moderate, so these findings describe a persistent gradient rather than a few extreme districts."),
 ),
 ("Interpretation",
  ("The district education gradient mirrors the individual-level inequalities documented in Korea, where declines in smoking were faster in more advantaged groups and relative inequalities widened [@khang2009impact; @chang2019long; @chang2018trends]. "
   "The somewhat stronger gradient in the most recent period, together with the credible post-2020 interaction, suggests that recent declines may have been smaller in districts with fewer university graduates. "
   "The ecological analysis cannot separate composition (more educated residents smoke less) from context (local norms or services), but either reading identifies districts where prevalence remains comparatively high. "
   "The within-district association should be read cautiously, because annual education values were interpolated between censuses and held constant after 2020, so the within-district component reflects census-to-census change rather than annual variation."),
  ("The positive associations with high-risk drinking and stress agree with individual studies of alcohol-tobacco co-use and of distress and smoking [@rathee2026bidirectional; @kassel2003smoking; @fujiwara2018smoking; @cheon2020factors; @simonavicius2025psychological]. "
   "Because these indicators come from the same respondents as the outcome, part of their association could reflect shared reporting tendencies; however, the education, divorce, and household associations were unchanged when the survey-based covariates were removed, which argues against survey artefact as the main explanation for the overall pattern. "
   "The positive association with single-person households reflected differences between districts rather than change within them, because the within-district component was inverse when annual data were available. The associations with divorce and single-person households are consistent with Korean evidence that living alone and being unmarried are associated with smoking "
   "[@lee2020associations; @jang2026living; @cho2008marital; @lim2010influence; @jee2019health] and with a Swedish panel in which marital disruption was associated with smoking uptake and relapse [@nystedt2006marital]; the crude divorce rate, however, measures divorce events rather than the share of divorced residents. "
   "Smoke-free rules were extended in phases to bars and restaurants during the study period [@kim2016impact; @noh2020impacts], which may have weakened any link between bar density and smoking; this was not tested here."),
  ("After the covariates were accounted for, the remaining hotspots included districts in Seoul and Gyeonggi with high average education, and the coldspots were concentrated in the south. "
   "Smoking prevalence was descriptively aligned with suicide mortality and high-risk drinking, whereas the residual spatial effects after adjustment showed little correlation with either; this comparison is descriptive and does not identify shared mechanisms."),
 ),
 ("Strengths and limitations",
  ("Strengths include complete coverage of all districts for 14 years, a model that uses the published sampling variance, and extensive robustness checks covering model choice, space-time interaction, spatial confounding, and survey effects. "
   "Several limitations apply. Smoking was self-reported; cotinine validation in Korea shows substantial underreporting, especially among women [@jungchoi2012hidden; @lee2026trends], and differential underreporting across districts, for example by household composition, could bias the comparison. "
   "The KCHS indicator covers cigarette smoking and does not capture exclusive use of heated tobacco or e-cigarettes, which grew during the period [@kim2024changes]. "
   "Stress and drinking were measured in the same respondents, so shared measurement error remains possible despite the sensitivity analyses, and their attenuation with lagged values suggests that part of these associations is contemporaneous; rear-seat belt use, also a KCHS item, was associated with smoking and was part of one survey-operation index. Two negative controls were weakly associated, with effect sizes similar to those of the weaker covariates; residual district-level confounding, or violation of the negative-control assumptions, could therefore account for associations of that size, whereas the education association was several times larger. "
   "Divorce and household covariates were crude rates, not age-standardized like the outcome, so part of their association may reflect district age structure beyond the controls for the population aged 80 years or older and the sex ratio. Tobacco retail density and district employment were not available for all districts and years. The analysis used a frozen copy of the district database (November 2026) that had been checked cell by cell against the published tables for the variables used here, but not yet released in final audited form. "
   "Finally, the associations are ecological and cannot be interpreted as individual effects [@greenland1989ecological]."),
 ),
]
CONCLUSION = ("District smoking prevalence in Korea declined between 2011 and 2024 but kept a stable geography that followed the educational composition of districts and, more weakly, drinking, stress, divorce, and living alone. "
              "Districts with fewer university graduates are candidates for closer monitoring and for assessment of cessation service needs.")
ACK = "None."
FIGCAP = {
 1: ("District current smoking prevalence and spatial effects, Korea, 2011-2024. (A) Age-sex-standardized prevalence, 2011-2015 mean. (B) 2020-2024 mean, same color scale. "
     "(C) Spatial odds ratios from the model with structural controls only. (D) Spatial odds ratios from the main model with district covariates. Solid outlines, hotspots (posterior probability that the spatial odds ratio exceeds 1 above 0.95); dashed outlines, coldspots (below 0.05)."),
 2: ("Odds ratios of current smoking per 1 standard deviation of district covariates across models. Filled symbols, 95% credible interval excludes 1. "
     "Main, main Fay-Herriot model; Knorr-Held IV, type IV space-time interaction; Spatial+, covariates residualized on spatial eigenvectors; Without survey covariates, model excluding stress and high-risk drinking; Between and Within, district-mean and annual-deviation components."),
}
