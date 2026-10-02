# Module 01 — Core Concepts 학습 기록

- 원문: [01-CoreConcepts/README.md](../../../01-CoreConcepts/README.md)
- 진행 상태: 요청 횟수 제한 설명 후 학습자가 원문 범위와 수업 길이 점검을 요청했다. 추가 개념 설명은 멈추고 수업의 세분화 정도를 조정한다.
- 첫 설명 범위: 여러 서버를 사용하는 Host와 서버별 Client, Server와 외부 데이터 소스의 구분.
- 남은 범위: 요청 제한 이해 확인, 감사 기록·통신 보안, Tasks, 도구 설계 연습. 실제 Python 설치·서버 실행은 아직 하지 않았다.
- Python 구현·실행 실습은 아직 수행하지 않았다.

## 관련 최신 이해 기록

- [Architecture](../../understanding/architecture.md)
- [Tools, Resources, Prompts](../../understanding/tools-resources-prompts.md)
- [Transports](../../understanding/transports.md)
- [Client Primitives](../../understanding/client-primitives.md)
- [Security Index](../../understanding/security/INDEX.md)

## 학습·복습 이력

### 2026-10-01 — Module 01 시작

- 학습자가 Module 01 시작을 요청했다. Module 00의 미확인 항목은 유지하며 관련 주제에서 복습한다.
- 기존 Host·Client·Server 및 도구 호출 흐름 이해를 바탕으로, 여러 서버에 대한 Client 분리와 데이터 소스 접근을 설명한다.
- 보충 예시: 파일 서버와 날씨 서버를 함께 사용하는 Python 학습 도우미.
- 확인 질문: 파일을 읽어 요약하는 상황에서 파일 읽기, 요약 생성, 통신 규칙을 각각 무엇이 담당하는가?
- 답변 대기 중이다. 설명만으로 이해 상태를 올리지 않는다.
- 원문에는 새 버전 안내와 초기화·상태 유지 설명, 도구별 동의 설명이 혼재한다. 관련 주제에 도달하면 버전·정책 차이를 확인해 구분하여 설명한다.

### 2026-10-01 — 파일 요약 흐름 확인

- 학습자는 Host → 모델의 도구 선택·요청 → Client → Server의 도구 호출 → 파일 읽기 → Client·Host → 모델의 요약이라는 흐름을 설명했다.
- 모델과 도구의 역할 및 호출 흐름은 파일 요약 사례에서 적용 확인으로 갱신했다.
- MCP 자체의 역할은 답변에서 명시되지 않았다. Client와 Server 사이의 표준화 역할을 추가 질문으로 확인한다.
- 서버별 Client 관계와 Server·데이터 소스 구분은 아직 별도의 답변으로 확인하지 않았다.

### 2026-10-01 — MCP 통신 구간 복습 완료

- 학습자는 MCP가 Client와 Server 사이의 통신을 표준화한다고 정확히 답했다.
- 이전 답변의 도구 실행·모델 요약 구분과 함께 MCP의 전체 역할을 이해 확인으로 갱신했다. Module 00에서 남긴 해당 복습 항목을 해결했다.
- 다음 확인 질문: 파일 서버와 날씨 서버를 함께 사용하는 Host가 관리하는 Client의 수와 각각의 역할.

### 2026-10-01 — 서버별 Client 확인 및 Resources 시작

- 학습자는 Client 두 개가 각각 파일 서버와 날씨 서버의 통신을 담당한다고 정확히 답했다. 서버별 Client 관계를 적용 확인으로 갱신했다.
- 원문의 Server Primitives → Resources를 바탕으로 URI, resources/list와 resources/read의 구분을 설명한다.
- 보충 예시: study://notes/python-basics라는 URI로 학습 노트를 제공하는 서버. URI의 문자열 모양만으로 인터넷 주소나 실행 함수를 의미하지 않는다.
- 확인 질문: 목록에서 URI를 받으면 내용까지 읽은 것인가, 아니면 추가 요청이 필요한가?

### 2026-10-01 — Resource 읽기 확인 및 Prompts 시작

