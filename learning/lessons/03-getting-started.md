# Module 03 — Getting Started 수업 요약

- 현재 원문: [Testing & Debugging README](../../03-GettingStarted/08-testing/README.md), 핵심 실습 완료(2026-10-05).07 Foundry Toolkit은 선택으로 남기고 건너뛰었다.
- 완료 범위: 01-first-server(2026-10-02), 02-client·03-llm-client(2026-10-04), 04-vscode·05-stdio-server·06-http-streaming(2026-10-05)의 Python 핵심 학습·실습. Module 03 전체 완료나 모든 개념의 독립 이해를 뜻하지 않는다.
- 다음 행동: 학습자가 다음 단원을 지정하면 해당 README를 검토한다. 테스트 접근 선택은 부분 이해로 이어가며 실제 HTTP 진단 도구 선택은 다음 관련 실습에서 재확인한다.

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

## stdio Server 단원

- 완료: 2026-10-05. 별도 05-stdio-server/.venv(Python 3.12.10·MCP 2.2.0), practice/server.py, Node v24.13.1·Inspector v2.9.0을 사용했다. MCPServer의 명시적 stdio·stderr logger와 네 Tool을 작성했다.
- Inspector: greeting(Mina), sum(8,13)=21, product(7,6)=42, server_info 결과와 필수 a 누락 실패(isError:true·CLI 종료 코드5)를 제출했다. 로그·실패 여부·계산 정확성을 구분했으며 product(4,5)의 로그9 사례는 집중 후속 질문 후 구현 점검을 제안했다. 종료 코드0의 정확성 한계는 보충한 범위이다.
- SDK 교정: 함수 내부 기본 print·stderr print 모두 정상 결과21·종료 코드0이었다. SDK 2.2.0 stdio의 일반 stdout→stderr 보호 구현을 확인해 초기 실험 전제를 교정했다. 보호 원리를 독립 설명한 것은 아니며 로그의 명시적 stderr 지정을 유지한다.
- VS Code: .vscode/mcp.json의 기존 calculator를 보존하고 stdio-practice를 추가했다. DEBUG print 제거를 확인했고 Copilot의 calculate_product 호출 카드와 최종52를 제출했다. 카드의 serverName/toolName을 실제 인자·서버 로그와 동일시하지 않는다.
- 원문 과제: 외부 농담 API Tool을 추가해 HTTP403 traceback을 확인했다. 에이전트 재현·헤더 요청 검증 후 User-Agent·Accept와 ToolError로 보완했고 학습자가 재호출 성공·농담 본문을 제출했다. RuntimeError의 일반 메시지와 예상 실패용 ToolError의 차이를 SDK 코드로 설명했다.
- 마지막 확인: 학습자는 Inspector↔Server의 stdio 지정과 Server↔외부 API의 HTTP 통신을 코드·배치 상황으로 구분했다. 개념의 최신 근거는 Transports에 둔다. 같은 컴퓨터만으로 transport가 결정되지 않고 외부 URL은 HTTPS라는 점을 보충했다.
- 원문 보완·한계: Python 본문의 API 혼합·3.8 요구조건·웹 서버 필요 문장·Claude 설정을 수업에서 교정했다. 로컬 stdio/원격 Streamable HTTP와 구형 HTTP+SSE를 구분했다. 기본 구현·디버깅·VS Code 사용·transport 구분과 과제를 완료했으나 독립 API 설계·bug 수정·breakpoint attach·ToolError 실패 재실행까지 평가하지 않는다.
- [상세 이력](history/03-stdio-server-2026-10-05.md)은 SDK 출력 보호·CLI 오류·HTTP403 교정 경위가 필요한 경우에만 읽는다.

## HTTP Streaming 단원

- 실습: 별도06 .venv(Python3.12.10·MCP2.2.0), practice/http_server.py·http_client.py·mcp_server.py·mcp_client.py. 일반 HTTP SSE와 MCP Streamable HTTP를 분리했다.
- 실행·이해: 일반 HTTP의 약1초 간격 출력과 response.text 전체 출력5.06초를 비교해 Client 읽기 차이를 설명했다. MCP URL 연결·add21, 세 진행 알림1.02/2.04/3.05초·최종3.11초를 확인했다. 진행3/3 뒤 저장 실패 사례에서 최종 오류를 근거로 전체 실패를 판단했다.
- 원문 과제 완료: 학습자가 files:list[str]·enumerate·len(files)·join 반환을 구현하고 네 항목·두 항목의 진행량·최종 결과를 제출했다. 두 번째 목록에 남은 항목은 피드백 후 제거했다. 실제 파일 I/O는 없고 기존 코드·요구사항 기반 수정이다.
- 보안: CORS의 웹페이지/서버 배경과 허용 대상 혼동을 그림으로 보충했다. 설명 반복 질문은 폐기했고 그림 뒤 이해했다는 자기 보고만으로 상태를 올리지 않았다. 이후 팀 서버 사례에서 사용자 인증·요청 권한 검사를 제안했다. 최신 평가·한계는 Security 기록을 따른다.
- 교정·범위: ctx.info 로그 대신 report_progress/progress_callback, async의 time.sleep 대신 asyncio.sleep, Requests 줄 읽기 buffering·경과 시간 관찰을 보충했다. 마지막 migration 개요는 현재 요청별 POST·SDK 호환·Client URL·알림/최종 결과 점검으로 설명한다. 실제 구형 Client migration·TLS/인증/CORS 배포는 미실습, migration 독립 설명은 미평가이다. Parallel hosted 연결은 선택 확장이다.
- [상세 이력](history/03-http-streaming-2026-10-05.md)은 초기 계획·관찰 값·CORS 교정 경위가 필요한 경우에만 읽는다.

