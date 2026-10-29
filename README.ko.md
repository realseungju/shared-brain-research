# Shared Brain Research

계산 연구자를 위한 Git 기반 실험 기억·교차 AI 인계 시스템입니다.

English: [README.md](README.md)

Shared Brain Research는 저장소를 Claude Code·Hermes·Orca·Codex CLI 같은 AI의 지속 가능한
작업 기억으로 만듭니다. 연구 질문, 실험 조건, 근거, 주장, 미팅 피드백, task, session 인계를
평문 Markdown으로 관리하고, 근거 없는 상태 변경은 lint로 거부합니다.

```text
질문 → 가설 → 실험 → 근거 → 사람이 검토한 주장
미팅 → atomic feedback → 사람 분류 → 연결 작업 → 검증
```

메모 앱이나 모델 실행기가 아닙니다. **저장소 루트 자체를 AI 플랫폼의 프로젝트·작업
디렉토리로 사용합니다.** 파일 생성과 Python 명령은 AI가 맡고, 연구자는 의도를 정하고 주장과
피드백을 승인하며 근거를 검토합니다.

## 왜 필요한가

연구 인계에서는 실행 커밋, 데이터셋 버전, 측정과 추론의 구분, 사람이 검토했다고 기록된
문장이 쉽게 사라집니다. 이 프로젝트는 그 경계를 강제합니다.

- 닫힌 실험에는 재현 조건·결과·해석·한계가 모두 있어야 합니다.
- lint 계약상 claim은 연결된 실험 근거와 `human_reviewed: yes` 없이는 `supported`가 될 수
  없습니다.
- 미팅 발언은 사람이 atomic feedback마다 수락·거절·보류하기 전까지 출처 자료입니다.
- session은 작은 색인형 인계를 남겨 다른 AI가 저장소 전체를 읽지 않고 이어갑니다.
- `research-lint`가 로컬과 CI에서 이 계약을 검사합니다.

## 빠른 시작

요구사항은 AI 환경의 Git과 Python 3.10 이상뿐입니다. 외부 Python 패키지는 없습니다.

1. 이 템플릿으로 저장소를 만들거나 clone합니다.
2. `AGENTS.md`·`CLAUDE.md`·`system/`이 있는 저장소 루트를 AI 플랫폼의 project,
   workspace, repository, working directory로 엽니다.
3. 첫 요청을 자연어로 전달합니다.

> 먼저 저장소 지침을 읽어줘. `my-project` 연구 프로젝트를 초기화하고 현재 context를
> 갱신한 다음 첫 연구 질문·가설과 baseline 실험 계획을 만들어줘. claim이나 미팅 feedback을
> accepted로 바꾸기 전에는 나에게 승인받아.

4. 같은 저장소를 Claude Code·Hermes·Orca·Codex CLI 또는 다른 AI에서 열어 이어갑니다.
   다른 기기나 동료에게 상태를 넘길 때 commit·push를 요청합니다.

아래 Python 명령은 보통 **사용자가 직접 입력하지 않습니다.** AI가 요청을 수행하면서
사용하는 정본 명령입니다.

```sh
python infra/new-task.py baseline --title "Baseline 실행"
python infra/new-experiment.py baseline \
  --project my-project \
  --title "Baseline" \
  --hypothesis H001
python infra/new-meeting.py weekly-review \
  --title "주간 연구 리뷰" \
  --project my-project
python infra/new-session.py baseline-result \
  --agent Hermes \
  --tags research,handoff \
  --hook "baseline experiment와 C001을 열 것" \
  --did "baseline 결과를 기록함" \
  --next "C001 지원 여부를 검토"
python infra/research-lint.py
```

문서에 명령을 남긴 이유는 AI가 같은 방식으로 작업하게 하고 사람이 필요할 때 직접 검증할 수
있게 하기 위해서입니다. 정확한 스키마와 허용값은
[`system/conventions.md`](system/conventions.md)에 있습니다.

## 연구 흐름

각 live 프로젝트는 다음 구조를 씁니다.

```text
research/{project}/
  overview.md
  questions.md
  claims.md
  experiments/
    EYYYY-MM-DD-{slug}.md
```

AI에게 `research/_template/`의 세 파일을 복사하고 `experiments/`를 만든 뒤 placeholder를
바꾸라고 요청합니다. 실험은 `planned` 또는 `running`으로 시작합니다. `completed`,
`negative-result`, `invalidated`로 닫으려면 데이터 버전, 코드 커밋, 시드·반복 조건,
artifact 위치, 근거 종류, 결과, 해석, 한계가 필요합니다.

실험 결과와 claim은 분리됩니다. 측정 결과에도 좁은 적용 범위나 교란이 있을 수 있습니다.
그래서 `supported` claim에는 같은 프로젝트의 실제 experiment 경로, `measured` 또는
`estimated`, `human_reviewed: yes`가 모두 필요합니다.

완성 예시는 [`examples/research/demo-vision/`](examples/research/demo-vision/)에,
Claude Code에서 Hermes로 넘기는 인계 fixture는
[`examples/cross-agent-demo/README.md`](examples/cross-agent-demo/README.md)에 있습니다.

## 미팅 피드백

AI에게 미팅·리뷰·동료 관찰을 redacted 미팅 기록으로 정리해 달라고 요청합니다. 기본
visibility는 `redacted`입니다. 참여자는 역할로 표시하고, 비공개 전사본과 대용량 산출물은
공개 저장소 밖에 둡니다.

