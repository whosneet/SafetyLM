# Research Snapshot — Verified AU/NZ WHS Source Map (2026-06-30)

> **What this is.** A web-verified map of the AU/NZ WHS document landscape — regulators,
> current instruments, real URLs, licensing, and currency — produced to ground the **Phase 1
> corpus-manifest build**. Use it as the starting point for the manifest; re-verify before
> finalising.
>
> **How it was produced.** Six parallel web-research agents (by jurisdiction group) + a
> synthesis pass, 30 Jun 2026. ~106 web searches/fetches.
>
> **Trust level.** Jurisdiction identities, current Act/Reg titles, harmonisation status, and
> licensing *regimes* are high-confidence (primary URLs resolved). **Exact code-of-practice
> counts and several licence pages are unverified** because many government sites return
> 403/timeout to automated fetch — these are flagged inline and in §Confidence. **Nothing here
> is final; the manifest build must re-verify each URL.**

---

## Part 1 — Per-jurisdiction source map

### FED — Safe Work Australia (model laws — NOT a regulator)
- **Role:** develops/maintains the *model* WHS laws; enforces nothing. Model text ≠ law until enacted. `pre_harmonisation: n/a`.
- **Model Act:** Model WHS Act (base 2011, point-in-time compilations) — `https://www.safeworkaustralia.gov.au/doc/model-work-health-and-safety-act`
- **Model Regulations:** now badged **Model WHS Regulations 2025** — `https://www.safeworkaustralia.gov.au/doc/model-whs-regulations` · hub `https://www.safeworkaustralia.gov.au/law-and-regulation/model-whs-laws`
- **Model Codes of Practice:** index `https://www.safeworkaustralia.gov.au/law-and-regulation/codes-practice`; per-code `…/doc/model-code-practice-<slug>`. **~28–30 (old "24" is stale); exact count UNVERIFIED (site timed out).**
- **Statistics (on `data.safeworkaustralia.gov.au`):** Key WHS Statistics Australia (2025 ed., Oct 2025) — `https://data.safeworkaustralia.gov.au/insights/key-whs-statistics-australia/latest-release`; Australian Workers' Compensation Statistics; Comparative Performance Monitoring (CPM, 24th ed.); Work-related Traumatic Injury Fatalities DB.
- **Licence:** CC BY 4.0 (Commonwealth); coat-of-arms/third-party excluded. `https://www.safeworkaustralia.gov.au/copyright` (confirm exact string — page timed out).

### NSW — SafeWork NSW · `pre_harmonisation: false`
- **Act:** WHS Act 2011 No 10 (NSW), commenced 1 Jan 2012; in-force 6 Dec 2025 — `https://legislation.nsw.gov.au/view/html/inforce/current/act-2011-010`
- **Regulations:** **WHS Regulation 2025 (SL-2025-0440)**, commenced 22 Aug 2025 — **replaced the WHS Regulation 2017** — `https://legislation.nsw.gov.au/view/whole/html/inforce/2025-10-03/sl-2025-0440`
- **Codes (~28 current WHS):** `https://www.safework.nsw.gov.au/resource-library/list-of-all-codes-of-practice` (the page lists ~47–50 mixing adopted/NSW-only/superseded — use ~28).
- **Licence:** legislation = CC BY 4.0; **regulator codes drift** (older CC BY-NC 3.0 AU, newer CC BY 4.0). **legislation.nsw.gov.au returns 403 to automated fetch.**

### VIC — WorkSafe Victoria · `pre_harmonisation: true` (SOLE non-harmonised) ✓
- **Act:** Occupational Health and Safety Act 2004 (Vic) — NOT a "WHS Act"; in-force v045, 6 Aug 2025 — `https://www.legislation.vic.gov.au/in-force/acts/occupational-health-and-safety-act-2004`
- **Regulations:** OHS Regulations 2017 (SR 22/2017) — **statutory sunset 26 Apr 2027, remake underway** — `https://www.legislation.vic.gov.au/in-force/statutory-rules/occupational-health-and-safety-regulations-2017`
- **Guidance:** **"Compliance codes"** (NOT "codes of practice") — `https://www.worksafe.vic.gov.au/summary-ohs-act-2004-compliance-codes`
- **Licence:** likely CC BY 4.0 — **not verified this round.**