## Foundry Toolkit 진행 여부 검토

- 결정: 2026-10-05 학습자가 선택으로 남기고 건너뛰기로 했다. 설치·실습 없이 문서 검토만 수행했으며 학습 목표 달성이나 개념 이해 확인을 의미하지 않는다. 아래 권고는 재개할 때 참고한다.
- 2026-10-05: README·solution의 세 목표(특정 Toolkit 연결·agent 도구 설정·자연어 사용)를03 LLM Client/04 Copilot 경험과 비교했다. 새 핵심 MCP 개념보다 별도 Host UI·모델/지침 설정·복수 도구 연계 관찰에 가치가 있어 기존 서버 재사용 축약 실습을 권한다. 학습자의 진행 결정·실습은 아직 없다.
- 최신 공식 문서는 local prompt의 외부 모델·local MCP와 NIM/Custom BYOM을 지원하므로 GPT-5.1 Foundry 배포는 이 목표의 필수조건이 아니다. 사용 중인 DeepSeek 모델의 Toolkit Tool Calling·SDK2.2/2026-07-28 상호운용은 실제 확인이 필요하다. README UI 경로는 최신 문서와 다르고 FastMCP 예제를 현재 MCPServer 환경에 맞춰야 하며 F5는 생성 프로젝트 launch 설정을 확인해야 한다.
- 진행한다면 모델 연결→기존 서버·도구 선택과 지침 설정→multiply 결과를 subtract에 전달하는 의존 호출 검증→새 Tool 추가·발견 확인으로 축약한다. 설치·Azure 생성·API 실행은 하지 않았다.

## Testing & Debugging 단원

- 핵심 실습 완료: 2026-10-05. 별도08 .venv(Python3.12.10·MCP2.2.0·pytest9.1.1), practice/server.py·divide_request.json, tests/test_calculator.py·test_mcp_server.py. 단원 완료와 모든 개념의 독립 이해는 구분한다.
- 실행: Inspector 세 divide 사례 일치 보고, pytest 단위 세 PASSED→임시 // 오류 실패→/ 복구 후 통과, AnyIO/asyncio의 Client(server) 통합 네 PASSED, curl.exe의 실제 /mcp 호출 HTTP200·isError:false·result2.5를 확인했다. 학습자가 add 단위 테스트를 추가해 전체 여덟 PASSED를 제출했다.
- 확인: 실제2·기대2.5 실패 보고, 기대와 다른 예외의 테스트 실패, 도구 등록 decorator만 제거할 때 단위 통과·목록 검사 실패를 설명했다. 계산 전 ToolError 분기와 실제 ZeroDivisionError 이름은 보충했다. 최신 평가 근거는 Python Client 기록에 둔다.
- 원문 교정: 표준 /mcp POST·현재 버전/메서드/이름 헤더·본문 메타데이터, MCPServer/Client public API·AnyIO asyncio backend로 교정했다. in-process 통합을 실제 HTTP/stdio 검사로 일반화하지 않는다. 이전 CLI 경험으로 중복 호출을 생략했고 버그 재현·회귀 검사를 보충했다. cursor 예제는 SDK 참고로 두었다.
- 한계: 단위 방식 선택 이유는 별도 근거 없이 선택했다고 답했다. HTTP 실패 사례의 검사 범위 한계·실제 실행 방향은 맞게 설명했으나 도구 선택은 몰라 curl.exe/Inspector HTTP 진단을 보충했다. 접근 선택은 부분 이해, raw 요청 독립 구성·실제 HTTP 실패 진단은 미평가이다. 유한 테스트의 보장 범위·전수 검사 예시는 보충만 했고 실행/독립 설명은 미확인이다.
- [상세 이력](history/03-testing-2026-10-05.md)은 초기 계획·순서 변경·실패 분석·보충 경위를 확인할 때만 읽는다. 2026-10-05 완료 시 누적 기록을 이동하고 요약·부모 INDEX를 갱신했으며 이동만으로 이해 상태를 바꾸지 않았다.

## 평가 한계와 원문 교정

- 안내된 예제·입력을 따른 실습과 독립 적용을 구분한다. 과제 입력·이름은 기존 예제와 같고 예외 범위는 보완 후 확인했다. 모든 개념·운영 능력을 확인한 것은 아니다.
- async with·asyncio.run의 독립 설명은 미확인이다. 종료 코드0은 stdio 단원에서 답변 후 Inspector 정상 처리와 계산 정확성의 차이를 보충했다. 독립 재확인은 남아 있으며 로그 기반 계산 오류 진단의 최신 근거는 Python Client를 따른다.
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
- 2026-10-05: stdio Server 완료 시 누적 실습·SDK 출력 보호·HTTP403 교정 경위를 history로 보존하고 모듈을 재개 요약으로 정리했다. 이동으로 이해 평가를 변경하지 않았다.
- 2026-10-05: HTTP Streaming 마무리 시 누적 계획·관찰·CORS 보충을 history로 보존하고 환경·핵심 실행·과제·보안·한계를 요약했다. 상위 history INDEX를 갱신했으며 이동만으로 평가를 바꾸지 않았다.





