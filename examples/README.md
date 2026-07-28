# Examples — Shared Brain Research

**읽기용 예시입니다. 여기 있는 파일은 live 기록이 아닙니다.**

`system/sessions/`와 `tasks/done/`을 채워 두면 이 저장소를 템플릿으로 복제한 사람의
Tier 0에 남의 기록이 그대로 섞입니다. 그래서 실제 산출물이 어떤 모양인지 보여주는 용도로만
여기에 두고, live 트리는 빈 상태로 배포합니다.

| 경로 | 무엇 |
|---|---|
| `research/demo-vision/` | 질문→실험→근거→supported claim을 완주한 가상 연구 |
| `feedback/meetings/` | accepted·rejected·deferred를 한 번씩 보여주는 redacted 미팅 |
| `sessions/` | Claude Code가 계획하고 Hermes가 이어받는 두 session |
| `tasks/` | experiment 결과 경로로 닫힌 task |
| `cross-agent-demo/` | 교차 AI 인계 재현 절차 |

## 주의

- 수치·commit·dataset은 전부 가상 fixture다. 실제 모델 성능이나 연구 결과가 아니다.
- 파일을 그대로 복사해 live 기록으로 쓰지 말고 생성기로 만든다:

```sh
python infra/new-task.py {slug} --title "제목"
python infra/new-session.py {slug} --agent {이름} --tags {태그} \
  --hook "index 한 줄 요약" --did "한 것" --next "다음"
python infra/new-experiment.py {slug} --project {project} \
  --title "실험 제목" --hypothesis {가설}
python infra/new-meeting.py {slug} --title "미팅 제목" --project {project}
```

- lint는 `examples/`를 live 기록으로 검사하지 않는다. 대신 회귀 시험이 이 파일들을 빈 저장소의
  live 위치에 넣고 `research-lint`를 통과시키므로, 스키마가 바뀌면 예시도 같이 깨져서 드러난다
  (`infra/tests/test_examples.py`).
