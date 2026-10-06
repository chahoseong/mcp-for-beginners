# Module 01 — Core Concepts 수업 요약

- 원문: [01-CoreConcepts/README.md](../../01-CoreConcepts/README.md)
- 진행: 2026-10-02 개요 학습·원문의 도구 설계 연습 완료. 모든 개념의 독립 이해·구현 확인을 뜻하지 않는다.
- 다룬 범위: 구조와 primitives, JSON-RPC·오류·발견·메타데이터, stdio·Streamable HTTP·SSE, Python 예시, 보안 개요, Tasks, 도구 설계. 설치·코드 실행은 이 모듈에서 하지 않았고 이후 Module 03에서 수행했다.
- 재개 시: 직전 설명의 재현·유도/선택 질문의 한계는 개념 기록을 따른다. 관련 사례에서 필요한 핵심만 재확인한다. 감사·권한 검사·상세 출력 스키마는 실제로 가르친 범위에서 평가하며 원문 개요보다 깊은 구현을 강제하지 않는다.

## 원문 주의사항

- 구형 초기화/세션과 2026-07-28 요청별 메타데이터가 혼재한다. Roots·Sampling·Logging의 deprecated 안내와 현행 기능을 구분한다.
- Python 실행·바인딩된 메서드 예시는 SDK 버전 차이가 있다. 당시 보충 설명을 실행 검증으로 표현하지 않는다.
- 날씨 반환은 고정 예시다. 최대7일·분당10회는 교사의 보충 조건이고 원문 코드의 제약이 아니다. 동의를 모든 호출의 새 확인창 의무로 일반화하지 않는다.

## 필요한 기록

- [Architecture](../understanding/architecture.md): 역할·호출 흐름
- [Tools, Resources, Prompts](../understanding/tools-resources-prompts.md): execute-script 설계의 답변·평가 변화, 제공 방식·Python 등록
- [Transports](../understanding/transports.md): 메시지·전송·버전의 최신 확인
- [Client Primitives](../understanding/client-primitives.md), [Extensions](../understanding/extensions.md): 클라이언트 기능·Tasks
- [Security Index](../understanding/security/INDEX.md): 요청 제한·감사 등 해당 주제 선택
- [2026-10-01 상세 이력](history/01-core-concepts-2026-10-01.md), [2026-10-02 마무리 이력](history/01-core-concepts-2026-10-02.md): 구체적 답변·평가/범위 교정이 필요할 때만 읽는다.

## 구조 변경

- 2026-10-06 반복 평가·수업 변경 이력을 history로 옮기고 최신 개념 기록에 연결했다. 이해 상태·날짜·답변 근거는 보존했다.
