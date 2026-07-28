# Feedback

미팅·리뷰·사용자 관찰을 출처가 남는 개선 입력으로 관리한다. **Tier 2**이므로 시작할 때
미팅 전체를 읽지 않는다. 현재 처리할 accepted feedback만 `system/context.md`나 task에서 가리킨다.

## 핵심 규칙

미팅 발언은 사실이나 결정이 아니다.

```text
meeting source
→ atomic feedback
→ human triage
→ accepted artifact
→ implementation / experiment
→ validation
```

- AI는 feedback 후보를 만들 수 있지만 `human_approved: yes`를 사람 대신 기록하지 않는다.
- `captured` 이외의 상태에는 `human_approved: yes`가 필요하다. 이 필드는 승인 provenance
  기록이지 승인자 신원을 인증하는 장치가 아니다. lint는 값과 상태 정합성만 검사하므로 실제
  사람 승인은 commit·PR 리뷰나 branch protection으로 확인한다.
- `accepted`에는 실제 task·가설·claim·ADR 경로인 `linked_artifact`가 필요하다.
- `rejected`와 `deferred`에는 분류 이유인 `reason`이 필요하다. `validation`은 반영 뒤 문제
  해결을 확인한 결과에만 쓴다.
- 구현 완료와 문제 해결은 다르다. 확인 결과가 있어야 `validated`다.
- `decision-candidate`는 사람이 승인하고 `system/decisions.md`에 기록한 뒤에만 accepted가 된다.
- meeting을 `closed`로 바꾸려면 `captured`, `accepted`, `deferred` feedback이 남아 있으면
  안 된다. `rejected` 또는 실제 확인까지 끝난 `validated`만 종결 상태다.

정확한 필드와 허용값은 `system/conventions.md`를 따른다.

## Privacy 기본값

새 미팅의 기본 `visibility`는 `redacted`다.

- 공개 Git에는 실명·연락처·비공개 연구정보·원문 녹취를 넣지 않는다.
- 참여자는 이름 대신 역할로 기록한다.
- 녹음·전사본은 외부 위치만 적고 여기에는 요약을 둔다.
- 인용·요약·AI 추론을 `source_mode`로 구분한다.

## 생성

사용자가 명령을 직접 입력하기보다 AI에게 미팅 기록을 정리해 달라고 요청한다. AI가 사용하는
정본 명령:

```sh
python infra/new-meeting.py weekly-review \
  --title "주간 연구 리뷰" \
  --project my-project
```

생성 뒤 `feedback/meetings/` 파일의 atomic feedback을 채우고 사람이 상태를 결정한다.
