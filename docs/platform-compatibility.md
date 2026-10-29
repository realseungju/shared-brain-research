# Platform Compatibility

검사일: 2026-07-28 처음, 2026-10-29 다시 확인. Windows.

| 플랫폼 | 확인 | 저장소 진입 계약 | 판정 |
|---|---|---|---|
| Claude Code | 2026-10-29 데스크톱 앱에서 이 저장소로 도서관 기능 개발·검증 | 루트 `CLAUDE.md` | 실사용 확인 |
| Codex CLI 0.164.0 | 2026-10-29 `codex --version`, 맥락 없이 도서관 trail을 이어 탐색(아래) | 루트 `AGENTS.md` | 실사용 확인 |
| Hermes Agent 0.22.5 | 2026-10-29 `hermes --version` | cwd의 `AGENTS.md`·`CLAUDE.md` 로드 | 버전 확인 (0.17.0에서 로컬 코드 확인) |

**교차 에이전트 실사용 (2026-10-29):** Claude Code가 만든 도서관 trail을 Codex가 이전 대화 없이
파일만 읽고 `step-02`에서 이어 탐색했다. Codex가 파악한 단계별 입력·방향·제안이 실제와 같았고,
기존 단계 파일은 바뀌지 않았으며 `research-lint`가 통과했다.

**도서관 기능의 환경 조건:** 네트워크가 필요하다. OpenAlex·Semantic Scholar 키는 선택이며
사람이 환경 변수에 넣는다. 에이전트가 외부 모델 프로세스에 키를 넘기지 않게 한다.

이 표는 실행 파일·작업 디렉터리·진입 파일 계약과 위 실사용을 확인한 결과다. 모델 응답 품질이나
자동 준수율 benchmark가 아니다. 직접 확인하려면 Claude Code에서 session을 닫고,
같은 저장소에서 Hermes를 시작해 `examples/cross-agent-demo/` 절차를 확인한다.

## 공통 사용법

1. 저장소 루트를 플랫폼의 project/workspace/working directory로 지정한다.
2. AI에게 저장소 지침을 먼저 읽으라고 요청한다.
3. 자연어로 연구 작업과 기록 갱신을 함께 요청한다.
4. agent가 `research-lint`를 실행하고 session을 닫도록 한다.

Hermes가 cwd의 context 파일을 읽는 근거는 설치된 Hermes의 `agent/agent_init.py`와
cron workspace 초기화 코드에서 `AGENTS.md`·`CLAUDE.md` 로드를 확인했다.
