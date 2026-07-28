# Platform Compatibility

검사일: 2026-07-28, Windows.

| 플랫폼 | 로컬 확인 | 저장소 진입 계약 | 판정 |
|---|---|---|---|
| Claude Code 2.1.220 | `claude --version` | 루트 `CLAUDE.md` | 구조 확인 |
| Hermes Agent 0.17.0 | `hermes --version` | cwd의 `AGENTS.md`·`CLAUDE.md` 로드 | 로컬 코드 확인 |
| Orca CLI | `orca --help`의 existing-folder·repo·worktree 명령 | 선택 agent에 저장소/worktree cwd 전달 | CLI 확인 |
| Codex CLI 0.145.0 | `codex --version` | 루트 `AGENTS.md` | 구조 확인 |

이 표는 executable·작업 디렉터리·진입 파일 계약을 확인한 결과다. 모델 응답 품질이나
자동 준수율 benchmark가 아니다. 실제 pilot에서는 Claude Code에서 session을 닫고,
Orca의 같은 project/worktree에서 Hermes를 시작해 `examples/cross-agent-demo/` 절차를 확인한다.

## 공통 사용법

1. 저장소 루트를 플랫폼의 project/workspace/working directory로 지정한다.
2. AI에게 저장소 지침을 먼저 읽으라고 요청한다.
3. 자연어로 연구 작업과 기록 갱신을 함께 요청한다.
4. agent가 `research-lint`를 실행하고 session을 닫도록 한다.

Hermes가 cwd의 context 파일을 읽는 근거는 설치된 Hermes의 `agent/agent_init.py`와
cron workspace 초기화 코드에서 `AGENTS.md`·`CLAUDE.md` 로드를 확인했다.
