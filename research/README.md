# Research

프로젝트별 질문·실험·근거·주장을 관리한다. **Tier 2**이므로 시작 절차에서는 읽지 않고,
현재 task나 session hook이 가리킬 때만 연다.

## 프로젝트 구조

```text
research/
  _template/
  {project-slug}/
    overview.md
    questions.md
    claims.md
    experiments/
      EYYYY-MM-DD-{slug}.md
```

새 프로젝트는 AI에게 초기화를 요청한다. AI는 `_template/`의 `overview.md`,
`questions.md`, `claims.md`를 복사하고 `experiments/`를 만든 뒤 project slug와
placeholder를 바꾼다.

## 증거 흐름

```text
Q001 question
→ H001 hypothesis
→ EYYYY-MM-DD-slug experiment
→ C001 claim candidate
→ human review
→ supported / rejected
```

- `overview.md`는 현재 상태와 정본 링크만 짧게 유지한다.
- `questions.md`에는 질문, 중요성, 연결 가설, 답과 근거를 둔다.
- `experiments/`에는 실행 전 가설·반증 조건과 실행 후 결과·해석·한계를 함께 둔다.
- `claims.md`에는 결과로부터 검토할 주장만 둔다. 결과 파일이 곧 supported claim은 아니다.

## 실험 규칙

새 실험은 생성기로 만든다.

```sh
python infra/new-experiment.py baseline \
  --project my-project \
  --title "Baseline" \
  --hypothesis H001
```

`planned | running`은 열린 상태다. `completed | negative-result | invalidated`로 닫으려면:

- `dataset_version`, `code_commit`, `seed_or_repeats`, `artifact`의 `TBD` 제거
- `evidence_kind`를 `measured` 또는 `estimated`로 변경
- 결과·해석·한계 작성
- 결과와 해석 분리, 이 결과로 말할 수 없는 범위 명시

원시 데이터·모델 가중치·대용량 산출물·비밀정보는 Git에 넣지 않는다. repo 밖 위치와
재생성 방법만 기록한다.

## Claim 규칙

`supported`에는 다음 셋이 모두 필요하다.

1. 같은 프로젝트에 실제로 존재하는 experiment 경로
2. `evidence_kind: measured | estimated`
3. `human_reviewed: yes`

AI는 claim candidate를 작성하고 근거를 연결할 수 있지만 사람 대신 supported로 승인하지
않는다. 정확한 frontmatter와 항목 스키마는 `system/conventions.md`를 따른다.

`supported`로 올리기 전과 experiment를 닫기 전에 `skills/experiment-claim-check`를 적용한다.
lint는 근거가 **있는지**만 보고 **타당한지**는 못 본다 — 경계에 붙은 스윕, argmax로만 읽은
모델, 재본 적 없는 "천장", 검정 없는 "+N pt"는 필드를 다 채운 채로 통과한다(ADR-007).

## Task·Session·Feedback과의 관계

- `tasks/`는 할 일, `research/`는 질문과 알아낸 것, `system/sessions/`는 인계 기록이다.
- 실험 실행은 task, 실험 조건과 결과는 experiment, 사람 검토를 거친 결론은 claim이다.
- 미팅 출처는 `feedback/meetings/`에 두고 accepted 항목이 실제 task·research 문서를
  가리키게 한다.
- 프로젝트를 넘어 재사용되는 교훈만 `knowledge/`로 올린다.

완성된 예시는 `examples/research/demo-vision/`, 교차 AI 인계는
`examples/cross-agent-demo/README.md`를 본다.