### QLD — Workplace Health and Safety Queensland · `pre_harmonisation: false`
- **Act:** WHS Act 2011 (Qld) (2011-018); current 29 Mar 2026 — `https://www.legislation.qld.gov.au/view/html/inforce/current/act-2011-018`
- **Regulations:** WHS Regulation 2011 (SL 2011-0240) — `https://www.legislation.qld.gov.au/view/pdf/inforce/current/sl-2011-0240`
- **Codes — 57 listed** (retains many state-specific) — `https://www.business.qld.gov.au/running-business/whs/whs-laws/codes-practice`
- **Licence:** likely CC BY 4.0 — not directly verified.

### SA — SafeWork SA · `pre_harmonisation: false`
- **Act:** WHS Act 2012 (SA), v2012.40 — authorised PDF `https://www.legislation.sa.gov.au/_legislation-documents/lz/c/a/work-health-and-safety-act-2012/current/2012.40.auth.pdf`
- **Regulations:** WHS Regulations 2012 (SA). **WHS (High Risk Construction Work) Amendment Regs 2025 commences 1 Jul 2026** (fall height → >2m).
- **Codes:** `https://www.safework.sa.gov.au/resources/codes-of-practice` — **count UNVERIFIED (403)**; SA adopts some Australian Standards as approved codes.
- **Licence:** likely CC BY 4.0 — not verified (403).

### WA — WorkSafe WA · `pre_harmonisation: false` — **HARMONISED since 31 Mar 2022**
- **Act:** **Work Health and Safety Act 2020 (WA)**, commenced **31 Mar 2022**, **repealed the OSH Act 1984** — `https://www.legislation.wa.gov.au/legislation/statutes.nsf/law_s53265.html`
- **Regulations (three 2022 sets):** WHS (General) Regs 2022 — `…law_s53267.html`; WHS (Mines) Regs 2022 — `…law_s53266.html`; WHS (Petroleum and Geothermal Energy Operations) Regs 2022 (no standalone URL established).
- **Codes:** "codes of practice" (model terminology) — `https://www.worksafe.wa.gov.au/work-health-and-safety-laws` (count not established).
- Regulator branding shifted (DMIRS → Dept of Energy, Mines, Industry Regulation and Safety); cite the stable "WorkSafe WA / WorkSafe Commissioner."

### TAS — WorkSafe Tasmania · `pre_harmonisation: false`
- **Act:** **Work Health and Safety Act 2012 (Tas)** (act-2012-001), commenced 1 Jan 2013; authorised 2 Jul 2025. **NOT "WHS Act 2022" — no 2022 Act exists.** — `https://www.legislation.tas.gov.au/view/html/inforce/current/act-2012-001`
- **Industrial manslaughter:** WHS Amendment (Industrial Manslaughter) Act 2024 (Act 15/2024), in force 2 Oct 2024.
- **Regulations:** WHS Regulations 2012 (Tas) — version date UNVERIFIED.
- **Codes:** adopts the model national set; **count UNVERIFIED (~25–28).**

### NT — NT WorkSafe · `pre_harmonisation: false` — **LICENCE OUTLIER**
- **Act:** **Work Health and Safety (National Uniform Legislation) Act 2011 (NT)** (Act 39/2011) — note the "(National Uniform Legislation)" suffix; current reprint REPW025 — `https://legislation.nt.gov.au/Legislation/work-health-and-safety-national-uniform-legislation-act-2011`
- **Regulations:** WHS (NUL) Regulations 2011 (Reg 59/2011); reprint REPW025R1 eff. 28 May 2026.
- **Codes:** `https://worksafe.nt.gov.au/forms-and-resources/codes-of-practice`. 30 Mar 2026: +3 new (RCS/silica, Healthcare & Social Assistance, Fatigue) + 7 revised. **Count ~28–30 (403).**
- **Licence — RESTRICTIVE:** NT legislation is **NOT open/CC** — Crown copyright, fair-dealing only. **Treat NT text as restricted for ingestion absent permission.**

