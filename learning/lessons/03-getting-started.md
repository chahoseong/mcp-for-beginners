# Module 03 — Getting Started 수업 요약

- 현재 원문: [Client README](../../03-GettingStarted/02-client/README.md)
- 완료 원문: [첫 서버 README](../../03-GettingStarted/01-first-server/README.md)
- 실습 위치: [practice/](../../03-GettingStarted/01-first-server/practice/)
- 진행: 01-first-server의 Python 학습·Inspector 실습·응용 Tool 과제를 완료했다(2026-10-02). Module 03 전체 완료를 뜻하지 않는다.
- 완료 범위: 서버 구조와 stdio, 가상환경·SDK 준비, add Tool·greeting Resource 구현, Inspector 연결·조회·호출·읽기, divide 설계·구현과 정상·오류 입력 테스트.
- 다음 행동: 제공된 client_example_python.py를 기준으로 Client의 역할과 비동기 문법을 설명하고, 이 단원의 서버 경로·최신 Client API에 맞춰 단계적으로 실습한다. 전체 Client migration은 아직 수행하지 않았다.

## Client 단원 준비 — 2026-10-02

- 학습자가 client_example_python.py를 활용하고 최신 SDK로 이전 단원과 독립된 실습을 하도록 요청했다. README와 예제 전체를 읽고 학습 계획을 설명했다.
- 에이전트가 02-client/.venv를 만들고 mcp[cli] 2.2.0을 설치했다. 02-client/requirements.txt에 버전을 고정했다. 이전 단원 환경·서버는 변경하지 않았다.
- 이 단원의 [solution/python/server.py](../../03-GettingStarted/02-client/solution/python/server.py)를 MCPServer로 migration하고 직접 실행용 mcp.run() 블록을 추가했다.
- 에이전트의 일회성 stdio 확인에서 프로토콜 2026-07-28, add 목록·add(3,4) 결과 7, greeting 템플릿·greeting://Mina 읽기 성공을 확인했다. 이는 환경 준비 검증이며 학습자의 Client 구현·이해 근거로 평가하지 않는다.
- 예제 Client는 아직 이전 서버 경로와 ClientSession.initialize를 사용하고 존재하지 않는 계산 기능도 호출한다. 이 단원 서버의 기본 기능은 add와 greeting뿐이다. Resource Template 조회와 is_error 확인도 수업 중 보완한다.
- 이전 단원 실습은 practice/.venv의 v1.30.0, 이번 단원은 02-client/.venv의 v2.2.0이다. 최신 원문 교정은 공식 migration·Client 문서와 설치된 API를 기준으로 구분하여 가르친다.

## 실습 결과와 평가 한계

- Python 3.12.10, SDK 1.30.0을 사용했다. 제출 출력에서 가상환경 Python 경로와 FastMCP import 성공을 확인했다.
- Inspector Connected, add(7,9)의 result 16, greeting://Mina의 URI·text/plain·Hello, Mina! 결과를 제출했다.
- 직접 작성한 divide에서 decorator·int 입력·float 반환형·docstring·return a / b를 확인했다. 안내한 입력 (3,2),(-9,3),(0,5)의 결과를 1.5,-3,0으로 보고했다(원시 응답 미제출).
- add 오류에는 a의 Field required와 input_value={'b':7}이 나타났고, divide(5,0)에는 division by zero가 나타났다. 학습자는 전자는 입력 검증으로 본문이 실행되지 않으며 후자는 본문 계산 단계라고 설명했다. Inspector가 내부 중단 단계를 직접 알려주지 않는다는 한계도 지적했다.
- 한글 ㅇ을 입력한 add 테스트에서 검증에 a가 전달되지 않았다. 입력칸 또는 요청 구성 과정의 정확한 누락 경위는 미확인이다. 문자열 자료형 검증 사례로 일반화하지 않는다.
- 예제 실습은 안내를 따른 경험이다. divide 기본 설계·본문은 학습자가 작성했으나 등록 방식·테스트 입력은 안내했다. 모든 개념의 독립 이해나 운영 능력을 확인한 것은 아니다.

## 원문 주의사항과 재개 시 유의점

- HTTP·포트 설명과 이 예제의 stdio를 구분한다. Python 최종 예제는 Tool·Resource이며 Prompt 구현은 포함되지 않는다.
- 2026-10-02 공식 문서 확인 후 원문의 FastMCP에 맞춰 mcp[cli]<2를 사용했다. Inspector는 원문 사용 흐름에 맞춰 v1-latest 태그를 지정했다. 후속 설치 시 버전을 다시 확인한다.
- Inspector 화면 소개 전 조작 질문을 했던 맥락 부족을 보완했다. UI·용어를 먼저 설명하고 미응답을 이해 부족으로 판단하지 않는다.
- 종료 코드 0과 기능 정확성 구분은 이전 단원의 미해결 항목으로 남는다. 이번 테스트로 종료 코드 해석을 평가한 것은 아니다.

## 관련 기록

- [Tools, Resources, Prompts](../understanding/tools-resources-prompts.md): 구현 경험, divide 설계·구현과 오류 구분의 최신 근거.
- [Transports](../understanding/transports.md): stdio 대기 상태와 오류 계층의 최신 근거.
- [정리 전 상세 기록](history/03-first-server-2026-10-02.md): 입력 누락·질문 맥락 보완 등 당시 경위가 필요한 경우에만 읽는다.
- 2026-10-02: 단원 완료 시 누적 기록을 history에 보존하고 현재 문서를 재개 요약으로 정리했다. 재구성만으로 이해 상태를 변경하지 않았다.
