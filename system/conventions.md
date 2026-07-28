# Conventions

## 파일명

| 위치 | 형식 |
|---|---|
| `tasks/*/` | `TYYYY-MM-DD-{slug}.md` |
| `system/sessions/` | `YYYY-MM-DD-{slug}.md` |
| `specs/` | `{slug}.md` |
| `knowledge/` | `{slug}.md` |
| `research/` | `{project-slug}/{doc-slug}.md` |
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
