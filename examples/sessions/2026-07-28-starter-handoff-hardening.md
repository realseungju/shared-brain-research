---
date: 2026-07-28
agent: Claude (Opus 5)
slug: starter-handoff-hardening
tags: [starter, research, onboarding, lint, portability]
---

# 2026-07-28 — Claude (Opus 5) — starter-handoff-hardening

## 한 것

Codex 초판을 검수하고, "동료 연구원에게 인계 + 공개 배포" 두 목표 기준으로 보강했다.
초판은 구조·테스트·CI 모두 그린이었고 개인정보 누출도 0이었다. 문제는 목표와의 정합이었다.

- **`research/` 도입** — 받는 사람이 연구원인데 정작 연구 기록 모듈이 "요청 전 구현 금지"로
  비어 있었다. README 관례 + overview·experiment 템플릿을 넣되 자동화는 넣지 않았다(ADR-001).
- **README 영어화** — 공개 목표의 최대 병목. 한국어는 `README.ko.md`로 분리.
- **README 10분 시작이 자기 게이트를 통과 못 하던 결함 수정** — 3단계대로 `doing/`으로 옮기면
  `agent`·`started` 누락으로 lint가 2건 거부했다. RULES에는 있고 README에는 없던 안내.
- **lint 스키마 문서화** — `phase` 유효값 4종·`assignee_role`·`spec`·session frontmatter·
  필수 섹션이 코드에만 있고 문서에 없었다. Tier 0만 읽는 규율과 정면 충돌하는 구멍.
- **훅 이식성** — `python` 하드코딩은 macOS/다수 Linux에서 즉사한다. 실행 가능한 인터프리터를
  탐색하도록 변경.
- **`sessions/index.md merge=union`** — append-only 로그라 두 사람이 session을 닫으면 확정 충돌.
- **테스트 6 → 18** — done 필드·phase 값·id 중복·session 섹션·index 정합, 그리고
  생성기 출력이 lint를 통과하는지(생성기와 검사기가 어긋나면 규율 전체가 무너진다).
- **예시 인공물** — ADR 2건·done task 1건·이 session. 방문자가 클론 없이 산출물 모양을 본다.

## 결정·이유

research/는 관례·템플릿만 제공하고 자동화하지 않는다(ADR-001). personal/은 요청 전까지 비워 둔다(ADR-002).

## 미완·다음

동료 피드백 수집 후 personal/ 착수 여부 판단.

## 주의·함정

pre-commit 훅에서 `command -v python3` 로 **존재만** 확인해 인터프리터를 고르면 Windows에서
Microsoft Store 설치 유도 스텁을 잡아 exit 49로 죽는다. macOS를 고치려던 수정이 Windows를
깨뜨린 것이고, 실제로 훅을 돌려보지 않았으면 그대로 나갔다.
**후보는 존재가 아니라 실행 여부로 판정해야 한다** — `"$candidate" -c "import sys"`.

같은 함정의 일반형: 게이트를 "설치했다"와 "돈다"는 다르다. README에 훅 설치 안내만 두지 말고
`git commit --allow-empty` 로 실제 발화를 확인하는 절차를 함께 적었다.
