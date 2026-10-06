# Module 03 — Getting Started 수업 요약

- 원문: [Getting Started](../../03-GettingStarted/README.md), 마지막 수업은 [MCP Apps](../../03-GettingStarted/15-mcp-apps/README.md).
- 현재 위치: 2026-10-06 MCP Apps까지 선택한 수업을 마쳤다. 07 Foundry Toolkit·12 MCP Hosts는 선택 보류, 14 Sampling은 개념·설계 비교 완료/레거시 구현 미실습이다. 모든 단원의 구현 목표나 독립 이해를 완료했다는 뜻은 아니다.
- 다음 행동: 학습자의 요청에 따라 [04-PracticalImplementation](../../04-PracticalImplementation/README.md)을 검토한다. 아직 시작하지 않았다.

## 마지막 실습을 이어갈 때

- 위치: [15/practice](../../03-GettingStarted/15-mcp-apps/practice/), 별도 .venv·mcp2.2.0. ui-basics.html·server.py·check_registration.py, practice/ui의 ext-apps2.0.3·Vite8.3.3·singlefile2.3.3 단일 HTML 빌드를 사용한다. VS Code HTTP3001의 get_server_time·ui://clock/app.html과 화면 버튼의 일반 get_faq를 연결했다. 기존 10 서버는 변경하지 않았다.
- 안내 실행: 최초 시간 표시·버튼 갱신·최초 중복 해소를 확인했다. FAQ 배송·공백/대문자 보증·미등록 항목은 예상 표시를 보고했고 임시 미등록 Tool의 실패 표시·버튼 재활성화·원복 후 정상 조회를 보고했다. 가위바위보·이미지 전송·전체 새 앱 작성은 미실습/미평가이다.
- 재개 판단: [Extensions](../understanding/extensions.md)의 역할·이벤트·호출 경로·기본값/빈 문자열·사용 시점별 최신 답변과 도움 여부를 따른다. 안내 구현 성공을 독립 구현으로 일반화하지 않는다. 후속 Host/Client·iframe·apps.add_html_resource/resource_uri 설명은 독립 답변 평가가 없었다.
- Host 표시·최초 결과 형태의 차이, 시간 전용 fallback, FAQ·실패/복구 경위가 필요하면 [MCP Apps 상세](history/03-mcp-apps-2026-10-06.md)를 읽는다.

## 완료 범위와 필요한 기록 선택

아래는 수업·실습 범위의 라우팅이다. 최신 개념 평가·답변 근거는 understanding의 해당 문서만 읽고, 구체적 시행착오가 필요할 때만 상세 이력을 추가한다.

