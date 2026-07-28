# Research

연구 문서와 실험 기록을 두는 곳이다. **Tier 2** — 시작 절차에서 읽지 않고, 필요할 때만 연다.

## 구조

```text
research/
  {project-slug}/
    overview.md        무엇을·왜·현재 어디까지 (프로젝트마다 1개, 필수)
    {topic}.md         방법·관련연구·실험 기록 등 주제별
```

`overview.md`는 짧게 유지하고, 길어지면 주제별 문서로 쪼갠 뒤 링크한다.

## 규칙

1. **정본을 하나 정한다.** 결론과 최신 수치는 정본 문서 한 곳에만 둔다. 나머지는 링크한다.
   같은 숫자가 두 문서에 있으면 둘 중 하나는 반드시 낡는다.
2. **실행 로그와 결론을 분리한다.** "무엇을 돌렸나"와 "그래서 무엇이 참인가"는 다른 문서다.
3. **주장에는 근거의 종류를 붙인다.** 측정 / 추정 / 미검정 중 무엇인지 적는다.
   특히 "천장이다 · 한계다 · 무의미하다 · N점 우수하다"를 쓰기 전에는
   경계값과 측정 방식을 먼저 확인한다. 지표가 포화된 것과 방법이 실패한 것은 다르다.
4. **원시 데이터·모델 가중치·대용량 산출물은 Git에 넣지 않는다.** 어디에 있는지, 어떻게
   재생성하는지만 적는다. 개인정보·API 키·피험자 데이터는 공개 저장소에 절대 넣지 않는다.
5. **재현 정보를 남긴다.** 코드 커밋 해시, 라이브러리 버전 핀, 시드, 프롬프트 원문.
   "그때 돌렸을 때는 됐다"는 6개월 뒤 아무 값어치가 없다.

## 템플릿

```sh
mkdir -p research/my-project
cp research/_template/overview.md research/my-project/overview.md
cp research/_template/experiment.md research/my-project/exp-001-baseline.md
```

## Task·Session과의 관계

- `research/`는 **알아낸 것**을 쌓는다. `tasks/`는 **할 일**, `system/sessions/`는 **한 일**이다.
- 실험을 돌리는 행위는 task, 그 결과 해석은 research 문서, 그날의 진행 요약은 session이다.
- 프로젝트를 넘어 재사용되는 교훈은 `knowledge/`로 올린다.
