---
aliases:
- Omalizumab
- Xolair
- Anti-IgE
analyzed: '2026-11-15'
assurance: sonnet
name: Omalizumab (Xolair, injected)
slug: omalizumab
status: published
tier: good
type: ingredient
updated: '2026-11-15'
---

An injected anti-IgE antibody, and the standard next step when antihistamines fail for chronic hives. **Bottom line:** the evidence is unusually good for something on this site, with twelve randomised trials behind it and a clear dose, and it is still a monthly injection for a condition that is miserable rather than dangerous. Three of its four labelled uses are not skin conditions at all. The condition is at [[chronic-spontaneous-urticaria]] and the drugs it follows at [[second-generation-h1-antihistamines]].

> **The dose is where the evidence is.** A 2025 meta-analysis pooled "Twelve RCTs involving 2,738 participants (2,090 in omalizumab groups, 648 in placebo)" across 75, 150, 300 and 600 mg.[^meta] Pooled across all doses the result is real but imprecise, an odds ratio of "3.29, 95% CI:1.16-9.38" for reaching a 7-day Urticaria Activity Score under 6. At 300 mg specifically it is both larger and far tighter, "7.60, 95% CI:5.44-10.62".[^meta] Reading the headline number without the dose breakdown understates how well the right dose does and overstates how well the wrong one does.

## The Rubric

- **Effect size: large, at 300 mg.** Against placebo the 300 mg dose reduced UAS7 by a mean difference of "12.20, 95% CI:9.65-14.76", itch severity by "5.26, 95% CI:4.42-5.36", and hive count by "6.83, 95% CI:5.73-7.94", all at P < 0.001.[^meta] Quality of life improved too, by "3.26, 95% CI:1.78-4.73" on the DLQI.[^meta]
- **Evidence quality: good.** Twelve randomised placebo-controlled trials, a labelled FDA indication, and a consistent dose-response. That is a stronger file than almost anything else graded here.
- **Why `good` and not `best`.** It is second line by its own label, it is injected rather than applied, adverse events were significantly more frequent than placebo at an odds ratio of "1.24, 95% CI:1.04-1.49", and the all-dose pooled estimate spans nearly an order of magnitude.[^meta] The authors' own closing note is that "Further studies are needed to confirm long-term safety."[^meta]
- **The label is narrow, and deliberately so.** Xolair is indicated for "Chronic spontaneous urticaria (CSU) in adults and adolescents 12 years of age and older who remain symptomatic despite H1 antihistamine treatment", with an explicit Limitation of Use: "Not indicated for other forms of urticaria."[^label] If your hives have a known physical trigger, this label does not cover you.
- **It is mostly not a skin drug.** The same label covers moderate to severe persistent asthma, nasal polyps and IgE-mediated food allergy; chronic spontaneous urticaria is indication 1.4 of four.[^label] It appears on this site because of one indication out of four.
- **Route: subcutaneous injection.** Nothing here is topical, and the comparison class is [[dupilumab]] rather than anything in a bottle.[^label]

## The Evidence

One meta-analysis, read from its abstract, plus the FDA label. The analysis searched PubMed, the Cochrane Library and Embase for randomised trials comparing omalizumab with placebo, and assessed UAS7, itch severity, hive count, DLQI and adverse events.[^meta]

What this page does not have is durability. The pooled trials report what happens during treatment, not how long people stay on it or what happens when they stop, and that question has its own literature which is not read here.

> **Bottom line.** When antihistamines have failed, this is the option with real numbers behind it. Graded `good` rather than `best` because it is injected, second line, and slightly worse tolerated than placebo.

## See Also

- [[chronic-spontaneous-urticaria]] for the condition and the treatment ladder
- [[second-generation-h1-antihistamines]], the first-line class this follows
- [[dupilumab]], the other injected biologic covered here

## Sources

[^meta]: Zhang W, Cao X, Liu L. "Efficacy and safety of Omalizumab in the treatment of CSU: a meta-analysis of a randomized controlled trial." Archives of Dermatological Research. 2025 May 29;317(1):785. doi: 10.1007/s00403-025-04283-y. PMID 40439896. Authors are at the Departments of Dermatology, Wuhai People's Hospital and Bayannur Hospital, Inner Mongolia, China; the first two contributed equally. PubMed abstract read in full on 2026-11-15. Databases searched were PubMed, the Cochrane Library and Embase, for randomised controlled trials comparing omalizumab with placebo. Quotations and figures verified verbatim against the abstract: "Twelve RCTs involving 2,738 participants (2,090 in omalizumab groups, 648 in placebo)"; the all-dose odds ratio "3.29, 95% CI:1.16-9.38"; the 300 mg odds ratio "7.60, 95% CI:5.44-10.62"; the 300 mg mean differences for UAS7 "12.20, 95% CI:9.65-14.76", ISS "5.26, 95% CI:4.42-5.36" and hive count "6.83, 95% CI:5.73-7.94"; the DLQI "3.26, 95% CI:1.78-4.73"; the adverse-event odds ratio "1.24, 95% CI:1.04-1.49"; and "Further studies are needed to confirm long-term safety." The doses analysed were 75, 150, 300 and 600 mg. Only the PubMed abstract was accessed, not the full article, so the twelve included trials were not read individually, no risk-of-bias rating is reported here, and no claim is made about which trials they were. https://pubmed.ncbi.nlm.nih.gov/40439896/ (accessed 2026-11-15)
[^label]: openFDA drug label API, XOLAIR (omalizumab), label effective 2026-08-13, read 2026-11-15. Route is recorded as SUBCUTANEOUS. Quotations verified verbatim from the Indications and Usage section: "Chronic spontaneous urticaria (CSU) in adults and adolescents 12 years of age and older who remain symptomatic despite H1 antihistamine treatment" at section 1.4, and the Limitation of Use "Not indicated for other forms of urticaria." The same section lists asthma in patients 6 years and older, nasal polyps in adults 18 and older, and IgE-mediated food allergy in patients aged 1 year and older, which is the basis for the statement that chronic spontaneous urticaria is one indication of four. No dosing, warning or contraindication detail is drawn from the label here. https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22xolair%22 (accessed 2026-11-15)