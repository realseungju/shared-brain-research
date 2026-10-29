> **Canonical: [`conventions.md`](conventions.md) (English).** This is a translation and may
> lag. Synced from commit: `4c7c42e`.
> 이 문서는 번역본입니다. 규칙이 어긋나면 영어 정본이 우선합니다.

# Conventions

## 파일명

| 위치 | 형식 |
|---|---|
| `tasks/*/` | `TYYYY-MM-DD-{slug}.md` |
| `system/sessions/` | `YYYY-MM-DD-{slug}.md` |
| `specs/` | `{slug}.md` |
| `knowledge/` | `{slug}.md` |
| `research/` | `{project-slug}/{doc-slug}.md` |
| `research/*/experiments/` | `EYYYY-MM-DD-{slug}.md` |
| `feedback/meetings/` | `YYYY-MM-DD-{slug}.md` |
| `inbox/` | `YYYYMMDD-{source}-{slug}.md` |

slug는 소문자 영문·숫자·하이픈만 쓴다. `_template.md`로 시작하는 템플릿 파일은 예외다.

## Task frontmatter

`infra/new-task.py`가 생성하고 `infra/brain-lint.py`가 검사한다. 손으로 상태를 옮길 때
아래 필드를 직접 채워야 한다.

| 필드 | 언제 필수 | 값 |
|---|---|---|
| `id` | 항상 | 파일명(확장자 제외)과 정확히 같아야 한다 |
| `title` | 항상 | 한 줄 제목 |
| `phase` | 항상 | `planning` \| `review` \| `implementation` \| `validation` |
| `assignee_role` | 선택 | 담당 역할(사람 이름 아님) |
| `spec` | 선택 | 연결된 `specs/{slug}.md` 또는 `none` |
| `agent` | `doing/`에서 | 지금 이 task를 쥔 작성자 |
| `started` | `doing/`에서 | `YYYY-MM-DD` |
| `finished` | `done/`에서 | `YYYY-MM-DD` |
| `closed_reason` | `done/`에서 | `completed` \| `cancelled` \| `superseded` |
| `result` | `done/`에서 | 커밋 해시·PR 번호 등 확인 가능한 산출물 |

`phase`는 task가 **지금 어느 단계인지**이고, `backlog/doing/done`은 **어느 디렉터리에 있는지**다.
둘은 독립이다 — `doing/`에 있는 `planning` phase task는 정상이다.

## Task 상태

```text
backlog → doing → done
```

완료 이유:

- `completed`: 목표 달성
- `cancelled`: 중단하고 재개 계획 없음
- `superseded`: 다른 접근으로 대체

## Session frontmatter

`infra/new-session.py`가 생성한다. 손으로 만들지 않는다.

| 필드 | 값 |
|---|---|
| `date` | `YYYY-MM-DD` — 파일명 앞부분과 일치해야 한다 |
| `agent` | 작성자 이름 |
| `slug` | 파일명 뒷부분과 일치해야 한다 |
| `tags` | 소문자-하이픈 목록 |

본문에 `## 한 것`과 `## 미완·다음` 섹션이 반드시 있어야 한다(lint 검사 대상).
`## 결정·이유`와 `## 주의·함정`은 생성기가 함께 넣지만 강제하지 않는다.
모든 session 파일은 `system/sessions/index.md`에 한 줄로 등재돼 있어야 한다 —
생성기가 자동으로 추가하므로 파일을 지울 때만 신경 쓰면 된다.

## Experiment frontmatter

`infra/new-experiment.py`가 생성하고 `infra/research-lint.py`가 검사한다.

| 필드 | 값 |
|---|---|
| `id` | 파일명과 동일한 `EYYYY-MM-DD-{slug}` |
| `title` | 한 줄 제목 |
| `project` | 상위 `research/{project}/`와 동일 |
| `date` | 파일명의 날짜와 동일 |
| `status` | `planned \| running \| completed \| negative-result \| invalidated` |
| `hypothesis` | 가설 ID 또는 한 줄 가설 |
| `evidence_kind` | `measured \| estimated \| unverified` |
| `dataset_version` | dataset 이름과 버전 |
| `code_commit` | 7~40자 Git SHA 또는 `not-applicable` |
| `seed_or_repeats` | 시드 또는 반복 조건 |
| `artifact` | repo 밖 산출물 위치 또는 재생성 경로 |

`completed`, `negative-result`, `invalidated`는 닫힌 상태다. 닫을 때 재현 필드의 `TBD`를
제거하고 결과·해석·한계 본문을 채워야 하며 `evidence_kind: unverified`는 허용하지 않는다.

## Claim 항목

`research/{project}/claims.md`의 각 `## C001` 항목:

| 필드 | 값 |
|---|---|
| `statement` | 검토할 주장 한 개 |
| `status` | `candidate \| supported \| rejected` |
| `evidence` | 같은 프로젝트의 experiment 파일 경로 |
| `evidence_kind` | `measured \| estimated \| unverified` |
| `human_reviewed` | `yes \| no` |
| `reason` | rejected 이유 |

