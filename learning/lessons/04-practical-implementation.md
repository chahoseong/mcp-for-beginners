# Module 04 — Practical Implementation 과제·검토

## 현재 진행 방식 — 2026-10-07 변경

- 학습자가 이 모듈에서 교사의 수업 대신 과제 출제·검토 역할을 요청했다. 기존 7단계 강의 계획은 진행 방식이 변경되었으며 목표·최신 교정 근거만 참고한다.
- 과제 제시→제출 검토→필요한 수정/재제출→다음 과제로 진행한다. 제출 코드/실행 근거와 설계 이유를 따로 평가하고 확인된 부분·빠진 근거·문제를 구분한다. 독립 작성과 기존 예제/힌트 활용을 구분하며 제출물 없이 이해 상태를 올리지 않는다. 새로운 개념이 필요한 과제에는 관련 자료/전제를 먼저 안내한다.
- 과제 묶음: (1) 실제 문제·도구 계약·Resource/Prompt·흐름 설계 (2) Python SDK v2로 최소 한 업무 Tool과 Resource/Prompt 구현·Client 연결/활용/검증 (3) 의존 호출/오류 처리·페이지네이션·측정 기반 개선 (4) 검사 목적별 테스트/오류 복구와 운영 구조 판단. 상세 요구는 각 과제 시작 때 필요한 범위만 제시한다. Azure 실제 배포는 선택이다.
- Client 범위 정정(2026-10-07): 학습자 질문에 따라 VS Code 등 기존 Host/MCP Client 사용을 허용한다. 새 Client 애플리케이션 작성은 선택이며 서버 연결·요구한 기능 호출·작업 흐름/실패 결과 검증을 필수 성취로 둔다. 자동 검사/페이지네이션 메시지 관찰에 작은 Python 검사 코드가 필요하면 해당 목적과 범위를 과제 때 안내한다. 전체 Client 프로그램을 요구하지 않는다. 과제1 설계 제출 범위는 유지한다.
- 과제1 제출 범위: 분야/문제·사용자 요청을 정하고 Tool3~4개의 이름/일/입력 자료형/주요 반환 필드/실패 조건, Resource1개와 Prompt1개 역할, 호출 순서/단계 간 전달 데이터/실패 시 처리 흐름을 제출한다. 그림 또는 번호 순서 모두 허용한다. 코드·설치·배포는 이 과제의 제출 범위가 아니다. 주제는 학습자 선택이며 이전 상품 견적 예시는 참고일 뿐이다.
- 검토 기준: 실제 문제와 도구 책임의 일치, 입력/출력 계약의 구체성·연결 가능성, Resource/Prompt 역할 구분, 단계 의존성과 실패 경로. 교사가 앞서 제공한 도구 이름/흐름을 재사용하는 경우 독립 새 설계로 일반화하지 않는다.
- 설계 제출/시험 요청(2026-10-07): [DESIGN.md](../../04-PracticalImplementation/practice/docs/DESIGN.md)를 에이전트와 함께 작성했다고 보고하고 필수 이해를 시험으로 확인받기를 요청했다. 상품 검색·재고·견적3개 Tool, quote://policy, prepare_quote, 후보별 데이터 연결·정책 버전·부분 완료·정상 조건 불충족/실행 실패 구분을 읽었다. 공동 문서 완성도를 독립 이해로 판정하지 않는다. 외부 API의 실제 지원·SDK 코드/Decimal/재시도 상세 구현은 과제1 핵심 이해 시험과 구분한다. 과제2 제출에서 docs/로 이동한 경로를 반영했다.
- 작성 방식 명확화(2026-10-08): 학습자가 에이전트 제안→본인 검토 방식이었다고 명확히 밝혔다. 이번 시험은 제안된 설계의 이해와 사례 판단을 확인한 것이며 처음부터 독립 설계를 만드는 능력은 미평가이다. 협업 방식 자체를 감점하거나 기존 이해 상태를 낮추지 않는다.
- 시험 방식: 역할/실행 경계, 입력·출력 계약과 데이터 의존성, 정상 업무 결과/실행 실패·부분 완료, 정책·완료 조건의4묶음/각2문항과 집중 후속 질문으로 진행했다. 설계 문서 참고는 허용했고 본인의 설명·이유·변경 사례 판단으로 평가했다. 미학습/불명확한 구분은 보충 후 재확인했다.
- 첫 묶음 평가(2026-10-07): Prompt 조회와 실제 도구 실행, Host/모델/Client/Server 역할·추가 도구 요청 흐름을 설명했다. 가격/할인 인자 추가를 정책 계산 책임 전체의 Host 이동으로 표현한 부분은 보충 후 재고 인자 변경 사례에서 정보 제공/서버 비교 책임과 실제 재고와 다른 값의 위험을 설명해 재확인했다. 보충 후 집중 확인이며 독립 적용으로 일반화하지 않는다. Client의 연결(세션) 유지 표현은 서버별 통신 관계와 최신 HTTP 프로토콜 세션을 구분해 보충했으며 해당 구분 자체는 미평가이다. 최신 근거는 [Architecture](../understanding/architecture.md), [Tools/Resources/Prompts](../understanding/tools-resources-prompts.md)에 둔다.
- 두 번째 묶음 평가(2026-10-07): 견적 인자 JSON과 반환 순서 차이/product_id 연결 이유는 정확했고 후속 답변에서 상품 ID의 검색 출처·수량/예산의 사용자 요청 출처와 이름이 같은 상품의 매칭 위험을 설명했다. 변환 과정 설명은 생략되었으나 숫자 인자는 정확했다. 문자열의 범위 검증·변환 구현은 보충/후속 구현 과제 대상으로 남기고 설계 수준의 연결은 이해 확인으로 기록한다.
- 세 번째 묶음 평가(2026-10-08): 정상 조회의 재고 부족/예산 초과와 도구 실행 실패를 구분했다. 적합 후보 제공과 다른 후보 미확인 안내, 전체 최저가 주장의 근거 부족을 설명해 부분 완료의 의미를 확인했다. 상태 이름은 보충하며 용어 미기재를 오개념으로 판정하지 않는다. 설계 문서 참고 허용의 개념 평가이며 실제 구현 검증은 아니다.
- 마지막 묶음 평가(2026-10-08): 조회 시점의 가격/재고와 실제 보장을 구분했다. 정책 문제는 원본 공유/조회 사이 업데이트/전체 중단 규칙 보충 후 여러 후보의 버전 불일치에 부분 완료가 부적합하며 현재 정책을 확인하고 안내를 중단해야 한다고 설명해 재확인했다. 보충 후 이해 확인이며 독립 구현으로 일반화하지 않는다.
- 과제1 이해 확인 시험 완료(2026-10-08): 설계의 역할·입력 출처·상품별 연결·정상 조건 불충족/부분 완료·정책 불일치 중단·조회/보장 구분의 핵심 이해를 확인했다. 정보 제공/계산 책임과 정책 불일치는 보충 후 확인한 부분이다. 다음은 과제2의 Python 최소 업무 Tool·Resource/Prompt 구현과 VS Code 등 기존 Client를 통한 결과 제출이다. 세부 과제2 요구는 아직 출제하지 않았다. 문자열 검증/변환, 내부 정책 공유, 실제 오류 제어/외부 API 계약은 구현에서 검증한다. Client 연결/프로토콜 세션 구분의 보충은 독립 확인으로 기록하지 않는다.
- 기록 구조 점검(2026-10-08): 최신 근거는 개념 기록에, 모듈에는 재개 요약을 유지했다. 추가 파일 분리 없이 INDEX의 과제/업무 계약 선택 기준을 갱신했다. 문서 공동 작성과 독립 구현 한계를 보존했다.
- 과제2 출제(2026-10-08): 아래 최소 구현과 실행 결과를 제출받고 설계 계약/실행 근거를 검토한다. 에이전트와 협업은 허용하며 본인이 먼저 정한 부분/검토·수정한 부분을 구분한다.
- 과제2 제출 검토(2026-10-08): app/의 stock Tool·policy Resource·quote Prompt와 입력 검사 middleware, tests/와 README/uv.lock을 읽었다. Python3.12.10/MCP2.3.0/HTTPX0.28.1/pytest9.1.1을 확인했다. 제한 환경에서는 asyncio 시작에서 멈춰 해당 실행을 종료하고 승인된 일반 실행 환경에서 전체 pytest125개가42.89초에 통과했다. 실제 stdio Tool 호출에서도 상품1의 stock99에 quantity1/99/100을 보내 각각 true/true/false·status ok·is_error false를 확인했다. 단위 모의 실패와 실제 API/stdio 검사 범위를 구분한다. 검토자는 제출 코드를 수정하지 않았다.
- 과제2 보완 요청: 기능 검증은 통과했으나 docs/DESIGN.md의 status:error/error 객체 계약과 실제 ToolError(텍스트 JSON·isError true·structured_content 없음) 계약이 달라 변경 이유/SDK 입력 검증 오류를 문서화해야 한다. README에는 실행 명령/검사 범위가 있지만 사례별 실제 결과와 입력 검증·외부 실패 구분·정책 관리 판단, 이번 협업 범위가 없다. 보완 제출 후 최종 판정하며 코드 존재/검토자의125개 통과만으로 학습자의 독립 구현 이해를 확정하지 않는다.
- 과제2 재검토(2026-10-08): f9e9fbf64의 README/DESIGN 문서 변경을 구현과 대조했다. ToolError/isError·성공 structuredContent 부재·SDK 검증 오류와 앱 오류 텍스트의 차이, 자동 재시도 미구현이 정확하게 정리됐다. 검증 위치·조회 실패/재고 부족·정책 단일 원본의 판단 설명과 에이전트 작성/학습자 승인·검토·수정 방향 결정의 분담도 제출됐다. 설명 문서의 정확성을 확인한 것이며 독립 작성 능력으로 판정하지 않는다. 문서만 변경되어 기존 기능 검증을 유지하고 테스트는 반복하지 않았다. 대표 요청 표에는 기대 결과만 있으므로 실제 결과 요약만 추가 제출을 기다린다. 기존 실행 결과를 사용하며 README 또는 채팅 모두 허용한다.
- 과제2 완료·제출 조건 정정(2026-10-08): 학습자가 같은 코드의 실행 결과를 검토자가 이미 확인했는데 별도 실행/기록을 요구하는 이유를 지적했다. 기존 pytest125개·실제 stdio 경계 호출의 근거를 그대로 인정하며 결과를 별도로 옮겨 적는 조건을 철회했다. 오류 계약·핵심 판단·협업 범위 보완과 기존 기능 검증으로 과제2를 완료 처리했다. 추가 실행/문서 보완은 요구하지 않는다. 협업 구현과 독립 작성 능력의 구분 및 기존 이해 상태는 유지한다. 기록 구조를 점검하고 최신 다음 행동을 과제3 안내로 갱신했다. 과제3 상세 요구는 아직 출제하지 않았다.

