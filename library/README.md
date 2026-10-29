# Library

논문을 찾고, **사람이 고른 것만** 보관한다. **Tier 2**이므로 시작할 때 읽지 않는다. 지금
이어 갈 trail만 task나 session hook이 가리킨다.

두 층으로 나뉜다. Research Rabbit의 Library(보관)와 Search(탐색)를 나눈 구조를 본떴고,
탐색 단계가 Git 파일로 남아 다른 AI가 어느 단계에서든 이어 탐색할 수 있다는 점이 다르다.

| 층 | 위치 | 담는 것 |
|---|---|---|
| 도서관 | `papers/L0001.md` | 논문 1편 = 레코드 1개. preprint·게재본을 한 레코드로 묶는다 |
| 도서관 | `collections/{slug}.md` | 프로젝트·주제별 레코드 목록 |
| 탐색 기록 | `trails/YYYY-MM-DD-slug/` | 질문 하나의 탐색. `trail.md` + 검색 1회마다 `step-NN.md` |

## 흐름

```text
trail-new (질문 + 시작 논문)
→ step: 입력 논문 × 방향 → 후보 목록       (references · citations · related · search)
→ choose --by human: 사람이 고름            (AI가 고르면 --by ai → proposed 로만 남음)
→ choose --save: 고른 것만 도서관 레코드가 됨
→ step --from step-NN: 그 단계의 입력 + 고른 것(chosen)이 다음 입력. AI 제안(proposed)은 따라가지 않는다 — 쓰려면 --add step-NN#k.
  이전 단계에서 다시 갈라져도 뒤 단계는 지우지 않는다
```

```sh
python infra/library.py trail-new factuality --question "LLM 사실성은 어떻게 재나?" \
  --seed arxiv:2305.14251 --seed doi:10.18653/v1/2023.emnlp-main.557 --agent Claude
python infra/library.py step 2026-10-27-factuality --direction references --agent Claude
python infra/library.py choose 2026-10-27-factuality step-01 --pick 2,10 --by human \
  --save factuality --agent Claude
python infra/library.py step 2026-10-27-factuality --from step-01 --direction citations \
  --year 2024- --agent Codex
python infra/library.py show 2026-10-27-factuality
python infra/library.py export factuality --bibtex --out refs.bib
python infra/library.py refresh
```

이어받는 에이전트는 `show`로 단계마다 입력·필터·보조 출처를 본 뒤 `--from`으로 잇는다. 2026-10-29 Codex가 이 흐름으로
Claude의 trail을 step-02에서 이어 갔다(AC 1).

사용자는 명령을 직접 치지 않는다. 「이 두 논문에서 출발해 참고문헌을 넓혀 줘」처럼 말하면
에이전트가 실행하고, 후보 표를 보여 준 뒤 **사람이 번호를 고른다**.

## 판본 — 게재본을 먼저 보인다

OpenAlex는 같은 논문의 arXiv 판과 게재본을 따로 두는 일이 많다. 실측(2026-10-27):
FActScore arXiv 판은 참고문헌 0개·피인용 14건, EMNLP 게재본은 참고문헌 46개·피인용 400건이었다.

- 시작 논문이 preprint뿐이면 정확히 같은 제목의 게재본을 찾아 함께 쓴다(`W…+W…`).
- 후보는 판본을 합쳐 한 줄로 보이고, 피인용은 판본 합계다.
- `venue`는 게재본 기준이다. 게재본을 못 찾으면 `preprint-only`로 드러낸다.
- 제목만으로 합치려면 저자 한 명 이상이 겹쳐야 한다. 저자 전체(최대 50명)를 OpenAlex 저자 ID, 또는 성+다른 쪽 끝의
  머리글자(앞뒤 양방향)로 비교한다. `Sewon Min`·`Min Sewon`·`S. Min`은 같은 사람으로, `Wei Zhang`·`Wei Wang`은
  다른 사람으로 본다. 같은 제목이라도 저자가 안 겹치거나,
  서로 다른 게재 DOI가 있거나, 연도가 3년 이상 떨어지면 다른 논문으로 둔다. preprint 서버·워킹페이퍼(bioRxiv·SSRN·NBER)가
  붙인 DOI는 「다른 게재 DOI」로 치지 않는다 — 같은 논문의 판본이다. 이미 보관한 레코드도 같은 규칙으로 찾는다
  (레코드 쪽은 저장된 앞 3명 이름만 쓴다).
