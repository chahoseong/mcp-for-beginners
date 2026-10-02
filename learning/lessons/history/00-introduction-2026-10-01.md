# Module 00 — Introduction 학습 기록

- 원문: [00-Introduction/README.md](../../../00-Introduction/README.md)
- 진행 상태: 핵심 개념 학습과 설계 연습 완료. 전체 문서의 상세 학습은 아직 완료하지 않았다.
- 다룬 범위: MCP의 필요성, 표준화, Host·Client·Server, Tools·Resources·Prompts, Data Layer·Transport Layer, 도구 호출 흐름, 최신 정보 접근, 기능 확장, 설계 연습.
- 남은 범위: Elicitation, Sampling·Roots 및 문서에 명시된 폐기 안내, SSE 관련 설명, 서버 간 연결과 서버 측 LLM 고급 예시의 상세 설명, Privacy 항목.
- Python 서버 구현·실행 실습은 아직 수행하지 않았다.

## 관련 최신 이해 기록

- [Architecture](../../understanding/architecture.md)
- [Tools, Resources, Prompts](../../understanding/tools-resources-prompts.md)
- [Transports](../../understanding/transports.md)

아래 이력은 당시의 학습 결과를 보존한다. 개념의 최신 상태는 위 기록에서 관리한다.

## 학습·복습 이력

### 2026-10-01 — Module 00 입문 핵심 개념

- 원문: [00-Introduction/README.md](../../../00-Introduction/README.md)
- 방식: 작은 단위의 설명, 확인 질문, 학습자의 답변, 필요한 보충 설명 순서로 진행했다.
- 확인된 이해: 도구와 모델의 역할, 인자 설명 방식의 표준화, Host·Client·Server, 호출 요청과 실행의 구분, 통신의 두 층, 재학습 없이 맥락을 전달하는 방식.
- 적용 사례: Python 학습 도우미에 코드 실행 Tool과 코드·학습 노트 Resources가 필요하다고 설계했다.
- 수정·명확화: read_file(path)의 분류는 함수 이름만으로 결정되지 않는다. 도구로 등록해 호출하면 Tool이고, URI로 읽을 수 있게 등록하면 Resource이다. 같은 데이터를 두 방식으로 제공할 수도 있다.
- 선생님 보충: 모델의 실행 예측은 실제 실행 증거와 다르지만 분석 근거가 있을 수 있다. 종료 코드 0은 성공 상태로 종료했다는 증거이며 기능의 정확성을 보장하지 않는다. MCP는 실행·분석의 주체가 아니라 기능과 데이터를 이용하는 통신 규칙이다.
- 보충 예시: 파일 읽기 함수, multiply 호출과 JSON-RPC 요청, 코드 설명 Prompt, Python 학습 도우미 설계 흐름은 원문의 개념을 설명하기 위해 추가한 예시이며 실습한 코드는 아니다.
- 남은 이해 확인: MCP의 전체 역할, 종료 코드 0의 의미, Prompts.
- 다음 단계: 복습 질문으로 이해를 확인하고 입문 문서의 남은 항목을 보충한 뒤 Module 01로 진행한다.
