---
id: step-02
trail: 2026-10-29-seed-reporting
parent: step-01
direction: citations
query: none
inputs: W2970283086, step-01#15
input_versions: W2970283086, W2754517384+W2963120839
filters: exclude-retracted; top 200 citing works per input newest
provider: openalex
fetched_at: 2026-10-29T08:00:37Z
pool: 581
candidates: 10
excluded: beyond-limit=571
supplement: none
candidates_sha256: 4f250d03a804eeeba173974e3fde46ee5ae07193fddb96f8df556db333b158a7
proposed: none
chosen: none
chosen_by: none
saved: none
agent: Claude
---

# step-02 · citations ← step-01

Inputs: W2970283086, step-01#15
OpenAlex works used: W2970283086, W2754517384+W2963120839

`links` = how many inputs this paper connects to. `venue` shows the published version; `preprint-only` means no published version was found.

## Candidates

| # | title | year | venue | links | cited by | library |
|---|---|---|---|---|---|---|
| 1 | Reproducibility of the NeurIPS 2020 Black-Box Optimization Challenge: Re-evaluating Competition Submissions | 2026 | ACM Conference on Reproducibility and Replicability (ACM REP) | 2 | 0 | - |
| 2 | Measuring deep learning performance - an empirical study of performance distributions across architectures and tasks | 2026 | Scientific Reports | 2 | 1 | - |
| 3 | Evaluating deep transfer learning for whole-brain cognitive decoding | 2023 | Journal of the Franklin Institute | 2 | 12 | - |
| 4 | Challenges for cognitive decoding using deep learning methods | 2021 | preprint-only | 2 | 4 | - |
| 5 | Hyperparameter Optimization Is Deceiving Us, and How to Stop It | 2021 | neural information processing systems | 2 | 12 | - |
| 6 | Problems and opportunities in training deep learning software systems | 2020 | IEEE/ACM International Conference on Automated Software Engineering (ASE) | 2 | 100 | - |
| 7 | A Training-Free Symbolic Baseline for Interactive Medical Diagnosis: Automatic Rule-Slot Derivation and Weighted Evidence Combination | 2026 | Journal of Computing Theories and Applications | 1 | 0 | - |
| 8 | Benchmark-path fidelity in parallel robot-policy evaluation: a CALVIN case study | 2026 | The Journal of Supercomputing | 1 | 0 | - |
| 9 | Comparison of Forecasts From Neural Network and Econometric Models . | 2026 | Economic Policy | 1 | 0 | - |
| 10 | PPO-ReLA: Residual Link Adaptation for UAV LoRa Backhaul Under Power-Line Interference | 2026 | Electronics | 1 | 0 | - |

## Candidate records

Written by `infra/library.py`. Do not edit — research-lint checks `candidates_sha256`.