- 학습자는 대상 URI와 함께 resources/read 요청을 Server로 보내야 내용을 읽을 수 있다고 답했다. Resource의 발견과 읽기를 이해 확인으로 갱신했다.
- 원문의 Server Primitives → Prompts를 바탕으로 재사용 템플릿, prompts/list 및 prompts/get을 설명한다.
- 보충 예시: explain_python_code 템플릿에 Python 코드를 인자로 넣어 설명 요청 메시지를 가져오는 과정.
- 확인 질문: prompts/get으로 메시지를 받았을 때 모델의 코드 설명까지 생성된 것인가, 이후 모델에 전달해야 하는가?

### 2026-10-01 — Prompts 확인 및 Tools 인자 명세 시작

- 학습자는 prompts/get으로 받은 프롬프트를 모델에 전달해야 한다고 답했다. Prompts를 이해 확인으로 갱신했다.
- 원문의 Tools 설명에서 이름·설명·입력 스키마와 tools/list·tools/call을 소개한다.
- Python 보충 예시: get_weather(location: str)의 필수 문자열 인자를 나타낸 간단한 명세. 실제 SDK 등록이나 실행 실습은 아니다.
- 확인 질문: 서울 날씨 조회 시 필수 문자열 location에 전달할 호출 인자는 무엇인가?

### 2026-10-01 — Tool 인자 확인 및 Annotations 시작

- 학습자는 location: "seoul"이라는 올바른 인자를 제시했다. Tool 인자 명세를 적용 확인으로 갱신했다.
- 원문의 readOnlyHint·destructiveHint 설명과 [MCP 공식 해설](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/)을 바탕으로 행동 힌트와 실제 권한 제한의 차이를 설명한다.
- 확인 질문: readOnlyHint: true만으로 파일 변경을 막을 수 있는가?

### 2026-10-01 — Tool Annotations 확인 및 Elicitation 시작

- 학습자는 readOnlyHint만으로 파일 수정을 막을 수 없다고 정확히 답했다. Tool Annotations를 이해 확인으로 갱신했다.
- 원문의 Client Primitives → Elicitation을 바탕으로 서버가 추가 입력을 요청하고 Host가 사용자 인터페이스를 담당하는 관계를 설명한다.
- 보충 예시: 학습 계획 저장 중 동일 이름의 파일을 발견한 Server가 다른 파일 이름을 요청한다. 모든 도구 호출에 질문이 필요한 것은 아니며, 이를 모델의 임의 질문과 구분한다.
- 확인 질문: 추가 입력 필요를 판단한 주체와 질문을 사용자에게 보여주는 주체는 각각 무엇인가?

### 2026-10-01 — Elicitation 확인 및 Roots 시작

- 학습자는 추가 파일 이름이 필요하다고 판단하는 주체를 Server, 질문을 보여주는 주체를 Host로 정확히 답했다. Elicitation을 이해 확인으로 갱신했다.
- Roots의 위치 정보와 접근 권한을 구분한다. 보충 예시: 프로젝트 학습 폴더를 관련 위치로 전달해도 외부 경로 접근은 별도 통제로 제한해야 한다.
- [공식 Deprecated 기능 목록](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)에서 Roots의 폐기 예정 상태와 도구 인자·Resource URI·서버 설정으로의 이전 안내를 확인했다. Deprecated는 즉시 제거와 구분한다.
- 확인 질문: Roots를 전달하는 것만으로 폴더 밖 접근이 자동 차단되는가?

### 2026-10-01 — Roots 확인 및 Sampling 시작

- 학습자는 Roots 전달만으로 외부 경로 접근을 차단할 수 없다고 답했다. Roots와 접근 권한을 이해 확인으로 갱신했다.
- 원문의 Sampling을 일반 도구 호출과 반대 방향의 능력 요청으로 설명한다. 보충 예시: Server가 문서 처리 도중 Host 측 모델에 요약 생성을 요청한다.
- Sampling에서 모델 사용은 Host가 통제한다. Server가 모델을 소유하거나 제한 없이 호출하는 권한을 얻는 것은 아니다.
- 공식 Deprecated 기능 목록에서 Sampling의 2026-07-28 폐기 예정 상태와 LLM 제공자 API 직접 연동으로의 이전 안내를 확인했다.
- 확인 질문: Server가 Host 측 모델에 요약을 요청하는 것은 일반 도구 호출인가, Sampling인가?