- 제목 비교는 한글·한자 등 모든 문자를 남긴다. 악센트만 지운다.
- 같은 제목의 preprint 하나가 서로 다른 게재 DOI를 가진 두 논문에 맞으면 어느 쪽에도 붙이지 않고 따로 둔다.
  단, preprint가 두 게재본 중 하나보다 먼저 들어와 이미 합쳐졌으면 그 묶음을 유지한다(도착 순서에 따름).
- `refresh`에서 OpenAlex가 더는 돌려주지 않는 옛 ID(병합·삭제)는 판본 표에 `· not returned`로 남는다.
  그 판본은 게재처·피인용·철회 판단에서 뺀다.

## 후보 정렬과 필터

- 정렬: 입력 논문 몇 편과 연결됐는지(`links`) → 피인용 → 연도. search는 OpenAlex 순서를 따른다.
- 철회 논문은 기본으로 뺀다. 숨기지 않고 `excluded: retracted=N`에 개수를 남긴다.
- `--year`, `--exclude-preprint-only`, `--limit`. 잘린 개수는 `beyond-limit=N`으로 남는다.
- citations는 입력마다 피인용 많은 순 상위 200편만 가져온다. 최근 논문이 빠질 수 있다 — `filters`에 적힌다.
  `--recent`를 주면 최신순 200편을 가져와 최신순으로 보인다.
- 입력 논문 자신과 **그 다른 판본**(같은 제목·겹치는 저자)은 후보에서 빼고 `input=N`으로 센다.
  실측(2026-10-29): QJE의 「Generative AI at Work」가 자기 NBER 워킹페이퍼를 참고문헌으로 달고 있었다.
- 인용한 논문보다 1년 넘게 늦은 참고문헌은 빼지 않고 연도 옆에 `⚠`를 붙인다(`after_input`).
  잘못된 연결일 수도, 잘못된 연도일 수도 있다. 실측(2026-10-29): AlphaFold(2021) 참고문헌에 2024년 논문이
  붙은 것은 연결 오류, 「Attention Is All You Need」가 2025년으로 적힌 것은 연도 오류였다.

## 참고문헌 보완 — Crossref·Semantic Scholar

OpenAlex 참고문헌 목록에는 빠진 것이 있다. 실측(2026-10-29): FActScore(EMNLP)의 OpenAlex 목록에는
FEVER·GPT-3·BERTScore가 없었다. 그래서 `references` 단계는 두 목록에 더 묻는다.

| 출처 | 아는 것 | 모르는 것 |
|---|---|---|
| Crossref | 출판사가 등록한 참고문헌(게재 DOI가 있어야 함) | ACL Anthology처럼 등록하지 않은 곳, DOI 없는 항목 |
| Semantic Scholar | 컴퓨터과학·preprint에 강함. DOI·arXiv ID로 못 찾으면 **정확히 같은 제목 + 겹치는 저자**로 찾는다 | 키 없이 쓰면 요청 제한(429)이 잦다. 키가 있어도 요청은 1.1초 간격 |

- 두 목록이 DOI·arXiv ID로 이름 댄 논문 중 OpenAlex 목록에 없는 것만 OpenAlex에서 다시 찾아 후보에 더한다.
  OpenAlex에 없으면 더하지 않고 `not found in OpenAlex`로 센다. ID 없는 항목은 추측하지 않고 `without DOI`로 센다.
