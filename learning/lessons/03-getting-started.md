# Module 03 — Getting Started 수업 요약

- 현재 원문: [Client README](../../03-GettingStarted/02-client/README.md)
- 완료 범위: 01-first-server(2026-10-02), 02-client(2026-10-04)의 Python 학습·실습·기본 과제. Module 03 전체 완료를 뜻하지 않는다.
- 다음 행동: 다음 단원 시작 요청 시 [LLM Client README](../../03-GettingStarted/03-llm-client/README.md)를 읽고 Python 학습 계획을 소개한다.

## 첫 서버 단원

- 실습: [practice/](../../03-GettingStarted/01-first-server/practice/), Python 3.12.10·SDK 1.30.0·Inspector v1-latest.
- 가상환경 Python·FastMCP import, add 호출 결과 16, greeting://Mina 읽기를 확인했다. 학습자가 divide를 설계·작성하여 정상 입력과 0 분모 오류를 테스트했다.
- 입력 검증 실패와 본문 계산 오류를 구분했다. Inspector가 내부 중단 단계를 직접 보여주지 않으므로 메시지·코드로 판단하는 한계도 지적했다.
- 숫자 입력칸에 한글을 넣은 사례는 필수 a 누락으로 전달되었다. 정확한 UI 누락 경위는 미확인이며 문자열 자료형 검증으로 일반화하지 않는다.

## Client 단원

- 실습: [02-client/](../../03-GettingStarted/02-client/), 별도 .venv·SDK 2.2.0. [requirements.txt](../../03-GettingStarted/02-client/requirements.txt)에 버전을 고정했다.
- 서버: [solution/python/server.py](../../03-GettingStarted/02-client/solution/python/server.py)를 MCPServer로 migration하고 직접 실행 블록을 추가했다. 이전 단원은 변경하지 않았다.
- 학습 코드: [client_example_python.py](../../03-GettingStarted/02-client/client_example_python.py)를 활용했다. 파일 기준 서버 경로·sys.executable·최신 Client API로 연결하며 stdio 프로토콜은 2026-07-28이다.
- 학습자가 연결·Tool 목록·add 호출의 TextContent와 structured_content·is_error, Resource 목록 0·greeting 템플릿·Mina 인사말 읽기 출력을 제출했다.
- 새 profile 템플릿 사례에서 구체 URI·read_resource·발견과 내용 읽기 차이를 설명하여 적용 확인했다. 두 await의 순서와 get_weather 실패 결과에서 is_error 검사 필요성은 이해 확인했다.
- 필수 a 누락은 is_error=True 결과, 미등록 Resource는 MCPError(-32602)로 처리하는 실습을 수행했다.
- 응용 메서드는 정상 add 결과를 예상값과 비교하고 Resource를 읽는다. 처음에는 Tool 호출이 try 밖에 있었으며 피드백 후 두 요청을 공통 try에 넣었다. 수정한 코드와 에이전트 실행의 True·Hello, Mina!를 확인하여 기본 과제를 완료했다.
- 현재 run은 목록 조회와 응용 메서드만 호출하고 이전 단계 실습 호출은 주석으로 보존되어 있다. 공통 catch의 Resource exception 출력 문구는 추후 MCP exception 등으로 다듬을 수 있다.

## 평가 한계와 원문 교정

- 안내된 예제·입력을 따른 실습과 독립 적용을 구분한다. 과제 입력·이름은 기존 예제와 같고 예외 범위는 보완 후 확인했다. 모든 개념·운영 능력을 확인한 것은 아니다.
- async with·asyncio.run의 의미는 설명·실행했으나 독립 설명은 미확인이다. 종료 코드 0과 기능 정확성 구분도 직접 재확인하지 않았다.
- SDK v1·v2 차이와 MCP 프로토콜 버전을 구분한다. 원문의 ClientSession.initialize 중첩 연결을 최신 Client로 보완했다. Resource 결과·템플릿 조회와 is_error 처리도 설치된 API를 기준으로 교정했다.
- Inspector UI를 설명하기 전 조작을 질문했던 맥락 부족을 보완했다. 필요한 UI·용어를 먼저 가르친다.

## 관련 기록

- [Python Client](../understanding/python-client.md): 비동기 문법·Client 오류 처리·실습 근거.
- [Tools, Resources, Prompts](../understanding/tools-resources-prompts.md): Resource 발견·읽기, divide 설계·구현과 최신 평가.
- [Transports](../understanding/transports.md): stdio 대기 상태와 오류 계층의 근거.
- [첫 서버 상세 이력](history/03-first-server-2026-10-02.md), [Client 상세 이력](history/03-client-2026-10-04.md): 구체적 교정 경위가 필요한 경우에만 읽는다.
- 2026-10-04: Client 단원 완료 시 누적 요약을 history에 보존하고 현재 문서를 두 단원의 재개 요약으로 정리했다. 이동만으로 평가를 변경하지 않았다.
