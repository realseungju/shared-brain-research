# Skills

사용자 정의 스킬을 두는 확장점이다.

## 포함된 스킬

| 스킬 | 언제 |
|---|---|
| [`experiment-claim-check`](experiment-claim-check/SKILL.md) | 실험 수치를 claim·해석·session 요약에 **주장으로 기록하기 직전** |

`research-lint`는 근거의 *존재*를 검사하고, 이 스킬은 근거의 *타당성*을 점검한다.
두 층은 대체 관계가 아니다 (ADR-007).

## 새 스킬

`_template/SKILL.md`를 복사해 이름·설명·절차·금지를 채운다.
각 AI 도구가 스킬을 발견하는 위치는 다를 수 있으므로 해당 도구 문서를 확인한다.