| 단원·완료일 | 다룬 범위·재사용 위치 | 최신 이해 기록 | 선택 상세 이력 |
| --- | --- | --- | --- |
| 01 first-server · 10-02 | FastMCP1.30.0·Inspector v1, practice에서 Tool/Resource·divide 과제 | [Tools, Resources, Prompts](../understanding/tools-resources-prompts.md) | [첫 서버](history/03-first-server-2026-10-02.md) |
| 02 client · 10-04 | 별도 .venv·SDK2.2.0, client_example_python.py·solution/python/server.py migration, 조회/호출·오류·공통 try 보완 | [Python Client](../understanding/python-client.md), [Resources](../understanding/tools-resources-prompts.md) | [Client](history/03-client-2026-10-04.md) |
| 03 llm-client · 10-04 | .venv·MCP2.2.0·openai3.24.0, NVIDIA hosted DeepSeek·AsyncOpenAI, schema·호출 ID·add/subtract 결과 재전달 | [Python Client](../understanding/python-client.md) | [LLM Client](history/03-llm-client-2026-10-04.md) |
| 04 vscode · 10-05 | 기존03 Python 재사용, .vscode/mcp.json·Copilot·서버 파일 로그; 최초 runtime 오류 후 시작 성공 | [Architecture](../understanding/architecture.md), [Testing & Debugging](../understanding/testing-and-debugging.md) | [VS Code](history/03-vscode-2026-10-05.md) |
| 05 stdio-server · 10-05 | 별도 .venv·practice, stderr logger·Inspector2.9.0·VS Code·외부 농담 API403 보완 | [Transports](../understanding/transports.md), [Tools](../understanding/tools-resources-prompts.md) | [stdio](history/03-stdio-server-2026-10-05.md) |
| 06 http-streaming · 10-05 | 일반 HTTP SSE/MCP Streamable HTTP 비교, practice의 HTTP/MCP 서버·Client·진행 알림·목록 과제 | [Transports](../understanding/transports.md), [CORS/접근 통제](../understanding/security/authentication-and-access.md) | [HTTP Streaming](history/03-http-streaming-2026-10-05.md) |
| 08 testing · 10-05 | practice·tests, pytest 단위/Client(server) 통합·실제 curl HTTP·버그 재현/복구·add 추가 | [Testing & Debugging](../understanding/testing-and-debugging.md) | [Testing](history/03-testing-2026-10-05.md) |
| 09 deployment · 10-05 | 별도09 practice·Docker v1/v2·Render 원격 정상/오류; Azure 비교만 | [Deployment](../understanding/deployment.md) | [Deployment](history/03-deployment-2026-10-05.md) |
| 10 advanced · 10-06 | 별도 .venv·practice의 low-level registry·엄격 검증·multiply·Resource/Prompt | [Tools, Resources, Prompts](../understanding/tools-resources-prompts.md) | [Advanced](history/03-advanced-2026-10-06.md) |
| 11 simple-auth · 10-06 | Bearer/JWT HTTP·claim 실패·scope/RBAC·검사 순서, OAuth 그림 개요; 실제 OAuth 획득/갱신 미실습 | [인증·접근 통제](../understanding/security/authentication-and-access.md) | [Simple Auth](history/03-simple-auth-2026-10-06.md) |
| 13 inspector · 10-06 | 기존10 서버·stdio·Inspector2.9.0, 도구 실패/Resource/Prompt·UI/CLI 교정·가상 진단 | [Testing & Debugging](../understanding/testing-and-debugging.md) | [Inspector](history/03-inspector-2026-10-06.md) |
| 14 sampling · 10-06 | Server 생성 요청과 직접 API 구조 비교·상품 설명 설계, 레거시/새 NIM 구현 미실습 | [Client Primitives](../understanding/client-primitives.md) | [Sampling](history/03-sampling-2026-10-06.md) |
| 15 mcp-apps · 10-06 | Python 서버·최소JS 화면·시간/FAQ·실패/복구·사용 시점 비교 | [Extensions](../understanding/extensions.md) | [MCP Apps](history/03-mcp-apps-2026-10-06.md) |

## 선택 보류와 이어갈 확인

- 07 Foundry Toolkit(10-05)·12 MCP Hosts(10-06)는 학습자 선택으로 보류했다. 설치·이수로 표시하지 않는다. 실제 다른 Host가 필요할 때 기존 Python 서버로 축약 재사용을 검토한다. 당시 검토·제품 안내는 [선택 단원 이력](history/03-optional-units-2026-10-06.md)에 보존했으며 재개 시 공식 문서를 다시 확인한다.
- 비동기 연결 관리, LLM 실패 결과 재전달·복수/반복 호출은 [Python Client](../understanding/python-client.md)의 미해결 확인을 따른다. 종료 코드0의 정확성 한계·테스트 접근 선택은 [Testing & Debugging](../understanding/testing-and-debugging.md)의 최신 근거를 따른다. 모듈 완료로 미확인·부분 이해를 해소하지 않는다.
- 실행 상태만 필요한 경우: Simple Auth reader 재발급 복원·Ctrl+C 중지 출력, Inspector Resource templates 하단 오류/종료, Docker 로컬 정리는 미확인이다. Render 삭제는 요청하지 않았다. 현재 원격 서비스 가동을 새로 검증한 기록은 아니다.

## 원문 교정과 구조 변경

- 초기 FastMCP1.30.0과 후속 MCPServer/Client2.2.0, SDK와 프로토콜 버전을 구분한다. 구형 초기화·SSE·Python 문법/검증·JWT/OAuth·Inspector UI 오류 안내를 해당 단원에서 교정했으며 원문 파일 수정과 구분한다. SDK stdout 보호·Host UI 전달 차이를 일반적 프로토콜 보장으로 표현하지 않는다.
- 질문 전 UI·용어·맥락을 먼저 설명한다. 단순 출력·안내 실습과 독립 답변/새 사례 적용을 구분하며 각 이해 기록의 확인 방식 한계를 유지한다.
- 2026-10-06: 오래된 상단 Apps 대기를 최신 수업 완료로 맞추고 단원별 반복 평가를 개념 기록에 연결했다. 정리 전 요약·단계별 실행 근거는 [보존본](history/03-implementation-evidence-2026-10-06.md), 기존 상세 이력은 각 링크에 유지한다. 테스트/진단7개 개념은 Python Client에서 별도 파일로 옮겼으며 이름·상태·날짜·답변 근거는 바꾸지 않았다.