### 2026-10-01 — Sampling 확인 및 Logging 시작

- 학습자는 Server가 Host 측 모델에 요약 생성을 요청하는 사례를 Sampling으로 정확히 분류했다. Sampling을 이해 확인으로 갱신했다.
- 원문의 Logging 설명에서 디버깅·작업 추적을 위한 로그와 도구의 반환 결과를 구분한다.
- 보충 예시: '서울 날씨 조회를 시작했습니다'는 처리 로그이고, 실제 기온과 날씨는 도구 실행 결과이다.
- 공식 Deprecated 기능 목록의 안내에 따라 stdio에서는 stderr, 구조화된 관측에는 OpenTelemetry를 사용하는 이전 방향을 소개한다. 세부 구현은 아직 다루지 않는다.
- 확인 질문: 조회 시작 로그만으로 실제 날씨 결과를 받았다고 볼 수 있는가?

### 2026-10-01 — Logging 확인 및 요청·응답 메시지 시작

- 학습자는 조회 시작 로그가 실제 날씨 결과는 아니라고 답했다. Logging을 이해 확인으로 갱신했다.
- 이미 답변으로 확인한 Information Flow 설명은 반복하지 않고, Protocol Messages의 요청·응답 구조와 id의 대응 관계를 설명한다.
- 보충 예시: id 7인 get_weather 호출과 id 7인 결과 응답. 메시지는 기본 필드 설명을 위한 발췌이며 버전별 필수 메타데이터를 포함한 완전한 요청은 아니다.
- 확인 질문: 응답 id가 12라면 id 11과 12의 두 요청 중 어느 요청의 결과인가?

### 2026-10-01 — id 대응 확인 및 Notification 시작

- 학습자는 id 12 응답을 id 12 요청의 결과로 정확히 연결했다. 요청·응답 id를 이해 확인으로 갱신했다.
- 원문의 Notification Messages와 Message Structure를 바탕으로 id 없는 알림과 응답이 필요한 요청을 구분한다.
- 예시: notifications/tools/list_changed는 목록 변경을 알리는 메시지이며 새 목록은 tools/list로 조회한다.
- 확인 질문: 도구 목록 변경 알림 뒤 새 목록을 얻으려면 무엇을 보내야 하는가?

### 2026-10-01 — Notification 확인 및 오류 응답 시작

- 학습자는 최신 도구 목록을 얻기 위해 tools/list를 보내야 한다고 정확히 답했다. Notification을 이해 확인으로 갱신했다.
- 원문의 Response Messages 설명을 바탕으로 result와 error를 구분한다.
- 공식 Tools 명세를 참고하여 프로토콜 오류와 result.isError로 나타내는 도구 실행 실패를 보충 설명한다.
- 확인 질문: result가 있어도 isError: true라면 작업이 성공했다고 볼 수 있는가?

### 2026-10-01 — 도구 실행 실패 확인 및 표준화 범위 질문

- 학습자는 isError: true이면 날씨 조회가 실패한 것으로 봐야 한다고 정확히 답했다. 필드명 오타 isErrro는 isError로 교정한다.
- 추가 질문: result 안의 실패 정보도 표준화되어 있는가?
- 보충 설명: isError와 content의 블록 구조는 표준화되어 있다. text의 구체적 오류 문구나 개별 업무 오류 코드는 도구별로 달라질 수 있으며, JSON-RPC error.code와 구분한다.
- 추가 설명 자체로 표준화 범위 이해를 확인 처리하지 않는다.

### 2026-10-01 — 실패 정보 표준화 확인 및 요청별 메타데이터 시작

