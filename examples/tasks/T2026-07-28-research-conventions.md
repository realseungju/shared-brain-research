---
id: T2026-07-28-research-conventions
title: research/ 최소 관례·템플릿 도입
phase: implementation
assignee_role: 관리자
spec: none
agent: Claude (Opus 5)
started: 2026-07-28
finished: 2026-07-28
closed_reason: completed
result: 683bbb1
---

# research/ 최소 관례·템플릿 도입

## 목적

연구용으로 이 저장소를 넘겨받는 사용자가 첫날부터 연구 기록을 남길 수 있게 한다.
기존에는 `research/`가 빈 확장 지점이라 정작 주 용도가 비어 있었다.

## 할 일

- [x] `research/README.md` — 디렉터리 구조·정본 규칙·재현 정보 규칙
- [x] `research/_template/overview.md` — 프로젝트 개요 템플릿
- [x] `research/_template/experiment.md` — 실험 기록 템플릿 (반증 조건·설정 핀·근거 종류)
- [x] `system/RULES.md`에 Research 절 추가, 선택형 영역에서 `research/` 제외
- [x] `system/conventions.md` 파일명 표에 `research/` 추가
- [x] ADR-001로 "관례만 제공, 자동화 없음" 결정 기록

## 완료 조건

- [x] Tier 0 읽기 비용이 늘지 않는다 (research는 Tier 2)
- [x] `brain-lint`가 `research/` 내용을 검사하지 않는다
- [x] 템플릿만 보고 새 프로젝트 문서를 시작할 수 있다

## 진행 메모

강제하지 않기로 한 이유는 ADR-001에 있다. 연구 기록 형태는 프로젝트마다 달라서
구조를 강제하면 우회가 생기고, 우회는 규칙 전체의 신뢰를 깎는다.