feedback 항목 하나에는 진술 하나와 출처 방식 `quote | paraphrase | inference`가 들어갑니다.
triage된 상태는 `human_approved: yes`를 기록하고 lint는 이 provenance 필드와 상태 정합성을
검사합니다. 다만 누가 필드를 수정했는지는 인증할 수 없으므로 승인자 확인이 중요하면 commit·PR
리뷰와 branch protection을 사용해야 합니다. accepted 항목은 실제 task·research
문서·claim·ADR을 가리켜야 합니다. rejected·deferred에는 이유가, validated에는 실제 확인
결과가 필요합니다.

자세한 규칙은 [`feedback/README.md`](feedback/README.md), 완성 예시는
[`example meeting`](examples/feedback/meetings/2026-07-28-weekly-review.md)에 있습니다.

## 논문 도서관

AI에게 논문 몇 편에서 출발해 넓혀 달라고 요청합니다. 참고문헌(과거)·피인용(이후)·관련 논문·
키워드 검색 중 하나로 찾고, 검색 한 번이 단계 파일 하나로 남습니다. 다른 AI가 그 단계에서
이어 찾거나 갈라질 수 있습니다. AI가 후보 표를 보여 주면 사람이 번호를 고르고, 고른 논문만
도서관 레코드가 됩니다.

preprint와 게재본은 한 레코드로 합치고 게재처를 먼저 보입니다. 실제로 확인해 보니 한 논문의
arXiv 레코드는 참고문헌 0개·피인용 14건, 게재본은 참고문헌 46개·피인용 400건이었습니다. 그래서
preprint만 있는 시작 논문은 같은 제목의 게재본과 함께 씁니다. 철회 논문은 기본으로 빼고 개수를
남깁니다. 도서관 논문은 claim의 실험 근거로 세지 않습니다.

메타데이터는 [OpenAlex](https://openalex.org)에서 옵니다. OpenAlex 참고문헌 목록에는 빠진 것이
있어서, 참고문헌 단계는 Crossref와 Semantic Scholar에도 물어 더하고 후보마다 어느 목록에서
찾았는지 남깁니다. 키 없이도 작은 예산으로 되고, 무료 키를 `OPENALEX_API_KEY`·
`SEMANTIC_SCHOLAR_API_KEY`에 넣으면 늘어납니다. 자세한 것은 [`library/README.md`](library/README.md).

## 구조

```text
system/       운영 규칙·현재 context·session 인계·ADR
research/     프로젝트별 질문·실험·근거·주장
library/      고른 논문·컬렉션·탐색 기록
feedback/     redacted 미팅과 사람이 분류한 feedback
tasks/        backlog / doing / done
specs/        구현 명세
inbox/        아직 계획되지 않은 아이디어
knowledge/    재사용 가능한 교훈
skills/       에이전트 스킬 — 주장 타당성 체크리스트 포함
examples/     live 상태가 아닌 완성 fixture
infra/        생성기·research lint·테스트·Git hook
personal/     빈 호환성 확장점
```

live task·session·research 프로젝트·미팅 영역은 비어 있는 상태로 배포됩니다. 예시는 live
트리와 분리되어 있고 회귀 테스트가 스키마 정합성을 검사합니다.

`system/RULES.md`가 운영 규칙의 단일 출처입니다. 각 AI 진입 파일은 이 문서를 가리키는 얇은
stub이라 지원 플랫폼마다 같은 시작 계약을 사용합니다.

## 포함 기능

- Git 기반 연구 질문·실험·근거·claim 기록
- supported claim과 미팅 feedback의 사람 검토 provenance 필드
- lint가 닿지 못하는 층을 위한 주장 타당성 체크리스트(`skills/experiment-claim-check`) —
  누출, 불균형한 튜닝 예산, 경계에 붙은 스윕, 검정 없는 차이. 운영 경험에 재현성 문헌의
  표준 점검을 더했다
- redacted 기본 미팅 기록과 accept/reject/defer/validate 상태
- 이어 갈 수 있는 탐색 기록·판본 병합·철회 필터·BibTeX 내보내기가 있는 논문 도서관
- 교차 AI task·session 인계
- Claude Code·Hermes·Codex CLI·Orca·Gemini·Copilot 진입점
- task·session·experiment·meeting 생성기
- pre-commit·GitHub Actions의 `research-lint`
- 테스트되는 교차 AI 데모 fixture

## 포함하지 않는 기능

- 개인 일정·personal 아이디어 관리
- 원문 전사·참여자 개인정보·비공개 데이터셋 저장
- 대용량 artifact·모델 가중치 저장
- 실험 실행·모델 라우팅·평가 인프라
- 외부 캘린더·이슈 트래커·연구실 시스템 동기화
- AI의 자동 진실 판정

이 경계는 의도적입니다. `personal/`은 빈 호환성 확장점으로만 남고, 연구 작업과 feedback
provenance가 이 배포판의 제품 범위입니다.

## 플랫폼 호환성

Claude Code·Hermes·Codex CLI·Orca의 저장소 계약과 설치된 CLI 동작을 확인했습니다.
모델 품질 benchmark가 아닌 구조적 호환성 확인입니다. 자세한 내용은
[`docs/platform-compatibility.md`](docs/platform-compatibility.md)에 있습니다.

## 검증

AI에게 로컬 hook을 한 번 설정해 달라고 요청합니다.

```sh
git config core.hooksPath infra/hooks
```

직접 검사할 때는 다음 명령을 사용합니다.

```sh
python infra/research-lint.py
python -m unittest discover -s infra/tests -v
```

GitHub Actions도 push·PR마다 두 검사를 실행합니다.

## Upstream과 License

Shared Brain Research는
[`shared-brain-lite`](https://github.com/realseungju/shared-brain-lite)에서 파생되었습니다.
가져온 revision과 소유 경계는 [`UPSTREAM.md`](UPSTREAM.md)에 기록되어 있습니다.

MIT — [LICENSE](LICENSE) 참조.