- 학습자는 오류 설명이 영어로 바뀌어도 isError 기반 실패 판단은 바뀌지 않는다고 답했다. 표준화 범위를 이해 확인으로 갱신했다.
- [공식 Versioning and Compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)를 확인했다. lifecycle URL은 이 페이지로 연결된다.
- 원문의 초기화·상태 유지 설명은 2025-11-25 이하의 방식과 구분한다. 2026-07-28은 요청마다 버전·클라이언트 정보·지원 기능을 전달하며 initialize handshake에 의존하지 않는다.
- Stateless는 Host의 대화 기록이나 서버 저장 데이터를 없앤다는 뜻이 아니다. 이전 연결에 기억된 프로토콜 정보에 의존하지 않는 요청 구조임을 보충한다.
- 확인 질문: 이전 요청에서 버전을 전달했다는 이유로 다음 요청에서 필수 버전 정보를 생략할 수 있는가?

### 2026-10-01 — 요청별 버전 확인 및 Stateless 의미 보충

- 학습자는 버전을 생략하면 안 되며 매 요청에 포함해야 한다고 정확히 답했다.
- 이유를 Server가 Client를 기억하지 않는 것으로 설명했다. 프로토콜이 이전 연결의 기억에 의존하지 않는 것과, 서버가 정보를 저장하거나 캐시할 수 없는 것은 다르다고 보충한다.
- 요청별 메타데이터·Stateless를 부분 이해로 기록했다. 요청별 필수 정보 판단은 확인했으나 저장 상태와의 구분은 아직 재확인하지 않았다.
- 보충 확인 질문: Stateless 방식의 MCP Server도 데이터베이스에 학습 기록을 저장하고 다음 요청에서 조회할 수 있는가?

### 2026-10-01 — Stateless 보충 확인 및 서버 발견 시작

- 학습자는 Stateless MCP Server도 데이터베이스에 학습 기록을 저장·조회할 수 있다고 답했다. 요청별 메타데이터·Stateless를 이해 확인으로 갱신했다.
- 원문의 Request Metadata and Discovery를 바탕으로 server/discover의 지원 버전·서버 정보·기능·확장 조회와 tools/list 등의 개별 목록 조회를 구분한다.
- 발견 요청은 initialize handshake나 작업 실행 요청과 구분한다. 버전별 세부 상호운용 절차는 아직 다루지 않았다.
- 확인 질문: get_weather의 이름과 필수 인자를 알아보려면 server/discover와 tools/list 중 무엇을 사용하는가?

### 2026-10-01 — 서버 발견 확인 및 stdio 시작

- 학습자는 개별 날씨 도구의 이름·인자 명세 조회에 tools/list를 선택했다. 서버 발견과 목록 조회를 이해 확인으로 갱신했다.
- 원문의 Transport Layer → STDIO와 공식 명세를 바탕으로 stdin·stdout·stderr 역할을 설명한다.
- Python 보충 예시: print의 기본 stdout 출력과 file=sys.stderr 출력의 구분. 실제 서버를 실행하지 않는다.
- 확인 질문: '서버가 시작되었습니다' 같은 디버깅 문구를 stdout에 보내면 왜 문제가 될 수 있는가?

### 2026-10-01 — stdio 확인 및 Streamable HTTP 시작

- 학습자는 Client가 stdout 문구를 서버 메시지로 읽지만 규약에 맞지 않아 실패할 수 있다고 설명했다. stdio의 메시지·로그 분리를 이해 확인으로 갱신했다.
- 보충: Client의 실패 처리 형태는 구현별로 다르며, MCP 메시지 파싱 실패가 도구의 isError 실행 실패를 의미하지는 않는다.
- 원문의 Streamable HTTP와 공식 전송 명세를 바탕으로 HTTP POST를 통한 MCP 메시지 전달, 로컬·원격 연결과 Data Layer 유지 관계를 설명한다.
- 확인 질문: 원격 Python 서버에 연결하려면 stdio와 Streamable HTTP 중 무엇이 적합하며 MCP 메시지 형식은 바뀌는가?

### 2026-10-01 — Streamable HTTP 확인 및 SSE 시작