## 과제2 — 최소 업무 서버 구현과 기능 검증

- 원문 Exercise의 최소1개 Tool 구현/Prompt 작성과 Core Server Features에 맞춘 단계 제출이다. 실습은 04-PracticalImplementation/practice 아래 별도 가상환경에서 Python 공식 SDK v2의 MCPServer·stdio로 진행한다. 기존 VS Code 또는 Inspector 사용을 허용하며 새 Client 작성은 선택이다. 사용한 Python/SDK/의존성 버전과 재실행 방법을 제출한다.
- 필수 구현: check_stock(product_id:int, quantity:int) 하나, quote://policy Resource, prepare_quote Prompt. Tool은 실제 DummyJSON 상품 조회 API에서 stock을 읽고 설계의 성공 필드/status를 반환한다. 양의 상품 ID·1이상 수량, 없는 상품, timeout/외부 API 오류·유효하지 않은 stock을 처리하며 조회 실패를 재고 부족으로 변환하지 않는다. timeout은 설계의10초를 적용한다. 자동 재시도·429 대기 정책은 다음 신뢰성 단계로 미룰 수 있으며 미구현을 기록한다.
- Resource는 설계의 정책 내용/버전을 제공하고 정책 원본을 한곳에 둔다. Tool이 MCP Resource를 경유해야 하는 요구는 없다. prepare_quote는 설계의 문자열 인자/keyword 기본값으로 메시지를 반환한다. 이번 제출에서는 Prompt 목록/내용 조회까지 검증하며 아직 없는 search_products/calculate_quote를 호출하는 전체 흐름은 실행하지 않는다. 미구현 도구를 동작하는 것처럼 등록하지 않는다.
- 필수 실행 증거: 연결/Tool 목록·입력 스키마, 양의 stock을 가진 상품의 수량1/재고와 같은 수량/재고+1, 수량0 입력 거부, 실제 없는 양의 상품 ID의 조회 실패, 정책 Resource 본문/버전, Prompt 목록과 정상 인자의 렌더링 메시지. 실제 stock 값으로 기대값을 정하며 고정 예시 숫자를 실시간 API 값으로 간주하지 않는다. 자동 테스트 전체 구축은 이후 과제로 둔다.
- 오류 계약은 설계의 업무 status/error와 MCP isError가 별개 층임을 전제로 반환/예외 매핑을 선택하고 설명한다. SDK의 인자 검증 오류와 서버 본문의 업무 오류를 구분한다. 계약을 조정하면 DESIGN.md에 이유를 기록한다.
- 제출: 구현 파일 경로, 재실행 가능한 의존성/실행·연결 설명, 사례별 입력/기대/실제 결과, 핵심 판단3개(입력 검증 위치·외부 실패와 재고 부족 구분·정책 원본 관리)와 협업 범위/설계 변경·미구현 사항. 첫 검토는 전체 견적 완성이 아닌 이 최소 범위에 한정한다.
- 최신 확인 자료: [SDK Tools](https://py.sdk.modelcontextprotocol.io/servers/tools/), [Prompts](https://py.sdk.modelcontextprotocol.io/servers/prompts/), [Handling errors](https://py.sdk.modelcontextprotocol.io/servers/handling-errors/), [DummyJSON Products](https://dummyjson.com/docs/products). 원문 Python 샘플의 SDK v1 코드를 그대로 기준으로 삼지 않는다.

- 2026-10-07 README 개요와 계획 검토 후 2026-10-08 과제1 시험과 과제2 제출 코드의 기능 검토를 마쳤다. 과제2 문서 보완은 남아 있다.
- 원문: [Practical Implementation](../../04-PracticalImplementation/README.md).
- 목적: SDK·Tools/Resources/Prompts·테스트·배포를 실제 문제의 워크플로로 연결하고 성능·신뢰성·API 관리 관점을 다룬다. Python을 주 언어로 유지하며 다국어 예제는 선택 참고이다.
- 이전 학습과의 관계: Module03에서 기본 기능·Client/LLM·테스트·배포·인증을 안내된 실습으로 다뤘다. 이 모듈에서 이를 독립적인 요구사항·도구 설계·흐름에 적용하는 것은 아직 평가하지 않았다.
- 원문 구성: 언어별 예제 링크·핵심 기능 개요·페이지네이션 가이드·Azure API Management/Functions 예제와 배포·Inspector 연결·실제 문제의 3~4개 도구 설계/흐름 그림/1개 도구 구현/Prompt 과제이다. README 자체가 모든 성능 최적화·복잡한 워크플로 구현을 상세 실습으로 가르치는 것은 아니다.
- 재개: 수업 계획 요청 시 Python 예제와 페이지네이션 가이드를 필요한 범위에서 검토하고, 기존 개념 이해 기록을 참조한다. Azure 실습은 구독 준비와 학습 목적을 고려해 선택한다. README의 SSE 배포 절차·SDK 상태 등 버전 의존 정보는 실행 전 공식 문서로 확인한다.

## 수업 계획 제안 — 2026-10-07

- 당시 강의 계획 제안 근거: Python 샘플 소스·README와 pagination 가이드를 읽고 공식 SDK v2·2026-07-28 전송/페이지네이션·Azure APIM 문서를 대조했다. 이후 위 과제·검토 방식으로 변경했다. 기존 원문 파일은 수정하지 않았다.
- 잠정 주제는 상품 검색·재고 확인·견적 작성이다. search_products/get_inventory/calculate_quote 3개 Tool, 견적/배송 정책 Resource, build_quote Prompt를 설계한다. 학습자가 다른 실제 주제를 고르면 같은 목표에 맞춰 조정한다. 최소 한 도구의 입력/출력/실패 정책은 학습자가 구현하고, 나머지 공통 연결은 필요한 범위에서 안내한다.
- 순서: (1) 요구·3개 Tool 계약·흐름·완료 조건 설계 (2) 별도04/practice/.venv와 원문 Python 예제의 SDK v2 migration·Tool/Resource/Prompt 기준 동작 (3) 실무 Tool·Resource·Prompt 구성 (4) Python Client로 의존 호출·중간 실패 중단·Prompt 활용, 모델 연계는 기존 NVIDIA NIM 설정을 재사용하되 API 준비 시 확인 (5) 프로토콜 목록 페이지네이션 소규모 low-level 예제와 검색 결과 업무 페이지네이션 구분 (6) 단위/SDK 통합/실제 전송 검사의 선택 이유·실패 재현/복구, 반환량·시간·호출 수 측정과 timeout/선별 재시도 보강 (7) 인증·인가·제한·로그의 서버/게이트웨이 역할과 APIM 호환 범위·배포 개요, 실제Azure/Docker/원격배포는 선택.
- 필수 성취: 자체 계약과 흐름 설명, 최소 한 업무 Tool 구현, Resource 조회와 Prompt를 실제 요청 메시지로 활용, 단계 의존성/오류 제어를 갖춘 최소 Client 흐름, cursor의 불투명성/종료/잘못된 cursor를 설명·검사, 검사 범위에 맞는 테스트 선택, 한 성능 변경의 측정 근거. 프로덕션 수준 전체 운영이나 모든 언어/클라우드 이수를 뜻하지 않는다.
- 교정: 설치는 공식 mcp 또는 mcp[cli] 패키지 사용, 현재 stable v2의 MCPServer/Client와 snake_case 필드에 맞춘다. 기존 검증2.2.0을 기준 후보로 두되 새 환경 시작 시 안정 버전/호환성을 확인·고정한다. stdio Client가 Server를 실행하므로 별도 서버 선실행은 불필요하고 sys.executable·절대 경로를 사용한다. completion은 모의 응답이며 실제 LLM 실행으로 간주하지 않는다. Client 예제에 is_error 검사와 예외의 구분을 보강한다.
- 페이지네이션 교정: 원문 Python Server는 FastMCP가 아닌 low-level Server 예제이며 SDK v2는 생성자 handler 방식으로 변경한다. nextCursor 부재/None이 종료이고 빈 문자열을 종료로 취급하지 않는다. Client는 cursor를 파싱하지 않는다. 잘못된 cursor를 첫 페이지로 조용히 돌리지 않고 -32602로 처리하는 명세 권고를 적용한다. MCP 목록 페이징과 Tool 검색 결과의 자체 cursor 계약은 구분하며 모든 결과를 먼저 로드하는 구현의 성능 한계도 다룬다.
- 전송/운영 교정: 신규 HTTP는 Streamable HTTP를 사용하고 raw 요청은 MCP-Protocol-Version/Mcp-Method/Mcp-Name과 요청별 _meta 일치를 확인한다. SDK가 처리할 메타데이터를 무조건 수작업으로 재구현하지 않는다. 원문 /mcp/sse 절차를 새 서버에 일괄 적용하지 않는다. APIM 현재 외부 MCP 연계는 Tools/Resources 지원·Prompts 미지원이므로 전체 앱 투명 통과로 전제하지 않는다.
- 확인 방식: 관련 짧은 항목을 묶고 핵심 설계·오류 원인·검사 선택·결과 한계에서 비유도 질문/다른 사례 적용을 확인한다. 기존 Testing의 검사 선택 부분 이해·유한 검사 범위 미확인, Python Client의 async 연결 관리·반복/실패 결과 전달 미평가를 해당 단계에서 다시 다룬다. 설명이나 안내 실행만으로 평가를 올리지 않는다.

## 계획의 공식 기준

- [Python SDK](https://py.sdk.modelcontextprotocol.io/), [v1→v2 migration](https://py.sdk.modelcontextprotocol.io/migration/), [SDK pagination](https://py.sdk.modelcontextprotocol.io/advanced/pagination/).
- [2026-07-28 pagination](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/pagination), [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http).
- [Azure APIM 외부 MCP 지원 범위](https://learn.microsoft.com/en-us/azure/api-management/expose-existing-mcp-server).