### ACT — WorkSafe ACT · `pre_harmonisation: false`
- **Act:** WHS Act 2011 (ACT) (A2011-35); republication R30, 26 Nov 2025 — `https://www.legislation.act.gov.au/a/2011-35/`
- **Regulations:** WHS Regulation 2011 (ACT) (SL2011-36); republication R47, 29 Nov 2025 (NOT remade as a 2025 instrument) — `https://www.legislation.act.gov.au/sl/2011-36`
- **Codes — 31 approved** — `https://www.worksafe.act.gov.au/laws-and-compliance/codes-of-practice`
- **Licence:** ACT Government content CC BY 4.0.

### CTH — Comcare (federal-jurisdiction workforce) · `pre_harmonisation: false`
- **Act:** WHS Act 2011 (Cth) — regulator page `https://www.comcare.gov.au/scheme-legislation/whs-act`. **Pull the latest in-force compilation from legislation.gov.au — do NOT hard-code the old C2018C00293 compilation ID.**
- **Regulations:** WHS Regulations 2011 (Cth).
- **Codes ~24–26** — `https://www.comcare.gov.au/scheme-legislation/whs-act/codes-of-practice` (count UNVERIFIED).
- **Licence:** legislation.gov.au = CC BY 4.0.

### NZ — WorkSafe New Zealand · `pre_harmonisation: n/a` (separate jurisdiction; modelled-on ≠ harmonised)
- **Act:** **Health and Safety at Work Act 2015 (HSWA)** (2015 No 70); main provisions 4 Apr 2016 — `https://www.legislation.govt.nz/act/public/2015/0070/latest/DLM5976660.html`
- **LIVE REFORM:** Health and Safety at Work Amendment Bill 2026 introduced 8 Feb 2026, in select committee, **NOT yet assented** as of 30 Jun 2026. HSWA-in-force remains operative — re-verify past mid-2026.
- **Regulations (legislation.govt.nz):** General Risk and Workplace Management 2016 (LI 2016/13); Hazardous Substances 2017; Asbestos 2016; Major Hazard Facilities 2016; Worker Engagement/Participation 2016; Adventure Activities 2016; Mining & Quarrying 2016; Petroleum 2016; plus levy/infringement instruments.
- **ACOPs (s.222):** **no clean canonical index — must crawl** `https://www.worksafe.govt.nz/laws-and-regulations/`. Three draft ACOPs were in consultation May 2026.
- **Good Practice Guidelines:** non-binding PDFs on worksafe.govt.nz; **no machine-readable manifest — crawl topic pages.**
- **Licence — TWO regimes (do NOT blanket CC BY):** (a) **NZ legislation = no copyright** (Copyright Act 1994 s.27) → freely reproducible, tag `public-domain-nz-s27`; (b) **WorkSafe guidance = bespoke Crown copyright, free reproduction with attribution, third-party media excluded — NOT CC BY.**

### AIHS OHS Body of Knowledge — **RESTRICTED, proprietary**
- **Location correction:** NOT `aihs.org.au/bok`. It lives at **`https://www.ohsbok.org.au`**; chapter directory `https://www.ohsbok.org.au/bok-chapters/`.
- **Licence:** bespoke proprietary (resembles CC BY-NC-ND but is **not** CC): non-commercial in-house use, attribution, **no modification, no charging**; bulk/commercial reuse needs written AIHS licence. **Treat as RESTRICTED for ingestion/training absent permission.** ~80+ public chapters.

---

## Part 2 — Corrections vs the project's 2024-era assumptions