- 학습자는 원격 Python Server에 Streamable HTTP를 선택하며 JSON-RPC 본문 형식을 유지한다고 답했다. 전송 방식 선택을 적용 확인으로 갱신했다.
- 공식 Streamable HTTP 명세를 바탕으로 단일 JSON 응답과 SSE 응답 스트림의 차이를 설명한다.
- 보충 예시: 오래 걸리는 파일 분석에서 요청 관련 진행 알림을 보내고 최종 응답을 전달한다. 모든 도구가 진행 알림이나 결과 조각을 반드시 보내는 것은 아니다.
- 오래된 HTTP+SSE 전송의 폐기와 Streamable HTTP 안에서의 SSE 사용을 구분한다.
- 확인 질문: SSE를 사용하면 진행 알림과 최종 응답을 JSON-RPC 대신 일반 문자열로 보내도 되는가?

### 2026-10-01 — SSE 메시지 확인 및 구버전 전송 비교 질문

- 학습자는 SSE의 진행 알림·응답도 임의 일반 문자열로 보내면 안 된다고 답했다. SSE 메시지 형식 유지를 이해 확인으로 갱신했다.
- 추가 질문: 옛 HTTP+SSE 전송 방식과 Streamable HTTP 안에서 SSE 사용은 어떻게 다른가?
- [2024-11-05 전송 명세](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports)와 [2026-07-28 Streamable HTTP 명세](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)를 비교했다.
- 이전 방식은 SSE 수신·POST 송신의 별도 엔드포인트를 요구한다. 2026-07-28은 단일 POST 엔드포인트로 요청을 보내고 요청의 응답을 JSON 또는 SSE로 받는다. 장기 변경 알림은 subscriptions/listen POST의 SSE 응답으로 받는다.
- 2025-03-26~2025-11-25 Streamable HTTP에는 선택적 GET 스트림이 있었다. 비교는 2026-07-28을 대상으로 하며 모든 Streamable HTTP 버전에 GET 제거를 적용하지 않는다.
- 확인 질문: 2026-07-28에서 단일 JSON 결과만 필요해도 별도 SSE 수신 연결을 먼저 열어야 하는가?

### 2026-10-01 — 단일 JSON 응답 확인 및 HTTP 헤더 시작

- 학습자는 JSON 하나라면 별도 SSE 수신 연결 없이 일반 HTTP 응답으로 보내면 된다고 정확히 답했다. 전송 방식 비교를 이해 확인으로 갱신했다.
- 원문의 Streamable HTTP headers 및 공식 명세를 바탕으로 MCP-Protocol-Version·Mcp-Method·Mcp-Name을 설명한다.
- 헤더는 HTTP 부가 정보이고, JSON-RPC 본문을 대체하지 않는다. 도구 호출은 도구 이름, Resource 읽기는 URI를 Mcp-Name에 반영한다.
- 확인 질문: resources/read로 study://notes/python-basics를 읽을 때 Mcp-Name은 무엇인가?

### 2026-10-01 — HTTP 헤더 적용 확인 및 메타데이터 버전 구분

- 학습자는 Mcp-Name으로 대상 Resource URI를 정확히 선택했다. HTTP 요청 헤더를 적용 확인으로 갱신했다.
- 원문의 요청별 메타데이터 안내와 공식 기본 명세를 바탕으로 params._meta에 있는 프로토콜 버전과 Client 프로그램 버전을 구분한다.
- 예시는 2026-07-28 프로토콜과 PythonStudyClient 프로그램 1.0.0이다. 프로그램 업데이트가 반드시 프로토콜 버전 변경을 뜻하지 않는다는 설명을 보충한다.
- 확인 질문: Client 프로그램이 1.0.0에서 1.1.0으로 바뀌면 MCP 프로토콜 버전도 반드시 바뀌어야 하는가?

### 2026-10-01 — 버전 구분 확인 및 Python 도구 등록 시작

- 학습자는 Client 업데이트에 프로토콜 버전 변경이 필수는 아니라고 정확히 답했다. 두 버전 구분을 이해 확인으로 갱신했다.
- 원문의 Python 예제에서 서버 생성·get_weather 등록 부분을 발췌하여 설명한다. 실행·설치 실습은 아직 하지 않는다.
- FastMCP 도구 문서를 확인하여 함수 이름·docstring·타입 힌트를 도구 메타데이터로 사용하는 역할을 설명한다.
- 원문 get_weather는 외부 API 조회 없이 고정된 72.5·Sunny를 반환하는 예시이다. 등록과 실행, 예시 데이터와 실시간 데이터를 구분한다.
- 확인 질문: @mcp.tool()로 등록한 시점에 날씨 함수가 실행되는가, 아니면 도구 호출 요청 시 실행되는가?

