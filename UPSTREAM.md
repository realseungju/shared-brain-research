# Upstream

Shared Brain Research는 `shared-brain-lite`의 연구자용 배포판이다.

| 항목 | 값 |
|---|---|
| upstream | `https://github.com/realseungju/shared-brain-lite` |
| imported commit | `5209e42241b8b8eb0cc5d6423f725be0530f6533` |
| imported date | 2026-07-28 |
| local base commit | `1552b27` |

## 소유 경계

공통 코어:

- AI 진입 stub
- task/session 생성기와 스키마
- `infra/brain-lint.py`
- Git hook과 공통 회귀 테스트

Research판 소유:

- `research/` 프로젝트·실험·claim 계약
- `feedback/` 미팅 feedback 계약
- `infra/new-experiment.py`, `infra/new-meeting.py`, `infra/research-lint.py`
- 연구 예시·교차 AI 데모·플랫폼 호환성 문서

upstream 변경은 자동으로 덮어쓰지 않는다. 변경 내용을 검토하고 공통 코어에 필요한 수정만
선택적으로 반영한 뒤 전체 테스트를 다시 실행한다.
