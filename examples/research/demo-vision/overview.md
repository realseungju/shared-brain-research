---
project: demo-vision
status: active
canon: research/demo-vision/overview.md
updated: 2026-07-28
---

# Demo Vision

## 한 줄 요약

가상 색상 분류 baseline으로 연구 provenance와 교차 AI 인계를 보여준다.

## 연구 질문

고정된 demo-v1에서 baseline이 무작위 기준보다 높은가?

## 성공 기준

- 주지표: Macro-F1
- baseline: 무작위 기준 0.50
- 판단 단위: 3시드 평균

## 현재 어디까지

| 항목 | 상태 | 근거 |
|---|---|---|
| 질문 Q001 | answered | `questions.md` |
| 실험 | completed | `experiments/E2026-07-28-color-baseline.md` |
| 주장 C001 | supported | `claims.md` |

## 방법

개인정보가 없는 가상 dataset에서 동일 설정을 세 시드로 반복한다.

## 현재 근거

- demo-v1의 3시드 평균은 0.81이다 — measured, experiment 링크.

## 다음 단계

- [ ] 다른 가상 분포에서 재검증

## 관련 문서

- `questions.md`
- `claims.md`
- `experiments/E2026-07-28-color-baseline.md`
