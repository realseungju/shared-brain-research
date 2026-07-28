# Shared Brain Lite

여러 AI 에이전트가 Git 저장소를 **공용 장기 기억**으로 쓰기 위한 경량 스타터입니다.

English: [README.md](README.md)

채팅 세션은 잊습니다. Claude·Codex·Gemini·Copilot은 서로의 기억을 공유하지 않습니다.
이 저장소는 기억을 *저장소 자체*에 둡니다 — 평문 Markdown, 모든 도구가 읽는 단일 진입점,
그리고 기록이 썩지 않게 막는 lint 게이트.

```text
아이디어 캡처 → 계획·Spec → Task → 작업 → Session 요약 → 다음 에이전트
```

## 그냥 메모 폴더와 뭐가 다른가

자유 형식 메모는 아무것도 강제하지 않아서 썩습니다. 썩지 않게 하는 장치는 셋입니다.

- **계층형 읽기.** 에이전트는 `system/RULES.md`, `system/context.md`, session index 꼬리
  몇 줄, `tasks/doing/` 파일명만 읽습니다. 나머지는 그 task가 필요로 할 때만 엽니다.
  저장소가 커져도 온보딩 비용이 일정하게 유지됩니다.
- **손편집 대신 생성기.** task·session 파일은 스크립트가 만듭니다. 그래서 모든 기록이
  같은 frontmatter 스키마를 갖고 올바른 위치에 놓입니다.
- **lint 게이트.** `brain-lint.py`가 pre-commit과 CI에서 돕니다. index에 없는 session,
  result 없이 `done/`에 있는 task, 파일명과 어긋나는 task id — 전부 거부됩니다.
  검사하지 않는 구조는 조용히 사실이 아니게 됩니다.

## 사용하는 방식

Shared Brain Lite는 따로 실행하는 앱이 아닙니다. **저장소 루트 자체를 AI 에이전트의
작업 디렉토리이자 장기 기억으로 사용합니다.**

이 템플릿으로 저장소를 만들거나 clone한 뒤, Orca·Hermes·Claude Code·Codex CLI 같은
AI 에이전트 플랫폼에서 해당 폴더를 프로젝트나 작업 디렉토리로 엽니다. 도구마다
project directory·workspace·repository·working directory처럼 이름은 다르지만,
`AGENTS.md`·`CLAUDE.md`·`system/`이 있는 저장소 루트를 지정하면 됩니다.

각 AI용 진입 파일은 모두 같은 운영 규칙과 현재 context를 읽도록 연결되어 있습니다.
사용자는 자연어로 작업을 요청하고, AI가 필요한 기억을 읽고 생성기와 lint를 실행하며,
다음 session이나 다른 AI가 이어받을 상태를 기록합니다.

## 빠른 시작

요구사항: AI가 실행되는 환경에 Git과 Python 3.10 이상. 외부 Python 패키지는 필요하지
않습니다.

1. 이 템플릿으로 저장소를 만들거나 clone합니다.
2. 저장소 루트를 AI 플랫폼의 작업 디렉토리로 지정하고 그 위치에서 AI를 시작합니다.
3. 첫 요청을 자연어로 전달합니다.

> 먼저 저장소의 운영 지침을 읽어줘. 이 shared brain을 [연구 주제] 용도로 초기화하고,
> `system/context.md`를 갱신한 다음 [목표]를 첫 task로 만들어줘.

4. 이후 작업도 자연어로 요청합니다. task를 시작하거나 마칠 때 shared brain 상태도
   갱신해 달라고 하면 됩니다. 다른 AI 플랫폼에서도 같은 저장소를 작업 디렉토리로 열면
   기록된 상태부터 이어갈 수 있습니다.
5. 다른 기기나 동료와 기억을 공유해야 할 때 AI에게 commit과 push를 요청합니다.
   사용하는 플랫폼에 따라 Git 작업 승인이 필요할 수 있습니다.

아래 Python 명령은 보통 **사용자가 직접 입력하지 않습니다.** AI가 운영 흐름 안에서
실행하는 정본 명령입니다.

```sh
python infra/new-task.py first-task --title "첫 작업"
python infra/new-session.py first-session \
  --agent Codex \
  --tags demo \
  --hook "다음 에이전트가 이 줄만 읽고 본문을 열지 판단한다" \
  --did "첫 task를 생성하고 구조를 확인함" \
  --next "실제 프로젝트 context 작성"
python infra/brain-lint.py
```

