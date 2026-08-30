> **Canonical: [`RULES.md`](RULES.md) (English).** This is a translation and may lag.
> Synced from commit: `730a0e8`.
> 이 문서는 번역본입니다. 규칙이 어긋나면 영어 정본이 우선합니다.

# RULES — Shared Brain Research 운영 규칙

**기록되지 않은 작업과 근거는 다음 에이전트에게 존재하지 않는다.**

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

연구 흐름:

```text
research question → hypothesis → experiment → evidence → claim/decision → next experiment
```

- 결과와 해석을 분리한다.
- 실패·무효 실험도 삭제하지 않고 닫힌 상태로 기록한다.
- supported claim은 실제 experiment 근거와 사람 검토가 필요하다.
- 연구 파일은 Tier 2다. 활성 항목만 context나 task에서 가리킨다.

## 파일 생성

task와 session 파일은 손으로 새로 만들지 않는다.

```sh
python infra/new-task.py {slug} --title "제목"
python infra/new-session.py {slug} --agent {이름} --tags {태그} \
  --hook "index 한 줄 요약" --did "한 것" --next "다음"
python infra/new-experiment.py {slug} --project {project} \
  --title "실험 제목" --hypothesis {가설}
python infra/new-meeting.py {slug} --title "미팅 제목" --project {project}
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

- 프로젝트마다 `overview.md`, `questions.md`, `claims.md`, `experiments/`를 둔다.
- **정본 문서 하나를 지정**하고 결론은 거기에만 둔다. 실행 로그는 별도 문서다.
- research는 Tier 2다. 시작 절차에서 읽지 않는다 — 필요할 때만 연다.
- 원시 데이터·모델 가중치·비밀정보는 Git에 넣지 않는다. 위치만 적는다.
- 정량 결과는 dataset/version, code commit, seed·반복, artifact, 근거 종류를 남긴다.
- `python infra/research-lint.py`가 실험·claim·feedback 계약까지 검사한다.
- 수치를 **주장으로 굳히기 직전**(claim supported 승격·experiment 닫기·context로 옮기기)에는
  `skills/experiment-claim-check`를 적용한다. lint는 근거의 존재만 보고 타당성은 못 본다.

## 미팅 Feedback

미팅 파일은 `feedback/meetings/`에 둔다. 상세 계약은 `feedback/README.md`.

- 기본 `visibility`는 `redacted`다.
- 발언은 사실이나 결정이 아니다. 인용·요약·AI 추론을 구분한다.
- AI는 후보를 추출할 수 있지만 `human_approved: yes`를 사람 대신 기록하지 않는다.
- 사람 승인과 연결 산출물이 있는 feedback만 accepted가 된다.
- 구현 완료를 validated로 자동 바꾸지 않는다. 문제 해결 여부를 따로 확인한다.
- `human_approved`는 provenance 기록이지 신원 인증이 아니다. 실제 승인은 Git 리뷰 이력으로
  확인한다.

`personal/`은 상속 호환성을 위한 빈 확장점이며 이 배포판의 기능 범위가 아니다.

## 금지

- Spec이나 완료 조건 없는 기능 구현
- task/session 파일을 생성기 없이 새로 만들기
- 검증하지 않은 결과를 완료로 기록
- 미검증 claim을 `supported`로 기록
- 사람 승인 없이 feedback을 `accepted` 또는 `validated`로 변경
- 미팅 발언이나 AI 추론을 확정 결정으로 기록
- 실제 개인정보·토큰·비밀정보를 공개 저장소에 기록
- 원문 녹취·전사본을 공개 저장소에 기록
- 대용량 데이터나 모델 파일을 Git에 직접 저장
