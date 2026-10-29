---
id: step-01
trail: 2026-10-29-seed-reporting
parent: none
direction: references
query: none
inputs: W2970283086
input_versions: W2970283086
filters: exclude-retracted; references also from crossref, semanticscholar
provider: openalex
fetched_at: 2026-10-29T07:59:29Z
pool: 42
candidates: 15
excluded: beyond-limit=27
supplement: crossref has no reference list; semanticscholar listed 44 (8 without DOI); added 1 not in OpenAlex's list, 1 not found in OpenAlex
candidates_sha256: a1ca4be313c7384a693d739704a71bddef2cf08aa0d7d28e63dda02e6f02c80f
proposed: none
chosen: 15
chosen_by: human
saved: 15=L0001
agent: Claude
---

# step-01 · references

Inputs: W2970283086
OpenAlex works used: W2970283086
Other reference lists: crossref has no reference list; semanticscholar listed 44 (8 without DOI); added 1 not in OpenAlex's list, 1 not found in OpenAlex. Each candidate's `found_by` says which list named it.

`links` = how many inputs this paper connects to. `venue` shows the published version; `preprint-only` means no published version was found.
`⚠` (1) = dated more than a year after the paper citing it: a wrong link or a wrong year. Check before saving.

## Candidates

| # | title | year | venue | links | cited by | library |
|---|---|---|---|---|---|---|
| 1 | BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding | 2019 | Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT) | 1 | 93195 | - |
| 2 | An Introduction to the Bootstrap | 1994 | Chapman & Hall/CRC eBooks | 1 | 40490 | - |
| 3 | Glove: Global Vectors for Word Representation | 2014 | Conference on Empirical Methods in Natural Language Processing (EMNLP) | 1 | 33599 | - |
| 4 | Deep Contextualized Word Representations | 2018 | Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT) | 1 | 11991 | - |
| 5 | Why Most Published Research Findings Are False | 2005 | PLoS Medicine | 1 | 10473 | - |
| 6 | Random search for hyper-parameter optimization | 2012 | preprint-only | 1 | 8011 | - |
| 7 | Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank | 2013 | Conference on Empirical Methods in Natural Language Processing (EMNLP) | 1 | 6876 | - |
| 8 | SQuAD: 100,000+ Questions for Machine Comprehension of Text | 2016 | Conference on Empirical Methods in Natural Language Processing (EMNLP) | 1 | 6204 | - |
| 9 | GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding | 2018 | BlackboxNLP Workshop on Analyzing and Interpreting Neural Networks for NLP (BlackboxNLP) | 1 | 5844 | - |
| 10 | Why Most Published Research Findings Are False | 2005 | CHANCE | 1 | 4702 | - |
| 11 | Energy and Policy Considerations for Deep Learning in NLP | 2019 | Annual Meeting of the Association for Computational Linguistics (ACL) | 1 | 3671 | - |
| 12 | Model Cards for Model Reporting | 2019 | ACM Conference on Fairness, Accountability, and Transparency (FAccT) | 1 | 2661 | - |
| 13 | Datasheets for datasets | 2021 ⚠ | Communications of the ACM | 1 | 2459 | - |
| 14 | An Introduction to the Bootstrap | 1995 | Technometrics | 1 | 2096 | - |
| 15 | Deep Reinforcement Learning That Matters | 2018 | Proceedings of the AAAI Conference on Artificial Intelligence | 1 | 2023 | - |

## Candidate records

Written by `infra/library.py`. Do not edit — research-lint checks `candidates_sha256`.