- 후보마다 `found_by`에 어느 목록이 찾았는지 남는다. 단계의 `supplement`에 출처별 개수와 실패가 적힌다.
- 보조 출처가 실패해도 단계는 쓴다(OpenAlex 실패만 단계를 막는다). 실패는 `supplement`에 `unavailable`로 남는다.
- 요청 제한(429)은 2·5·10초 쉬고 다시 시도한다.
- `--openalex-only`를 주면 보조 출처에 묻지 않는다.
- `found_by: [semanticscholar]`만 있는 후보는 한 번 더 본다. 2026-10-29 6편에서 이런 후보 61개 중 5~6개는 인용 문자열이
  다른 논문으로 잘못 연결된 것으로 보였다(예: BERT 인용이 「BERT: A Review of Applications…」로, 제목 「MEETING SUMMARIES」).
  눈으로 본 판정이다. 같은 6편을 키를 넣고 4번 돌린 후보 목록은 매번 같았다.

같은 4편으로 Research Rabbit과 견준 결과(2026-10-29, 제목 앞 8단어 기준, 중복 제거 후 겹친 수):

| 시작 논문 | Research Rabbit | 보완 전 겹침 | 보완 후 겹침 |
|---|---|---|---|
| FActScore | 59 | 41 | 56 |
| AlphaFold | 87 | 77 | 79 |
| GraphCast | 27 | 24 | 25 |
| Generative AI at Work | 77 | 56 | 65 |

## 지켜지는 것 (research-lint)

- 단계 파일의 후보 목록은 검색 뒤 고쳐 쓸 수 없다 (`candidates_sha256`).
- `chosen`은 `chosen_by: human`일 때만. `saved`는 `chosen` 안에서만.
- 레코드는 자기 `source_step`의 `saved`에 있어야 한다 — 사람이 고르지 않은 레코드는 없다.
- 레코드와 컬렉션은 서로를 가리켜야 한다.
- 도서관 논문은 **실험 근거가 아니다.** `supported` claim의 evidence로 `library:`를 쓰면 실패한다.
- 단계 입력 `step-NN#k`는 앞선 단계의 실제 후보 번호여야 한다.
- 철회된 레코드를 `library:L0001`이나 `library/papers/L0001.md` 링크로 가리키는 research 문서는 WARN으로 알린다.

`chosen_by: human`은 `human_approved`와 같은 출처 기록이지 신원 인증이 아니다.

## 이용 조건

2026-02-13부터 OpenAlex는 API 키 기준 하루 예산제다. 키 없이도 되지만 예산이 작고, 무료 키는
10배다. ID 조회는 무료, 목록·필터는 1,000건당 $0.10, 검색은 1,000건당 $1이다.

- 키는 사람이 환경변수 `OPENALEX_API_KEY`에 넣는다. 파일·커밋·프롬프트에 쓰지 않는다.
- `OPENALEX_MAILTO`는 선택이다. Crossref에도 같은 주소로 연락처를 남긴다.
- Semantic Scholar 키는 `SEMANTIC_SCHOLAR_API_KEY`(선택). 없으면 요청 제한이 잦다.
- Crossref는 키가 없다.
- 한도 초과·네트워크 실패면 **단계를 쓰지 않고** 실패를 보고한다(종료 코드 3).

## 알려진 한계

- OpenAlex 참고문헌 연결에는 잡음이 있다. 실데이터에서 주제와 무관한 고피인용 논문이 후보에
  섞였다. 사람이 고르는 단계가 그래서 있다.
- `related`는 OpenAlex `related_works`다. 임베딩 유사도는 쓰지 않는다. 주제가 같은 최근 후속 연구가 주로 나온다.
  Research Rabbit의 Similar는 함께 자주 인용되는 논문(고전·도구 논문 포함)을 보여 준다 — 같은 이름의 다른 기능이다.
  2026-10-29 비교에서 4편 모두 겹침이 0~1편이었다. 함께 인용 방향은 아직 없다.
- 저자 방향, Zotero 동기화, 새 논문 알림, 인용 지도 화면은 아직 없다.
- 문헌 유형(논문·책·데이터셋 등) 필터는 넣지 않는다(2026-10-27 결정). 사람이 후보 표를 보고 고른다.
- 저자 정보가 없는 판본은 제목으로 합치지 않는다. 잘못 합치는 것보다 두 줄로 보이는 편이 낫다.
- PDF 원문 확보와 인용문 검증은 범위 밖이다.
