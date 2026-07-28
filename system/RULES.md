# RULES — Shared Brain Lite 운영 규칙

**기록되지 않은 작업은 다음 에이전트가 알 수 없다.**

## 시작 절차

1. 이 문서를 읽는다.
2. `system/context.md`를 읽는다.
3. `system/sessions/index.md` 꼬리 3~5줄을 읽는다.
4. `tasks/doing/` 파일명만 확인한다.
5. 현재 작업에 연결된 task·spec만 추가로 읽는다.

전체 저장소를 매번 통독하지 않는다.

## 읽기 계층

| Tier | 읽는 시점 | 대상 |
|---|---|---|
| 0 | 모든 session | `context.md`, session index 꼬리, doing 파일명 |
| 1 | 작업 착수 | 해당 task, 연결된 spec |
| 2 | 필요할 때만 | ADR, knowledge, research, 과거 session |

## 작업 흐름

```text
inbox → planning/spec → tasks/backlog → tasks/doing → tasks/done
```

- inbox는 아이디어 캡처용이다. 바로 구현하지 않는다.
- 기능 구현 전 요구사항과 완료 조건을 Spec 또는 task에 적는다.
- task 착수 시 `doing/`으로 옮기고 `agent`, `started`를 채운다.
- 완료 시 `done/`으로 옮기고 `finished`, `closed_reason`, `result`를 채운다.
- 한 task에는 한 명의 활성 작성자만 둔다.

필드 이름과 허용값은 `system/conventions.md`에 전부 적혀 있다. 채우지 않으면
`brain-lint`가 거부하므로 추측하지 말고 표를 본다.

## 파일 생성

task와 session 파일은 손으로 새로 만들지 않는다.

```sh
python infra/new-task.py {slug} --title "제목"
python infra/new-session.py {slug} --agent {이름} --tags {태그} \
  --hook "index 한 줄 요약" --did "한 것" --next "다음"
```

생성 후 task 본문과 session 본문을 보강하는 것은 허용한다.

## Session 종료

다음 에이전트가 알아야 할 작업이면 session 요약을 남긴다.

- 미완 작업은 task에 둔다.
- 현재 상태 변화는 `system/context.md`에 반영한다.
- 재사용 가능한 교훈은 `knowledge/`에 승격한다.
- 사소한 문구 수정은 task와 session을 생략할 수 있다.

## Research 기록

연구·실험 기록은 `research/{project-slug}/`에 둔다. 관례와 템플릿은 `research/README.md`.

- 프로젝트마다 `overview.md` 하나를 두고, 나머지는 주제별로 쪼갠다.
- **정본 문서 하나를 지정**하고 결론은 거기에만 둔다. 실행 로그는 별도 문서다.
- research는 Tier 2다. 시작 절차에서 읽지 않는다 — 필요할 때만 연다.
- 원시 데이터·모델 가중치·비밀정보는 Git에 넣지 않는다. 위치만 적는다.

## 선택형 영역

`personal/`은 기본 기능이 없는 확장 지점이다. 사용자가 실제 사용 사례를 요청하기
전에는 파일 구조·자동화·데이터 포맷을 임의로 만들지 않는다.

## 금지

- Spec이나 완료 조건 없는 기능 구현
- task/session 파일을 생성기 없이 새로 만들기
- 검증하지 않은 결과를 완료로 기록
- 실제 개인정보·토큰·비밀정보를 공개 저장소에 기록
- 대용량 데이터나 모델 파일을 Git에 직접 저장