```json
[
 {
  "n": 1,
  "title": "Reproducibility of the NeurIPS 2020 Black-Box Optimization Challenge: Re-evaluating Competition Submissions",
  "year": 2026,
  "authors": [
   "Ivan Raytchinov",
   "Marie Anastacio",
   "Anja Jankovič"
  ],
  "n_authors": 5,
  "venue": "ACM Conference on Reproducibility and Replicability (ACM REP)",
  "venue_type": "conference",
  "doi": "10.1145/3820002.3828590",
  "arxiv": "",
  "openalex": [
   "W7214229640"
  ],
  "cited_by": 0,
  "connections": 2,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W7214229640",
    "kind": "published",
    "doi": "10.1145/3820002.3828590",
    "arxiv": "",
    "venue": "ACM Conference on Reproducibility and Replicability (ACM REP)",
    "venue_type": "conference",
    "year": 2026,
    "cited_by": 0,
    "is_retracted": false,
    "authors": [
     "A5000680322",
     "A5022601333",
     "A5025342513",
     "A5079238593",
     "A5152606064",
     "anastacio|m",
     "anja|j",
     "gundersen|o",
     "holger|h",
     "hoos|h",
     "ivan|r",
     "jankovic|a",
     "marie|a",
     "odd|g",
     "raytchinov|i"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 2,
  "title": "Measuring deep learning performance - an empirical study of performance distributions across architectures and tasks",
  "year": 2026,
  "authors": [
   "Kevin L. Coakley",
   "Odd Erik Gundersen"
  ],
  "n_authors": 2,
  "venue": "Scientific Reports",
  "venue_type": "journal",
  "doi": "10.1038/s41598-026-49656-z",
  "arxiv": "",
  "openalex": [
   "W7160135851"
  ],
  "cited_by": 1,
  "connections": 2,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W7160135851",
    "kind": "published",
    "doi": "10.1038/s41598-026-49656-z",
    "arxiv": "",
    "venue": "Scientific Reports",
    "venue_type": "journal",
    "year": 2026,
    "cited_by": 1,
    "is_retracted": false,
    "authors": [
     "A5022601333",
     "A5103237919",
     "coakley|k",
     "gundersen|o",
     "kevin|c",
     "odd|g"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 3,
  "title": "Evaluating deep transfer learning for whole-brain cognitive decoding",
  "year": 2023,
  "authors": [
   "Armin W. Thomas",
   "Ulman Lindenberger",
   "Wojciech Samek"
  ],
  "n_authors": 4,
  "venue": "Journal of the Franklin Institute",
  "venue_type": "journal",
  "doi": "10.1016/j.jfranklin.2023.07.015",
  "arxiv": "2111.01562",
  "openalex": [
   "W3210724280"
  ],
  "cited_by": 12,
  "connections": 2,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W3210724280",
    "kind": "published",
    "doi": "10.1016/j.jfranklin.2023.07.015",
    "arxiv": "2111.01562",
    "venue": "Journal of the Franklin Institute",
    "venue_type": "journal",
    "year": 2023,
    "cited_by": 12,
    "is_retracted": false,
    "authors": [
     "A5026451495",
     "A5070255304",
     "A5084761067",
     "A5107838719",
     "armin|t",
     "klaus|m",
     "lindenberger|u",
     "muller|k",
     "samek|w",
     "thomas|a",
     "ulman|l",
     "wojciech|s"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 4,
  "title": "Challenges for cognitive decoding using deep learning methods",
  "year": 2021,
  "authors": [
   "Armin W. Thomas",
   "Christopher Ré",
   "Russell Alan Poldrack"
  ],
  "n_authors": 3,
  "venue": "preprint-only",
  "venue_type": "preprint",
  "doi": "",
  "arxiv": "2108.06896",
  "openalex": [
   "W3194016805"
  ],
  "cited_by": 4,
  "connections": 2,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W3194016805",
    "kind": "preprint",
    "doi": "",
    "arxiv": "2108.06896",
    "venue": "",
    "venue_type": "",
    "year": 2021,
    "cited_by": 4,
    "is_retracted": false,
    "authors": [
     "A5046868253",
     "A5070255304",
     "A5103852640",
     "armin|t",
     "christopher|r",
     "poldrack|r",
     "re|c",
     "russell|p",
     "thomas|a"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 5,
  "title": "Hyperparameter Optimization Is Deceiving Us, and How to Stop It",
  "year": 2021,
  "authors": [
   "A. Feder Cooper",
   "Yucheng Lu",
   "Forde, Jessica Zosa"
  ],
  "n_authors": 4,
  "venue": "neural information processing systems",
  "venue_type": "conference",
  "doi": "",
  "arxiv": "2102.03034",
  "openalex": [
   "W3128997905"
  ],
  "cited_by": 12,
  "connections": 2,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W3128997905",
    "kind": "published",
    "doi": "",
    "arxiv": "2102.03034",
    "venue": "neural information processing systems",
    "venue_type": "conference",
    "year": 2021,
    "cited_by": 12,
    "is_retracted": false,
    "authors": [
     "A5041869459",
     "A5064217008",
     "A5066555129",
     "a|c",
     "christopher|d",
     "cooper|a",
     "de|c",
     "forde|z",
     "lu|y",
     "yucheng|l",
     "zosa|f"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 6,
  "title": "Problems and opportunities in training deep learning software systems",
  "year": 2020,
  "authors": [
   "Hung Viet Pham",
   "Shangshu Qian",
   "Jiannan Wang"
  ],
  "n_authors": 8,
  "venue": "IEEE/ACM International Conference on Automated Software Engineering (ASE)",
  "venue_type": "conference",
  "doi": "10.1145/3324884.3416545",
  "arxiv": "",
  "openalex": [
   "W3122184684"
  ],
  "cited_by": 100,
  "connections": 2,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W3122184684",
    "kind": "published",
    "doi": "10.1145/3324884.3416545",
    "arxiv": "",
    "venue": "IEEE/ACM International Conference on Automated Software Engineering (ASE)",
    "venue_type": "conference",
    "year": 2020,
    "cited_by": 100,
    "is_retracted": false,
    "authors": [
     "A5002648627",
     "A5005636247",
     "A5009306083",
     "A5032731074",
     "A5063985157",
     "A5101612061",
     "A5101850961",
     "A5104247245",
     "hung|p",
     "jiannan|w",
     "jonathan|r",
     "lin|t",
     "lutellier|t",
     "nachiappan|n",
     "nagappan|n",
     "pham|h",
     "qian|s",
     "rosenthal|j",
     "shangshu|q",
     "tan|l",
     "thibaud|l",
     "wang|j",
     "yaoliang|y",
     "yu|y"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 7,
  "title": "A Training-Free Symbolic Baseline for Interactive Medical Diagnosis: Automatic Rule-Slot Derivation and Weighted Evidence Combination",
  "year": 2026,
  "authors": [
   "Naufal Denta Elsatya Nugraha",
   "Dhendra Marutho",
   "Muhammad Sam’an"
  ],
  "n_authors": 5,
  "venue": "Journal of Computing Theories and Applications",
  "venue_type": "journal",
  "doi": "10.62411/jcta.17677",
  "arxiv": "",
  "openalex": [
   "W7223563726"
  ],
  "cited_by": 0,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W7223563726",
    "kind": "published",
    "doi": "10.62411/jcta.17677",
    "arxiv": "",
    "venue": "Journal of Computing Theories and Applications",
    "venue_type": "journal",
    "year": 2026,
    "cited_by": 0,
    "is_retracted": false,
    "authors": [
     "A5016969382",
     "A5019714454",
     "A5066078934",
     "A5066093413",
     "A5119204824",
     "an|m",
     "de|s",
     "dhendra|m",
     "marutho|d",
     "muhammad|a",
     "naufal|n",
     "nugraha|n",
     "sarasjati|w",
     "setiadi|d",
     "wendy|s"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 8,
  "title": "Benchmark-path fidelity in parallel robot-policy evaluation: a CALVIN case study",
  "year": 2026,
  "authors": [
   "Yuanzhi He",
   "Qiming Wang",
   "Jiayu Xu"
  ],
  "n_authors": 3,
  "venue": "The Journal of Supercomputing",
  "venue_type": "journal",
  "doi": "10.1007/s11227-026-08965-w",
  "arxiv": "",
  "openalex": [
   "W7223474091"
  ],
  "cited_by": 0,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W7223474091",
    "kind": "published",
    "doi": "10.1007/s11227-026-08965-w",
    "arxiv": "",
    "venue": "The Journal of Supercomputing",
    "venue_type": "journal",
    "year": 2026,
    "cited_by": 0,
    "is_retracted": false,
    "authors": [
     "A5040823262",
     "A5134862339",
     "A5153486771",
     "he|y",
     "jiayu|x",
     "qiming|w",
     "wang|q",
     "xu|j",
     "yuanzhi|h"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 9,
  "title": "Comparison of Forecasts From Neural Network and Econometric Models .",
  "year": 2026,
  "authors": [
   "D. A. Koloskov",
   "M.Yu. Turuntseva",
   "Vadim Zyamalov"
  ],
  "n_authors": 3,
  "venue": "Economic Policy",
  "venue_type": "journal",
  "doi": "10.18288/1994-5124-2026-5-84-111",
  "arxiv": "",
  "openalex": [
   "W7223344040"
  ],
  "cited_by": 0,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W7223344040",
    "kind": "published",
    "doi": "10.18288/1994-5124-2026-5-84-111",
    "arxiv": "",
    "venue": "Economic Policy",
    "venue_type": "journal",
    "year": 2026,
    "cited_by": 0,
    "is_retracted": false,
    "authors": [
     "A5054848264",
     "A5071690355",
     "A5159318494",
     "d|k",
     "koloskov|d",
     "m|t",
     "turuntseva|m",
     "vadim|z",
     "zyamalov|v"
    ]
   }
  ],
  "library": ""
 },
 {
  "n": 10,
  "title": "PPO-ReLA: Residual Link Adaptation for UAV LoRa Backhaul Under Power-Line Interference",
  "year": 2026,
  "authors": [
   "Long Luo",
   "Duo Wang",
   "Ming Chen"
  ],
  "n_authors": 5,
  "venue": "Electronics",
  "venue_type": "journal",
  "doi": "10.3390/electronics15204823",
  "arxiv": "",
  "openalex": [
   "W7222984876"
  ],
  "cited_by": 0,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W7222984876",
    "kind": "published",
    "doi": "10.3390/electronics15204823",
    "arxiv": "",
    "venue": "Electronics",
    "venue_type": "journal",
    "year": 2026,
    "cited_by": 0,
    "is_retracted": false,
    "authors": [
     "A5015538526",
     "A5034801072",
     "A5073448025",
     "A5113750738",
     "A5159042329",
     "chen|m",
     "duo|w",
     "fubao|j",
     "jin|f",
     "long|l",
     "luo|l",
     "ming|c",
     "wang|d",
     "yunlong|z",
     "zhao|y"
    ]
   }
  ],
  "library": ""
 }
]
```
