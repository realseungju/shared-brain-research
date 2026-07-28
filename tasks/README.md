# Tasks

```text
backlog/ → doing/ → done/
```

연구 실행·구현·검증처럼 완료 조건이 있는 작업을 둔다. 질문과 결과는 `research/`, 미팅
출처는 `feedback/`에 두고 task에서는 그 경로를 링크한다.

새 task는 AI가 생성기를 사용해 만든다.

```sh
python infra/new-task.py {slug} --title "제목"
```

파일 생성 뒤 성공 기준과 관련 experiment·feedback 경로를 채운다. `doing/`으로 옮길 때
agent·started를, `done/`으로 닫을 때 finished·closed_reason·실제 result를 기록한다.