명령을 문서에 남긴 이유는 AI가 같은 방식으로 작업하게 하고, 필요할 때 사람이 직접
문제를 확인하거나 검증할 수 있게 하기 위해서입니다. task 필드와 허용값은
[`system/conventions.md`](system/conventions.md)에 있습니다.

## 구조

```text
system/       운영 규칙·현재 context·session 요약·ADR
tasks/        backlog / doing / done
specs/        만들기 전에 쓰는 명세
inbox/        아직 계획되지 않은 아이디어
knowledge/    프로젝트를 넘어 재사용되는 교훈
research/     프로젝트별 연구 문서·실험 기록 (Tier 2)
skills/       도구별 스킬 확장점
personal/     확장점, 기본은 비어 있음
examples/     읽기용 예시 산출물 — live 기록이 아님
infra/        생성기·lint·테스트·Git hook
```

live 트리는 **의도적으로 비어 있습니다** — session 요약 없음, 닫힌 task 없음,
`system/context.md`는 플레이스홀더. 템플릿으로 저장소를 만들면 구조를 물려받지 남의 Tier 0을
물려받지 않습니다. 채워진 session 요약이나 닫힌 task가 어떤 모양인지는
[`examples/`](examples/)를 보세요 — 회귀 시험이 이 예시들을 `brain-lint` 스키마와 맞춰 둡니다.

`system/RULES.md`가 운영 규칙의 단일 출처입니다. `CLAUDE.md`·`AGENTS.md`·`GEMINI.md`·
`.github/copilot-instructions.md`는 전부 그걸 가리키는 얇은 stub이라, 새 AI 도구를 붙일 때
규칙 사본이 아니라 stub 하나만 늘어납니다.

## 포함 기능

- Claude·Codex·Gemini·Copilot 공통 진입점
- Tier 0/1/2 계층형 읽기
- `inbox → spec → task` 계획 게이트
- `backlog → doing → done` task 생명주기
- 태그·훅이 있는 session 요약과 append-only index
- task/session 생성기
- pre-commit과 GitHub Actions에 연결된 `brain-lint` 구조 검사
- spec·knowledge 노드·연구 문서·실험 기록 템플릿

## 포함하지 않는 기능

- 개인 일정·아이디어 관리 (`personal/`은 의도적으로 비움 — ADR-002)
- 외부 캘린더·GitHub Issue 동기화
- 멀티 worktree 자동 통합
- 모델 라우팅·평가 하니스·에이전트 안전 훅

전부 의도적으로 뺐습니다. 이유는 `system/decisions.md`에, 실제로 필요해졌을 때 착수할
opt-in task는 `tasks/backlog/`에 있습니다.

## Git hook

선택 사항이지만 권장합니다. AI에게 한 번 설정해 달라고 요청하면 이후 매 commit 전에
`brain-lint`가 실행됩니다. AI가 사용할 명령은 다음과 같습니다.

```sh
git config core.hooksPath infra/hooks
```

AI에게 **실제로 도는지도 확인해 달라고 요청하세요** — 있다고 믿는데 안 도는 게이트는
없느니만 못합니다.

```sh
git commit --allow-empty -m "hook check"   # "brain-lint: 클린 ✓"가 찍혀야 정상
```

GitHub Actions가 push·PR마다 같은 lint와 테스트를 돌리므로, 로컬 훅이 빠져도 CI가 잡습니다.

## 둘 이상이 같이 쓸 때

각자 자기 사본을 쓰거나, 하나의 repo를 공유할 수 있습니다. 공유한다면
`system/sessions/index.md`가 append-only라 두 사람이 session을 닫을 때마다 확정적으로
충돌합니다 — `.gitattributes`에 `merge=union`을 걸어 두어 양쪽 줄이 모두 보존됩니다.
task·session 본문은 1항목=1파일이라 충돌면이 없습니다.

## 원칙

- 기록되지 않은 작업은 다음 에이전트에게 존재하지 않습니다.
- 저장소 전체가 아니라 필요한 Tier만 읽습니다.
- inbox 항목은 Spec이나 task가 되기 전에 구현하지 않습니다.
- 실제 비밀정보·개인정보·대용량 연구 산출물은 공개 저장소에 넣지 않습니다.

## License

MIT — [LICENSE](LICENSE) 참조.