```json
[
 {
  "n": 1,
  "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
  "year": 2019,
  "authors": [
   "Jacob Devlin",
   "Ming-Wei Chang",
   "Kenton Lee"
  ],
  "n_authors": 4,
  "venue": "Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)",
  "venue_type": "conference",
  "doi": "10.18653/v1/n19-1423",
  "arxiv": "1810.04805",
  "openalex": [
   "W2963341956",
   "W2896457183"
  ],
  "cited_by": 93195,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2963341956",
    "kind": "published",
    "doi": "10.18653/v1/n19-1423",
    "arxiv": "",
    "venue": "Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)",
    "venue_type": "conference",
    "year": 2019,
    "cited_by": 48455,
    "is_retracted": false,
    "authors": [
     "A5053947885",
     "A5057457287",
     "A5081862885",
     "chang|m",
     "devlin|j",
     "jacob|d",
     "kenton|l",
     "kristina|t",
     "lee|k",
     "ming|c",
     "toutanova|k"
    ]
   },
   {
    "openalex": "W2896457183",
    "kind": "preprint",
    "doi": "",
    "arxiv": "1810.04805",
    "venue": "",
    "venue_type": "",
    "year": 2018,
    "cited_by": 44740,
    "is_retracted": false,
    "authors": [
     "A5057457287",
     "A5127838054",
     "A5159833220",
     "A5159955724",
     "chang|m",
     "devlin|j",
     "jacob|d",
     "kenton|l",
     "kristina|t",
     "lee|k",
     "ming|c",
     "toutanova|k"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 2,
  "title": "An Introduction to the Bootstrap",
  "year": 1994,
  "authors": [
   "Bradley Efron",
   "Robert John Tibshirani"
  ],
  "n_authors": 2,
  "venue": "Chapman & Hall/CRC eBooks",
  "venue_type": "other",
  "doi": "10.1201/9780429246593",
  "arxiv": "",
  "openalex": [
   "W1995945562"
  ],
  "cited_by": 40490,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W1995945562",
    "kind": "published",
    "doi": "10.1201/9780429246593",
    "arxiv": "",
    "venue": "Chapman & Hall/CRC eBooks",
    "venue_type": "other",
    "year": 1994,
    "cited_by": 40490,
    "is_retracted": false,
    "authors": [
     "A5027340494",
     "A5108567924",
     "bradley|e",
     "efron|b",
     "robert|t",
     "tibshirani|r"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex"
  ],
  "after_input": false
 },
 {
  "n": 3,
  "title": "Glove: Global Vectors for Word Representation",
  "year": 2014,
  "authors": [
   "Jeffrey Pennington",
   "Richard Socher",
   "Christopher D. Manning"
  ],
  "n_authors": 3,
  "venue": "Conference on Empirical Methods in Natural Language Processing (EMNLP)",
  "venue_type": "conference",
  "doi": "10.3115/v1/d14-1162",
  "arxiv": "",
  "openalex": [
   "W2250539671"
  ],
  "cited_by": 33599,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2250539671",
    "kind": "published",
    "doi": "10.3115/v1/d14-1162",
    "arxiv": "",
    "venue": "Conference on Empirical Methods in Natural Language Processing (EMNLP)",
    "venue_type": "conference",
    "year": 2014,
    "cited_by": 33599,
    "is_retracted": false,
    "authors": [
     "A5010225522",
     "A5046006076",
     "A5059955534",
     "christopher|m",
     "jeffrey|p",
     "manning|c",
     "pennington|j",
     "richard|s",
     "socher|r"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 4,
  "title": "Deep Contextualized Word Representations",
  "year": 2018,
  "authors": [
   "Matthew E. Peters",
   "Mark Neumann",
   "Mohit Iyyer"
  ],
  "n_authors": 7,
  "venue": "Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)",
  "venue_type": "conference",
  "doi": "10.18653/v1/n18-1202",
  "arxiv": "1802.05365",
  "openalex": [
   "W2787560479"
  ],
  "cited_by": 11991,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2787560479",
    "kind": "published",
    "doi": "10.18653/v1/n18-1202",
    "arxiv": "1802.05365",
    "venue": "Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)",
    "venue_type": "conference",
    "year": 2018,
    "cited_by": 11991,
    "is_retracted": false,
    "authors": [
     "A5020085226",
     "A5035088083",
     "A5067919401",
     "A5081862885",
     "A5082767919",
     "A5101509445",
     "christopher|c",
     "clark|c",
     "gardner|m",
     "iyyer|m",
     "kenton|l",
     "lee|k",
     "luke|z",
     "mark|n",
     "matthew|p",
     "matt|g",
     "mohit|i",
     "neumann|m",
     "peters|m",
     "zettlemoyer|l"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 5,
  "title": "Why Most Published Research Findings Are False",
  "year": 2005,
  "authors": [
   "John P. A. Ioannidis"
  ],
  "n_authors": 1,
  "venue": "PLoS Medicine",
  "venue_type": "journal",
  "doi": "10.1371/journal.pmed.0020124",
  "arxiv": "",
  "openalex": [
   "W2144981148"
  ],
  "cited_by": 10473,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2144981148",
    "kind": "published",
    "doi": "10.1371/journal.pmed.0020124",
    "arxiv": "",
    "venue": "PLoS Medicine",
    "venue_type": "journal",
    "year": 2005,
    "cited_by": 10473,
    "is_retracted": false,
    "authors": [
     "A5070446713",
     "ioannidis|j",
     "john|i"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex"
  ],
  "after_input": false
 },
 {
  "n": 6,
  "title": "Random search for hyper-parameter optimization",
  "year": 2012,
  "authors": [
   "James Bergstra",
   "Yoshua Bengio",
   "Léon Bottou"
  ],
  "n_authors": 3,
  "venue": "preprint-only",
  "venue_type": "preprint",
  "doi": "",
  "arxiv": "",
  "openalex": [
   "W2097998348"
  ],
  "cited_by": 8011,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2097998348",
    "kind": "preprint",
    "doi": "",
    "arxiv": "",
    "venue": "",
    "venue_type": "",
    "year": 2012,
    "cited_by": 8011,
    "is_retracted": false,
    "authors": [
     "A5019206666",
     "A5057264590",
     "A5086198262",
     "bengio|y",
     "bergstra|j",
     "bottou|l",
     "james|b",
     "leon|b",
     "yoshua|b"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex"
  ],
  "after_input": false
 },
 {
  "n": 7,
  "title": "Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank",
  "year": 2013,
  "authors": [
   "Richard Socher",
   "Alex Perelygin",
   "Jean Y. Wu"
  ],
  "n_authors": 7,
  "venue": "Conference on Empirical Methods in Natural Language Processing (EMNLP)",
  "venue_type": "conference",
  "doi": "10.18653/v1/d13-1170",
  "arxiv": "",
  "openalex": [
   "W2251939518"
  ],
  "cited_by": 6876,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2251939518",
    "kind": "published",
    "doi": "10.18653/v1/d13-1170",
    "arxiv": "",
    "venue": "Conference on Empirical Methods in Natural Language Processing (EMNLP)",
    "venue_type": "conference",
    "year": 2013,
    "cited_by": 6876,
    "is_retracted": false,
    "authors": [
     "A5023259221",
     "A5042601761",
     "A5046006076",
     "A5047624579",
     "A5051147845",
     "A5059955534",
     "A5111979273",
     "alex|p",
     "a|n",
     "christopher|m",
     "christopher|p",
     "chuang|j",
     "jason|c",
     "jean|w",
     "manning|c",
     "ng|a",
     "perelygin|a",
     "potts|c",
     "richard|s",
     "socher|r",
     "wu|j"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 8,
  "title": "SQuAD: 100,000+ Questions for Machine Comprehension of Text",
  "year": 2016,
  "authors": [
   "Pranav Rajpurkar",
   "Jian Zhang",
   "Konstantin Lopyrev"
  ],
  "n_authors": 4,
  "venue": "Conference on Empirical Methods in Natural Language Processing (EMNLP)",
  "venue_type": "conference",
  "doi": "10.18653/v1/d16-1264",
  "arxiv": "",
  "openalex": [
   "W2963748441"
  ],
  "cited_by": 6204,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2963748441",
    "kind": "published",
    "doi": "10.18653/v1/d16-1264",
    "arxiv": "",
    "venue": "Conference on Empirical Methods in Natural Language Processing (EMNLP)",
    "venue_type": "conference",
    "year": 2016,
    "cited_by": 6204,
    "is_retracted": false,
    "authors": [
     "A5001094226",
     "A5025255782",
     "A5060537142",
     "A5100409994",
     "jian|z",
     "konstantin|l",
     "liang|p",
     "lopyrev|k",
     "percy|l",
     "pranav|r",
     "rajpurkar|p",
     "zhang|j"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 9,
  "title": "GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding",
  "year": 2018,
  "authors": [
   "Alex Wang",
   "Amanpreet Singh",
   "Julian Michael"
  ],
  "n_authors": 6,
  "venue": "BlackboxNLP Workshop on Analyzing and Interpreting Neural Networks for NLP (BlackboxNLP)",
  "venue_type": "conference",
  "doi": "10.18653/v1/w18-5446",
  "arxiv": "",
  "openalex": [
   "W2923014074",
   "W2963310665"
  ],
  "cited_by": 5844,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2923014074",
    "kind": "published",
    "doi": "10.18653/v1/w18-5446",
    "arxiv": "",
    "venue": "BlackboxNLP Workshop on Analyzing and Interpreting Neural Networks for NLP (BlackboxNLP)",
    "venue_type": "conference",
    "year": 2018,
    "cited_by": 4223,
    "is_retracted": false,
    "authors": [
     "A5010396788",
     "A5024311574",
     "A5072681909",
     "A5100672985",
     "A5103982993",
     "A5112713734",
     "alex|w",
     "amanpreet|s",
     "bowman|s",
     "felix|h",
     "hill|f",
     "julian|m",
     "levy|o",
     "michael|j",
     "omer|l",
     "samuel|b",
     "singh|a",
     "wang|a"
    ]
   },
   {
    "openalex": "W2963310665",
    "kind": "published",
    "doi": "",
    "arxiv": "",
    "venue": "International Conference on Learning Representations",
    "venue_type": "conference",
    "year": 2018,
    "cited_by": 1621,
    "is_retracted": false,
    "authors": [
     "A5010396788",
     "A5024311574",
     "A5072681909",
     "A5100672985",
     "A5100783908",
     "A5112713734",
     "alex|w",
     "amanpreet|s",
     "bowman|s",
     "felix|h",
     "hill|f",
     "julian|m",
     "levy|o",
     "michael|j",
     "omer|l",
     "samuel|b",
     "singh|a",
     "wang|a"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 10,
  "title": "Why Most Published Research Findings Are False",
  "year": 2005,
  "authors": [
   "John P. A. Ioannidis"
  ],
  "n_authors": 1,
  "venue": "CHANCE",
  "venue_type": "journal",
  "doi": "10.1080/09332480.2005.10722754",
  "arxiv": "",
  "openalex": [
   "W2331384579"
  ],
  "cited_by": 4702,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2331384579",
    "kind": "published",
    "doi": "10.1080/09332480.2005.10722754",
    "arxiv": "",
    "venue": "CHANCE",
    "venue_type": "journal",
    "year": 2005,
    "cited_by": 4702,
    "is_retracted": false,
    "authors": [
     "A5070446713",
     "ioannidis|j",
     "john|i"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 11,
  "title": "Energy and Policy Considerations for Deep Learning in NLP",
  "year": 2019,
  "authors": [
   "Emma Strubell",
   "Ananya Ganesh",
   "Andrew McCallum"
  ],
  "n_authors": 3,
  "venue": "Annual Meeting of the Association for Computational Linguistics (ACL)",
  "venue_type": "conference",
  "doi": "10.18653/v1/p19-1355",
  "arxiv": "1906.02243",
  "openalex": [
   "W2948223045"
  ],
  "cited_by": 3671,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2948223045",
    "kind": "published",
    "doi": "10.18653/v1/p19-1355",
    "arxiv": "1906.02243",
    "venue": "Annual Meeting of the Association for Computational Linguistics (ACL)",
    "venue_type": "conference",
    "year": 2019,
    "cited_by": 3671,
    "is_retracted": false,
    "authors": [
     "A5051203366",
     "A5084241804",
     "A5107835063",
     "ananya|g",
     "andrew|m",
     "emma|s",
     "ganesh|a",
     "mccallum|a",
     "strubell|e"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 12,
  "title": "Model Cards for Model Reporting",
  "year": 2019,
  "authors": [
   "Margaret Mitchell",
   "Simone Wu",
   "Andrew Zaldivar"
  ],
  "n_authors": 9,
  "venue": "ACM Conference on Fairness, Accountability, and Transparency (FAccT)",
  "venue_type": "conference",
  "doi": "10.1145/3287560.3287596",
  "arxiv": "1810.03993",
  "openalex": [
   "W2897042519"
  ],
  "cited_by": 2661,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2897042519",
    "kind": "published",
    "doi": "10.1145/3287560.3287596",
    "arxiv": "1810.03993",
    "venue": "ACM Conference on Fairness, Accountability, and Transparency (FAccT)",
    "venue_type": "conference",
    "year": 2019,
    "cited_by": 2661,
    "is_retracted": false,
    "authors": [
     "A5089275971",
     "A5118595929",
     "andrew|z",
     "barnes|p",
     "ben|h",
     "elena|s",
     "gebru|t",
     "hutchinson|b",
     "inioluwa|r",
     "lucy|v",
     "margaret|m",
     "mitchell|m",
     "parker|b",
     "raji|i",
     "simone|w",
     "spitzer|e",
     "timnit|g",
     "vasserman|l",
     "wu|s",
     "zaldivar|a"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 },
 {
  "n": 13,
  "title": "Datasheets for datasets",
  "year": 2021,
  "authors": [
   "Timnit Gebru",
   "Jamie Morgenstern",
   "Briana Vecchione"
  ],
  "n_authors": 7,
  "venue": "Communications of the ACM",
  "venue_type": "journal",
  "doi": "10.1145/3458723",
  "arxiv": "1803.09010",
  "openalex": [
   "W2795038878"
  ],
  "cited_by": 2459,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2795038878",
    "kind": "published",
    "doi": "10.1145/3458723",
    "arxiv": "1803.09010",
    "venue": "Communications of the ACM",
    "venue_type": "journal",
    "year": 2021,
    "cited_by": 2459,
    "is_retracted": false,
    "authors": [
     "A5019928111",
     "A5033954307",
     "A5043117896",
     "A5045592180",
     "A5046348432",
     "A5069421536",
     "A5089275971",
     "briana|v",
     "crawford|k",
     "daume|h",
     "gebru|t",
     "hal|d",
     "hanna|w",
     "jamie|m",
     "jennifer|v",
     "kate|c",
     "morgenstern|j",
     "timnit|g",
     "vaughan|j",
     "vecchione|b",
     "wallach|h"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": true
 },
 {
  "n": 14,
  "title": "An Introduction to the Bootstrap",
  "year": 1995,
  "authors": [
   "Scott D. Grimshaw",
   "Bradley Efron",
   "Robert John Tibshirani"
  ],
  "n_authors": 3,
  "venue": "Technometrics",
  "venue_type": "journal",
  "doi": "10.2307/1269918",
  "arxiv": "",
  "openalex": [
   "W4310299640"
  ],
  "cited_by": 2096,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W4310299640",
    "kind": "published",
    "doi": "10.2307/1269918",
    "arxiv": "",
    "venue": "Technometrics",
    "venue_type": "journal",
    "year": 1995,
    "cited_by": 2096,
    "is_retracted": false,
    "authors": [
     "A5027340494",
     "A5065321980",
     "A5108567924",
     "bradley|e",
     "efron|b",
     "grimshaw|s",
     "robert|t",
     "scott|g",
     "tibshirani|r"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex"
  ],
  "after_input": false
 },
 {
  "n": 15,
  "title": "Deep Reinforcement Learning That Matters",
  "year": 2018,
  "authors": [
   "Peter Henderson",
   "Riashat Islam",
   "Philip Bachman"
  ],
  "n_authors": 6,
  "venue": "Proceedings of the AAAI Conference on Artificial Intelligence",
  "venue_type": "conference",
  "doi": "10.1609/aaai.v32i1.11694",
  "arxiv": "1709.06560",
  "openalex": [
   "W2754517384",
   "W2963120839"
  ],
  "cited_by": 2023,
  "connections": 1,
  "is_retracted": false,
  "versions": [
   {
    "openalex": "W2754517384",
    "kind": "published",
    "doi": "10.1609/aaai.v32i1.11694",
    "arxiv": "",
    "venue": "Proceedings of the AAAI Conference on Artificial Intelligence",
    "venue_type": "conference",
    "year": 2018,
    "cited_by": 1683,
    "is_retracted": false,
    "authors": [
     "A5049073875",
     "A5058417675",
     "A5065836447",
     "A5079926596",
     "A5080591144",
     "A5109496264",
     "bachman|p",
     "david|m",
     "doina|p",
     "henderson|p",
     "islam|r",
     "joelle|p",
     "meger|d",
     "peter|h",
     "philip|b",
     "pineau|j",
     "precup|d",
     "riashat|i"
    ]
   },
   {
    "openalex": "W2963120839",
    "kind": "preprint",
    "doi": "",
    "arxiv": "1709.06560",
    "venue": "",
    "venue_type": "",
    "year": 2017,
    "cited_by": 340,
    "is_retracted": false,
    "authors": [
     "A5049073875",
     "A5058417675",
     "A5065836447",
     "A5079926596",
     "A5080591144",
     "A5109496264",
     "bachman|p",
     "david|m",
     "doina|p",
     "henderson|p",
     "islam|r",
     "joelle|p",
     "meger|d",
     "peter|h",
     "philip|b",
     "pineau|j",
     "precup|d",
     "riashat|i"
    ]
   }
  ],
  "library": "",
  "found_by": [
   "openalex",
   "semanticscholar"
  ],
  "after_input": false
 }
]
```