`supported`에는 존재하는 experiment, 검증된 근거 종류, `human_reviewed: yes`가 모두 필요하다.
결과 파일이 있다는 사실만으로 supported가 되지 않는다.

## Meeting과 Feedback

미팅 frontmatter:

| 필드 | 값 |
|---|---|
| `date` | 파일명의 날짜와 동일 |
| `title` | 한 줄 제목 |
| `project` | project slug 또는 `product` |
| `visibility` | `public \| private \| redacted` — 생성기 기본은 redacted |
| `status` | `captured \| triaged \| closed` |

각 `### FB-YYYY-MM-DD-01` 항목:

| 필드 | 값 |
|---|---|
| `scope` | `product \| research \| workflow` |
| `kind` | `request \| problem \| observation \| question \| decision-candidate` |
| `statement` | atomic 요청·관찰 한 개 |
| `source_mode` | `quote \| paraphrase \| inference` |
| `status` | `captured \| accepted \| rejected \| deferred \| validated` |
| `human_approved` | `yes \| no` |
| `linked_artifact` | 연결 task·가설·claim·ADR 파일 |
| `reason` | rejected·deferred로 분류한 이유 |
| `validation` | validated 전환 전, 반영 뒤 문제 해결을 확인한 결과 |

`captured` 이외의 triage는 사람 승인이 필요하다. accepted·validated에는 존재하는 연결 파일,
validated에는 실제 확인 결과가 필요하다. 승인된 `decision-candidate`는
`system/decisions.md#ADR-...`을 가리켜야 한다.

`rejected`와 `deferred`에는 `reason`이 필수다. `validation`에 분류 이유를 대신 쓰지 않는다.
meeting의 `status: closed`는 모든 feedback이 `rejected` 또는 `validated`일 때만 허용한다.
`captured`, `accepted`, `deferred`가 하나라도 남아 있으면 닫을 수 없다.

`human_approved`는 승인 provenance를 기록하는 필드이며 작성자 신원을 인증하지 않는다.
lint는 필드와 상태 정합성을 검사하고, 실제 사람 승인 여부는 Git commit·PR 리뷰나 branch
protection으로 확인한다.

## 도서관과 trail

`infra/library.py`가 도서관 파일을 모두 쓰고 `infra/research-lint.py`가 검사한다.
레코드·단계를 손으로 만들지 않는다. 흐름과 한계는 `library/README.md`.

레코드 frontmatter (`library/papers/L0001.md`):

| 필드 | 값 |
|---|---|
| `id` | `L` + 숫자 4자리, 파일명과 같음 |
| `venue` | 게재처, 또는 `preprint-only` |
| `venue_type` | `journal` \| `conference` \| `other` \| `preprint` — `venue`가 `preprint-only`일 때만 `preprint` |
| `openalex` | 이 레코드로 합친 OpenAlex work 전부 |
| `is_retracted` | `yes` \| `no` |
| `source_step` | `saved`에 이 레코드가 있는 `{trail}/{step}` |
| `collections` | 컬렉션 slug. 각 컬렉션 파일도 이 레코드를 나열해야 함 |

단계 frontmatter (`library/trails/{YYYY-MM-DD-slug}/step-NN.md`):

| 필드 | 값 |
|---|---|
| `parent` | 같은 trail의 이전 단계, 또는 `none` |
| `direction` | `search` \| `references` \| `citations` \| `related` |
| `inputs` | `L0001`, `W…`(한 논문의 판본은 `W…+W…`), 또는 `step-NN#k` |
| `excluded` | 이유별 개수: `retracted`, `year`, `preprint-only`, `input`(입력 또는 그 다른 판본), `beyond-limit` |
| `supplement` | 참고문헌 단계: Crossref·Semantic Scholar가 나열한 수, 더한 수, 실패한 출처. 그 밖에는 `none` |
| `candidates_sha256` | 후보 레코드 digest — 후보를 고치면 lint 실패 |
| `proposed` | AI가 제안한 번호. 저장되지 않음 |
| `chosen` / `chosen_by` | 사람이 고른 번호. `chosen`이 있으면 `chosen_by: human` |
| `saved` | `n=L0001` 쌍. chosen 번호만 |

참고문헌 후보에는 `found_by`(어느 참고문헌 목록에서 찾았는지)와 `after_input`(인용한 논문보다 1년 넘게
늦은 날짜 — 잘못된 연결이거나 잘못된 연도, 표에 `⚠`)도 붙는다.

도서관 논문은 실험 근거가 아니다. `supported` claim은 `library:`를 가리킬 수 없다.

## Commit

Conventional Commits를 권장한다.

```text
<type>(<scope>): <imperative summary>
```

## 문서

- 결론을 먼저 쓴다.
- 같은 내용을 여러 문서에 복제하지 않는다.
- 실제 상태와 재사용 지식을 분리한다.
- 다음 에이전트가 필요한 만큼만 남긴다.
- 미팅 원문은 Tier 2, accepted 항목만 활성 context나 task에서 가리킨다.
