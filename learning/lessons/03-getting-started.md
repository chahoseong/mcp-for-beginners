# Module 03 — Getting Started 수업 요약

- 현재 원문: [VS Code README](../../03-GettingStarted/04-vscode/README.md)
- 완료 범위: 01-first-server(2026-10-02), 02-client·03-llm-client(2026-10-04), 04-vscode(2026-10-05)의 Python 핵심 학습·실습. Module 03 전체 완료를 뜻하지 않는다.
- 다음 행동: 다음 단원 시작 요청 시 05-stdio-server README를 읽고 기존 경험과 새 범위를 구분해 계획한다.

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

## LLM Client 단원

- 완료: 2026-10-04. 실습은 03-llm-client/.venv·MCP 2.2.0·openai 3.24.0과 solution/python/server.py·client.py이다. NVIDIA hosted API의 deepseek-ai/deepseek-v4.1-flash를 AsyncOpenAI로 호출하며 NVIDIA_API_KEY는 uv run --env-file로 전달한다.
- 서버를 MCPServer로 migration하고 전체 input_schema를 모델용 parameters에 보존했다. required 누락의 모델 입력·서버 실패 영향을 설명했다. get_stock 사례에서 모델 선택·Application 실행·결과 전달 역할을 설명했으며 최신 평가는 Python Client 기록에 둔다.
- 기본 흐름: list_tools → 모델용 정의 변환 → 첫 모델 tool_calls → MCP 실행 → assistant 호출 메시지와 tool_call_id가 있는 tool 결과 메시지 보존 → 두 번째 모델 최종 답변. add(20,2) 결과 22와 최종 답변을 제출했다.
- 응용: 학습자가 subtract(a:int,b:int)->int를 등록·구현했다. 두 Tool이 등록된 상태에서 subtract(141,20) → 121, add(141,20) → 161의 선택 이름·인자·is_error=False·최종 답변을 각각 제출해 기본 과제를 완료했다. Tool 선택 검증용 입력·출력 코드는 안내했으며 전체 독립 구현으로 일반화하지 않는다.
- 교재 교정·보충: 구형 ClientSession·inputSchema를 최신 API로 바꾸고 required 누락을 교정했다. 최종 결과 재전달은 Python 원문에 추가한 범위이며 세 학습 목표에 맞춰 핵심 실습에 포함하는 데 동의했다.
- 한계: 호출 ID 연결은 실제 ID 보존을 보충한 뒤 뒤바뀐 결과를 진단하여 이해 확인했다. 복수 호출 구현·실패 결과의 모델 재전달·추가 호출 반복은 실행 확인하지 않았다. 현재 두 번째 응답이 추가 호출을 요청하면 출력만 한다.
- [상세 이력](history/03-llm-client-2026-10-04.md)은 구체적 단계·교정 경위가 필요한 경우에만 읽는다.

## VS Code 단원

- 완료: 2026-10-05. VS Code 1.140.0·x64, 저장소 전체 workspace, Copilot Chat을 사용한다. 기존 03-llm-client/.venv와 solution/python/server.py를 재사용했다. 새 Server·LLM Client를 만들지 않았다.
- 실제 설정: workspace .vscode/mcp.json의 servers.calculator에 stdio·가상환경 Python·server.py 절대 경로를 지정했다. 처음 사용한 .mcp.json은 .mcp.json.backup에 보존했다. 현재 기본 설정을 바꾸지 않고 이 재개 위치를 따른다.
- 진단: 같은 실행 경로의 Python Client는 정상 연결됐으나 초기 VS Code 시작·출력에 문제가 있었다. 호환 설정에서 로그가 표시되어 Chat session runtime 생성 전 시작 불가·Send a message first 오류를 확인했다. Chat 메시지를 먼저 보낸 뒤 시작 성공을 보고했다. 설정 형식 변경과 초기 출력 문제의 인과는 확정하지 않는다.
- 실행 검증: Chat에는 serverName/toolName 메타데이터만 표시되었다. 에이전트가 서버 함수에 파일 logger를 추가했고 tool_calls.log의 add(34,19)=53·subtract(87,29)=58 새 행과 Copilot 최종 답변을 확인했다. 에이전트 확인 호출 add(1,2)=3은 학습자의 Copilot 실행 증거와 구분한다.
- 이해 확인: 다른 MCP 앱에서도 Client를 통해 기존 Server를 재사용할 수 있다고 설명했다. 마지막 오류 사례에서 최종 답변부터 거꾸로 추적하고 서버 로그·반환62를 근거로 subtract(50,12)의 계산 오류를 판단했다. 최신 평가 근거는 Architecture·Python Client 기록을 따른다.
- 완료 범위·한계: 등록·시작·중지/재시작·로그 확인을 안내에 따라 수행했고 두 Tool의 실제 실행을 확인했다. 독립 설정 작성·버그 수정·종료 코드 해석까지 평가하지 않는다. Resources·Prompts 사용은 선택 확장으로 남겼다.
- [상세 진단 이력](history/03-vscode-2026-10-05.md)은 구체적인 실패·교정 경위가 필요한 경우에만 읽는다.

## 평가 한계와 원문 교정

- 안내된 예제·입력을 따른 실습과 독립 적용을 구분한다. 과제 입력·이름은 기존 예제와 같고 예외 범위는 보완 후 확인했다. 모든 개념·운영 능력을 확인한 것은 아니다.
- async with·asyncio.run의 독립 설명과 종료 코드0 해석은 미확인이다. VS Code 단원의 로그 사례에서 실제 실행과 계산 정확성 구분은 진단 답변으로 확인했다.
- SDK v1·v2 차이와 MCP 프로토콜 버전을 구분한다. 원문의 ClientSession.initialize 중첩 연결을 최신 Client로 보완했다. Resource 결과·템플릿 조회와 is_error 처리도 설치된 API를 기준으로 교정했다.
- Inspector UI를 설명하기 전 조작을 질문했던 맥락 부족을 보완했다. 필요한 UI·용어를 먼저 가르친다.

## 관련 기록

- [Python Client](../understanding/python-client.md): 비동기 문법·Client 오류 처리·실습 근거.
- [Tools, Resources, Prompts](../understanding/tools-resources-prompts.md): Resource 발견·읽기, divide 설계·구현과 최신 평가.
- [Transports](../understanding/transports.md): stdio 대기 상태와 오류 계층의 근거.
- [첫 서버 상세 이력](history/03-first-server-2026-10-02.md), [Client 상세 이력](history/03-client-2026-10-04.md): 구체적 교정 경위가 필요한 경우에만 읽는다.
- 2026-10-04: Client 단원 완료 시 누적 요약을 history에 보존하고 현재 문서를 두 단원의 재개 요약으로 정리했다. 이동만으로 평가를 변경하지 않았다.
- 2026-10-04: LLM Client 완료 시 단계별 누적 요약을 history로 보존하고 환경·실행 근거·교정·한계를 재개 요약으로 정리했다. 이동만으로 이해 평가를 변경하지 않았다.
- 2026-10-05: VS Code 완료 시 상세 실패·교정 기록을 history로 보존하고 현재 설정·실행 근거·한계를 재개 요약으로 정리했다. 파일 이동만으로 이해 평가를 변경하지 않았다.


