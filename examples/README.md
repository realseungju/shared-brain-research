# Examples

**읽기용 예시입니다. 여기 있는 파일은 live 기록이 아닙니다.**

`system/sessions/`와 `tasks/done/`을 채워 두면 이 저장소를 템플릿으로 복제한 사람의
Tier 0에 남의 기록이 그대로 섞입니다. 그래서 실제 산출물이 어떤 모양인지 보여주는 용도로만
여기에 두고, live 트리는 빈 상태로 배포합니다.

| 파일 | 무엇 |
|---|---|
| `sessions/2026-07-28-starter-handoff-hardening.md` | 채워진 session 요약 — 한 것·결정·미완·함정 4절 |
| `tasks/T2026-07-28-research-conventions.md` | 닫힌 task — `done/` 이동 시 채우는 필드가 전부 들어 있음 |

## 주의

- **`result: 683bbb1`은 이 저장소 상류(upstream shared-brain-lite)의 커밋 해시입니다.**
  템플릿으로 새로 만든 저장소의 이력에는 존재하지 않습니다. 형식 예시로만 보세요.
- 이 파일들을 그대로 복사해 쓰지 말고, 반드시 생성기로 만드세요:

```sh
python infra/new-task.py {slug} --title "제목"
python infra/new-session.py {slug} --agent {이름} --tags {태그} \
  --hook "index 한 줄 요약" --did "한 것" --next "다음"
```

- `brain-lint`는 `examples/`를 검사하지 않습니다. 대신 회귀 시험이 이 파일들을 빈 저장소에
  넣고 lint를 통과하는지 확인하므로, 스키마가 바뀌면 예시도 같이 깨져서 드러납니다
  (`infra/tests/test_examples.py`).
