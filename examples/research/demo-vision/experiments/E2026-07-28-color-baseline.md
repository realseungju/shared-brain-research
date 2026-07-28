---
id: E2026-07-28-color-baseline
title: 색상 분류 baseline
project: demo-vision
date: 2026-07-28
status: completed
hypothesis: H001
evidence_kind: measured
dataset_version: demo-v1
code_commit: 1a2b3c4
seed_or_repeats: seeds-1-3
artifact: external/demo/color-baseline.json
---

# 색상 분류 baseline

## 연구 질문

demo-v1에서 baseline이 무작위 기준보다 높은가?

## 가설

- 연결 가설: `H001`
- 예상: Macro-F1 평균이 0.50보다 높다.
- **반증 조건:** 3시드 평균이 0.50 이하이면 기각한다.

## 계획

- 비교 조건: 동일 설정, 시드 1·2·3
- 주지표: Macro-F1
- baseline: 0.50
- 판단 기준: 3시드 평균

## 실행 조건

| 항목 | 값 |
|---|---|
| 코드 커밋 | `1a2b3c4` |
| 데이터·버전 | `demo-v1` |
| 모델·버전 핀 | `demo-classifier-1.0` |
| 시드·반복 | `seeds-1-3` |
| 하드웨어 | 가상 예시 |
| artifact | `external/demo/color-baseline.json` |

## 실행 로그

- 2026-07-28 — 가상 3시드 결과 기록

## 결과

| 조건 | 지표 | 값 | N |
|---|---|---|---|
| baseline | Macro-F1 | 0.81 평균 | 3 seeds |

## 해석

- claim candidate: C001
- 근거 종류: `measured`
- 이 결과로 말할 수 없는 것: demo-v1 밖의 일반화

## 한계

- 가상 fixture라 실제 모델 성능을 나타내지 않는다.
- 통계 검정을 수행하지 않았다.

## 다음 단계

- [ ] 다른 가상 분포에서 반복