### 2026-10-01 — 도구 실행 시점 확인 및 서버 실행 설명

- 학습자는 도구 함수가 실행 요청을 처리할 때 실행된다고 답했다. Python 도구 등록·실행 구분을 이해 확인으로 갱신했다.
- 원문은 asyncio.run(serve_stdio(mcp))로 실행을 표현한다. 현재 [FastMCP 실행 문서](https://gofastmcp.com/deployment/running-server)는 mcp.run() 또는 run_async()를 안내한다. 현재 문서 기준으로 mcp.run(transport="stdio")를 보충 예시로 설명하며, 원문 코드를 최신 버전에서 실행 검증한 것으로 표현하지 않는다.
- __main__ 조건은 파일을 직접 실행할 때만 서버를 시작하게 한다. 서버 시작 자체는 특정 날씨 도구 호출과 다르다.
- 확인 질문: 서버를 실행하기만 하면 자동으로 서울 날씨 결과가 나오는가?

### 2026-10-01 — 서버 시작 확인 및 기본값 인자 설명

- 학습자는 Client가 해당 도구 요청을 보내야 결과를 얻는다고 답했다. 서버 시작과 도구 호출을 이해 확인으로 갱신했다. 실제 메시지 종류는 tools/call이라고 보충한다.
- 원문 forecast(self, location: str, days: int = 1)의 작업 인자인 location과 days를 설명한다. 클래스 메서드 등록은 다음 단계에서 별도로 다룬다.
- 기본값이 없는 location은 필수이며 days는 생략 시 1을 사용한다. 생략과 null 전달은 같지 않다는 구현 세부는 아직 다루지 않았다.
- 확인 질문: location만 전달하고 days를 생략하면 며칠의 예보를 반환하는가?

### 2026-10-01 — 기본값 확인 및 클래스 메서드 등록 보충

- 학습자는 days 생략 시 1일 예보를 반환한다고 답했다. 기본값 인자를 이해 확인으로 갱신했다.
- 원문은 클래스 안의 메서드에 @mcp.tool()을 적용한 뒤 인스턴스를 생성한다. 현재 [FastMCP 메서드 문서](https://gofastmcp.com/servers/tools#using-with-methods)는 이 방식에서 self/cls가 필수 입력으로 노출될 수 있음을 설명한다.
- 공식 문서 방식에 맞춰 @tool()로 메타데이터를 붙이고 mcp.add_tool(weather_tools.forecast)로 바인딩된 메서드를 등록하는 보충 예시를 설명한다. 원문 수정·실행 실습은 하지 않는다.
- self는 인스턴스를 가리키며 Python이 연결한다. Client가 제공하는 작업 입력은 location과 선택적 days이다.
- 확인 질문: Client가 forecast를 호출할 때 self도 JSON 인자로 보내야 하는가?

### 2026-10-01 — self 확인 및 예시 데이터 점검

- 학습자는 바인딩된 메서드 호출 시 self를 전달하지 않아도 된다고 답했다. 클래스 메서드 등록을 이해 확인으로 갱신했다.
- 원문 get_weather의 반환값을 비교한다. seoul과 busan 요청은 location만 달라지고 temperature=72.5와 conditions=Sunny는 같다.
- 도구 등록·통신 성공이 실시간 데이터 조회 또는 업무 결과의 정확성을 보장하지 않는다는 점을 설명한다.
- 확인 질문: 원문 get_weather를 도구로 등록하면 실제 서울 날씨를 조회하게 되는가? 왜 그런가?

### 2026-10-01 — 실시간 조회 확인 및 인증·인가 시작

- 학습자는 실제 날씨를 알려면 API를 호출해 정보를 가져와야 한다고 설명했다. 예시 데이터·실시간 조회 구분을 이해 확인으로 갱신했다.
- 원문의 Authentication & Authorization·Tool Permission Control을 바탕으로 신원 확인과 작업 권한 판단을 구분하는 보충 설명을 제공한다.
- 예시: 로그인에 성공한 학습자도 읽기만 허용된 노트를 수정할 권한은 없을 수 있다.
- 확인 질문: 로그인 후 수정이 거부되는 것은 인증과 인가 중 어느 판단인가?

### 2026-10-01 — 인가 확인 및 사용자 동의 구분

- 학습자는 로그인 후 권한 없는 수정이 거부되는 상황을 인가로 정확히 답했다. 인증·인가를 이해 확인으로 갱신했다.
- 원문의 사용자 동의·도구 권한 항목과 공식 Tools 보안 안내를 바탕으로 Host의 사용자 동의와 Server의 요청별 접근 권한 검사를 구분한다.
- 보충 예시: 사용자 승인만으로 서버의 파일 삭제 권한이 생기는 것은 아니다. Host가 도구를 숨기는 것도 서버 권한 검사를 대신하지 않는다.
- 원문의 매 도구 호출 동의 문구와 민감한 작업 확인 안내를 구분한다. 모든 호출에서 새 확인창이 필요한 것으로 가르치지 않는다.
- 확인 질문: Host에서 승인했지만 Server에서 해당 파일 삭제 권한이 없으면 삭제 요청을 허용할 수 있는가?

### 2026-10-01 — 사용자 동의 확인 및 입력 검증 설명

- 학습자는 Host에서 승인했어도 Server에서 삭제 권한이 없으면 허용해서는 안 된다고 답했다. 사용자 동의와 서버 권한 검사를 이해 확인으로 갱신했다.
- 원문의 Validation과 공식 Tools 보안 안내를 바탕으로 Server가 입력의 타입·필수 항목·허용 범위를 검증해야 함을 설명한다.
- 보충 예시: forecast의 days를 정수이며 1~7로 제한한다고 가정한다. 원문의 days: int = 1 자체에는 이 범위 제한이 없다. 타입에 맞아도 범위를 벗어나면 거부해야 한다.
- 확인 질문: days=100은 정수이므로 처리해도 되는가? 이유는 무엇인가?

### 2026-10-01 — 입력 검증 확인 및 요청 횟수 제한 설명

- 학습자는 날씨 API가 최대 7일까지 제공하므로 days=100 요청을 진행하면 안 된다고 설명했다. 입력 검증을 이해 확인으로 갱신했다.
- 원문의 Rate Limiting을 바탕으로 요청 횟수를 사용자·자격 증명·작업 또는 서버 전체 단위로 제한할 수 있음을 설명한다. MCP 연결만으로 특정 횟수 제한이 자동 적용되는 것은 아니다.
- 보충 예시: 사용자당 1분 10회 정책은 비용·서버 부하·외부 API 한도를 관리하기 위한 가정이다. 권한과 입력이 유효해도 횟수 한도를 넘으면 제한할 수 있다.
- 확인 질문: 권한과 입력이 유효한 11번째 요청도 제한할 수 있는가? 이유는 무엇인가?

### 2026-10-01 — 원문 범위와 수업 길이 점검

- 학습자는 현재 설명이 Module 01 원문에 있는지 질문하고 수업이 길어지고 있다고 지적했다. 요청 횟수 제한 질문에 답한 것은 아니므로 이해 상태는 미확인으로 유지한다.
- 원문의 Security and Authorization에는 Tool Permission Control, Authentication, Validation, Rate Limiting이 있다. 최대 7일·분당 10회 조건은 선생님의 보충 예시이다.
- 짧은 원문 항목마다 설명과 질문을 세분화하여 수업이 길어졌다. 이후 원문의 비중에 맞춰 관련 항목을 묶고 보충 설명과 질문은 필요한 지점에 한정한다.
- 남은 보안 내용은 개요 수준으로 정리하며 상세 보안은 다음 Module 02에서 다룬다. 이후 Tasks 개요와 원문의 도구 설계 연습을 진행한다. 기존 미확인 항목을 이해 확인으로 올리지는 않는다.