| # | 2024 assumption | 2026 reality | Confidence |
|---|---|---|---|
| 1 | **WA pre-harmonisation under OSH Act 1984** | **WRONG.** WHS Act 2020 (WA) + 2022 regs commenced 31 Mar 2022; OSH Act 1984 repealed. `pre_harmonisation: false`. | HIGH |
| 2 | VIC still non-harmonised | **CORRECT** (sole non-harmonised; OHS Act 2004; "compliance codes"; regs sunset Apr 2027). | HIGH |
| 3 | TAS = "WHS Act 2022" | **WRONG.** It is the **WHS Act 2012 (Tas)**. | HIGH |
| 4 | NSW WHS Regulation 2017 current | **STALE.** Replaced by **WHS Regulation 2025** (SL-2025-0440). | HIGH |
| 5 | Model WHS Regulations 2011 | **SUPERSEDED** label — now **Model WHS Regulations 2025**. | MED-HIGH |
| 6 | Model code count ~24 | **STALE — now ~28–30.** | MEDIUM |
| 7 | Codes = mere guidance | **Changing 1 Jul 2026:** duty to comply with a code (per-jurisdiction rollout). | MED-HIGH |
| 8 | Industrial manslaughter patchy | **Now in force in ALL nine AU jurisdictions** (QLD'17, NT'20, VIC'20, WA'22, SA'24, Cth'24, NSW'24, TAS'24, ACT). **NZ has none** (HSWA s.47 is top offence). | HIGH |
| 9 | "WHS: How Australia Compares" report | **Not a real current title** — use CPM reports + Comparison of Workers' Comp AU/NZ. | MED-HIGH |
| 10 | AIHS BoK at aihs.org.au/bok, CC-licensed | **WRONG on both** — `ohsbok.org.au`; proprietary non-CC. | HIGH |
| 11 | NZ govt content = CC BY 4.0 | **PARTLY WRONG** — NZ legislation = no copyright (s.27); WorkSafe guidance = bespoke crown-copyright, not CC BY. | HIGH |
| 12 | All AU portals uniformly CC BY 4.0 | **Only Cth + NSW + ACT confirmed.** NT is non-open (restrictive). VIC/QLD/SA/WA/TAS unverified. State codes show per-doc CC drift. | MEDIUM |

---

## Part 3 — Recommended manifest schema/process adjustments

- **`pre_harmonisation`** — default `false`; `true` **only for VIC**; `n/a` for FED-SWA, NZ, AIHS. Hard-assert **WA = false** to kill the stale assumption.
- **`document_type`** enum extensions: `compliance_code` (VIC), `acop` (NZ approved code), `good_practice_guideline` (NZ), `bok_chapter`, `standard` — alongside the docs/03 base types.
- **`title_exact`** — preserve full statutory short title incl. NT's "(National Uniform Legislation)" suffix.
- **`instrument_id`** (SL-2025-0440, A2011-35, act-2012-001), `commencement_date`, `currency_version_date`.
- **`url_verified`** + `verification_method` (`direct_fetch | search_snippet | regulator_index`). **No fabricated URLs.**
- **`license_notes`** values: `CC-BY-4.0 | CC-BY-NC-3.0-AU | crown-copyright-open-attribution | crown-copyright-restricted-NT | nz-legislation-public-domain-s27 | proprietary-restricted-AIHS | iso-restricted`.
- **`ingestable`** (bool) + `ingest_caveat` — **false for AIHS BoK, ISO 45001, NT legislation/codes; non-commercial-only for CC BY-NC items.**
- **Currency default:** corpus `as_of_date = 2026-06-30`; anything without a verified currency date → `VERIFY`/`UNVERIFIED`, never guessed. Prefer each register's `/latest/` view over a pinned compilation ID.
- **Counts:** record `count_source` + `count_verified` per jurisdiction (firm: QLD 57, ACT 31; the rest are ranges/unverified).
- **403/timeout handling:** legislation.nsw/.sa/.gov.au, AustLII, NT WorkSafe, SWA `www` block automated fetch — retry / use a browser-level fetch (the `/browse` skill) / fall back to mirrors; **never treat a 403 as "URL invalid."**

---

## Confidence & gaps

**High confidence:** WA harmonisation (31 Mar 2022, OSH 1984 repealed); VIC sole non-harmonised; TAS = WHS Act 2012; NSW Reg 2025; ACT Act/Reg/31 codes; NZ HSWA identity + s.27 no-copyright + bespoke WorkSafe licence + 2026 Bill not yet assented; AIHS location + proprietary licence; ISO 45001 restricted; industrial manslaughter across all 9 AU jurisdictions; QLD 57 codes.

**Thin / unverified — confirm with a browser-level fetch before finalising:** exact code counts (SWA ~28–30, NT, SA, TAS, Cth); Model WHS Regulations "2025" label + the 1 Jul 2026 duty-to-comply transition; the current Cth Act compilation ID; TAS WHS Regulations version date; licence pages for VIC/QLD/SA/WA/TAS (assumed CC BY 4.0 — do **not** assume); NZ ACOP/GPG inventories (no clean index — crawl).

**Fast-moving:** NZ HSW Amendment Bill 2026 (pending assent); SA HRCW Amendment Regs (1 Jul 2026); VIC OHS Regs remake (sunset Apr 2027); codes duty-to-comply rollout from 1 Jul 2026.
