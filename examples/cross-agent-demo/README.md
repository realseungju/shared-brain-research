# Claude Code → Hermes 인계 데모

이 fixture는 모델 성능 benchmark가 아니라 **저장소 계약이 인계를 가능하게 하는지** 재현한다.

## Turn 1 — Claude Code

1. 저장소 루트에서 시작해 `CLAUDE.md` → Tier 0을 읽는다.
2. Q001·H001과 baseline experiment 계획을 기록한다.
3. session 훅에 다음 agent가 열 경로를 남긴다.

예시: `examples/sessions/2026-07-28-claude-baseline-plan.md`

## Turn 2 — Hermes

1. 같은 저장소를 작업 디렉터리로 열면 Hermes가 `AGENTS.md`를 읽는다.
2. Tier 0의 최신 session 훅과 doing task를 통해 experiment만 추가로 연다.
3. 결과·한계·claim candidate를 기록하고, 사람 검토 뒤 claim을 supported로 바꾼다.

예시: `examples/sessions/2026-07-28-hermes-baseline-result.md`

## Feedback 연결

미팅 FB-01은 사람 승인 뒤 task로 연결된다. FB-02는 rejected, FB-03은 deferred다.
다음 AI는 미팅 전체를 Tier 0으로 읽지 않고 accepted task에서 출처로 거슬러 올라간다.

## 재현

회귀 테스트는 examples의 research·meeting·task·session을 빈 brain의 live 위치에 복사한 뒤
`research-lint`를 실행한다.

```sh
python -m unittest infra.tests.test_examples -v
```
