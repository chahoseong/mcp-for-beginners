# stdio Server — 2026-10-05 상세 실습·교정 이력

단원 완료 시 누적 내용을 보존했다. 아래 당시의 다음 행동·미확인은 최신 상태가 아니다. 최신 재개 위치는 [Module 03](../03-getting-started.md), 개념 평가는 [Transports](../../understanding/transports.md)와 [Python Client](../../understanding/python-client.md)를 따른다.

## stdio Server 단원 계획

- 2026-10-05 첫 수업: subprocess·표준 스트림·줄 구분·로컬/원격 transport 선택을 설명했다. 학습자가 stderr INFO 로그와 is_error=False·result=15의 근거를 각각 구분했다. 설명 직후 사례 해석이며 최신 이해·한계는 Transports 기록에 둔다. 이후 uv 별도 환경·SDK 설치 명령을 안내했다.
- 2026-10-05: README·Python solution과 공식 2026-07-28 transport·Inspector·VS Code 문서를 검토했다. 목표는 stdio 서버 구현, Inspector 진단, VS Code 사용, 현재 transport 선택 이유이다.
- 환경·서버 확인: 학습자가 05-stdio-server/.venv 경로, Python 3.12.10·MCP 2.2.0·MCPServer import 성공 출력을 제출했다. 네 Tool·stderr logging·명시적 stdio 실행 예제를 작성한 파일을 확인했고 INFO Starting stdio-practice·대기 상태를 보고했다. Node v24.13.1을 확인했다.
- 정상 호출 확인: 학습자가 Inspector의 greeting(Mina)=Hello, Mina!, sum(8,13)=21, product(7,6)=42와 server_info의 네 필드를 제출했다. 안내된 입력의 정상 호출 실습이며 독립 구현 평가와 구분한다. UI 입력 검증으로 요청이 차단되는 경우를 피하고자 다음 필수 a 누락 호출은 Inspector CLI로 안내한다. CLI는 별도 프로세스를 실행하므로 Web Inspector의 로그와 혼동하지 않는다.
- 오류 호출 확인: b=13만 전달해 SDK의 a 필수 누락 검증 실패·isError:true 응답, Inspector의 tool_is_error·종료 코드5를 제출했다. 안내 실행의 오류 경로를 확인했으며 독립 종료 코드 해석은 아직 확인하지 않았다. 입력 검증·도구 결과·CLI 진단을 구분해 설명하고 정상 종료와 계산 정확성의 다른 사례를 확인한다.
- 진단 후속 확인: 학습자는 예상값 비교 후 서버 로그로 Tool 호출·결과를 확인한다고 설명했다. 집중 질문 후 product(4,5)의 예상20과 로그9를 근거로 Tool 구현을 점검한다고 답했다. 종료 코드0을 크래시 없이 실행된 의미로 답했으며 Inspector의 실패 분류·계산 정확성 보장의 차이를 보충한다. 최신 근거와 한계는 Python Client 기록에 둔다. 다음 stdout/stderr 비교 실습은 안내 단계이다.
- 출력 비교·SDK 교정: 두 경우 모두 DEBUG 로그·result21·isError:false·종료 코드0을 제출했다. 저장된 stderr print를 확인했다. 설치된 SDK 2.2.0의 stdio_server가 일반 fd1을 stderr로 돌리는 보호 동작을 확인했다. 함수 print가 실제 MCP 채널을 오염시키는 실험이라는 초기 전제를 버전 보충으로 교정하며 Client가 오류를 무시했다고 단정하지 않는다. 보호 구현의 원리는 보충 설명이며 이해 평가를 올리지 않는다. 다음 VS Code 설정·호출을 안내한다.
- VS Code 확인: .vscode/mcp.json에 기존 calculator를 보존하고 stdio-practice의 가상환경 Python·server.py 절대 경로를 추가한 파일을 확인했다. DEBUG print 제거를 확인했다. 학습자가 calculate_product Completed 카드(serverName·toolName)와 최종52를 제출했다. 카드에는 인자·서버 로그가 없으므로 a=13,b=4의 별도 서버 실행 로그 증거와 동일시하지 않는다. 외부 API Tool 과제를 시작한다.
- 외부 API 실패·교정: 학습자가 get_random_joke의 isError:true와 기본 메시지를 제출하고 이어 HTTP403·RuntimeError·UnexpectedToolError traceback을 제공했다. 예제 그대로 작성한 코드를 확인했다. 에이전트의 일반 네트워크 허용 실행에서도 기본 urllib 요청403을 재현했고 User-Agent=mcp-stdio-practice/1.0·Accept=application/json 요청은 JSON value 읽기에 성공했다. 이것은 에이전트 확인이며 학습자 Tool 성공은 아직 없다. SDK 2.2.0에서 예상 실패는 ToolError로 메시지를 전달하고 RuntimeError는 예상치 못한 예외로 취급해 상세 메시지를 숨긴다는 설치 코드 근거로 예제를 보완한다. 403의 서버 내부 정책까지 단정하지 않는다.
- 외부 API 성공: Request 헤더·ToolError를 반영한 코드를 확인했다. 학습자가 재호출 성공과 농담 본문을 제출했다. 안내된 구현·실행이며 독립 API Tool 설계로 일반화하지 않는다. 마지막 transport 구분 답변은 아직 받지 않았다.
- 순서: subprocess·stdin/stdout/stderr·줄 단위 JSON-RPC → 별도 .venv·practice/server.py의 SDK 2.2.0 MCPServer와 네 가지 기본 Tool → Inspector 목록·호출·오류·로그 확인 → 기존 .vscode/mcp.json에 별도 서버 등록 → 원문 과제의 외부 API 호출 Tool 한 개.
- 교정: 본문 Server.tool·stdio_server(server)의 API 혼합, Python 3.8 요구조건, stdio에 웹 서버가 필요하다는 문장, VS Code 절의 Claude 설정을 수정한 수업 예제를 사용한다. solution의 저수준 list_tools/call_tool handlers는 본문과 다르므로 모든 저수준 코드를 동일한 오류로 취급하지 않는다.
- 보충: stdout은 MCP 메시지 전용이고 stderr에는 일반 로그도 가능하다. 로컬 subprocess에는 stdio, 원격에는 Streamable HTTP를 비교하며 구형 HTTP+SSE와 SSE 기술 자체를 구분한다. Inspector v2를 사용하고 Node 요구조건을 확인한다. get_server_info는 사용자 정의 Tool이며 공식 서버 발견 응답과 구분한다.
- VS Code debugger는 현재 debugpy와 Inspector가 실행한 동일 프로세스에 attach해야 한다는 점을 설명한다. breakpoint 실습은 선택 범위로 두고 기본 Inspector 진단을 먼저 완료한다. 외부 API 과제에는 GET·JSON 추출·timeout·기본 실패 처리만 필요한 만큼 설명한다.


## 마지막 확인과 완료

- 학습자는 Inspector↔server.py는 같은 컴퓨터에서 실행하고 transport=stdio를 지정한 stdio 통신, server.py↔외부 API는 네트워크상 HTTP API 통신이라고 설명했다. 코드·배치 상황의 근거를 함께 제시했다. 실제 URL은 HTTPS이며, 같은 컴퓨터라는 조건만으로 stdio가 결정되지는 않고 Client의 실행·설정이 근거임을 보충한다.
- 네 학습 목표의 기본 실습과 외부 API 과제를 완료했다. 안내된 구현·교정을 독립 설계로 일반화하지 않는다. breakpoint attach는 선택 항목으로 실제 수행하지 않았다. ToolError 교정 후 예상 실패의 메시지 전달 경로는 재실행하지 않았다.
- API 호출 성공 후 농담 본문은 원문 표현 그대로 제공되었으며 농담의 사실 정확성을 평가한 것은 아니다.

