# Module05 — Advanced Topics

- 계획 검토일: 2026-10-09. [원문](../../05-AdvancedTopics/README.md)과 17개 단원의 범위·예제, 공식 명세/SDK/플랫폼 문서를 검토했다. 2026-10-12 승인된 첫 수업(5.1 개관 → 5.16 요청 취소·자원 정리)을 마쳤다. 나머지 모듈은 미완료다.
- Python 중심으로 개념 설명→작은 관찰 실습→다른 사례의 판단 확인을 진행한다. Module04의 과제 중심 방식은 이번 모듈에 자동 적용하지 않는다. 기존 평가와 협업 구현의 한계는 유지한다.
- 원문 목표: 멀티모달 구현, 확장 가능한 구조 설계, 보안 적용, 기업 AI 시스템/프레임워크 연계, 성능·신뢰성 개선. 필수/선택 구분은 원문의 공식 지정이 아니라 목표·선행 관계·학습 이력·환경을 고려한 수업 제안이다.

## 권장 순서와 범위

1. 5.1의 전체 연계 구조를 먼저 개관한다. 상세 연결 실습은 마지막에 진행한다.
2. 5.16: 진행/오류/템플릿은 기존 경험과 연결하고 취소·자원 정리·현행 요청 수명주기를 새로 다룬다.
3. 5.3 핵심 + 5.8: 토큰 발급/검증 책임과 grant 구분, 도구·대상별 권한, 외부 내용의 신뢰 경계와 감사 근거. 기존 JWT 실습을 반복하는 대신 남은 OAuth 발견/issuer·audience 이유를 설명한 뒤 필요한 범위만 확인한다.
4. 5.2: 공식 이미지 content와 텍스트를 반환/수신하는 Python 실습. Host 표시와 모델의 이미지 이해는 별개로 확인한다. 음성·유료 이미지 생성·비전 모델 연결은 선택 확장이다.
5. 5.14: 필요한 문맥 선택, 크기/신선도/권한, 실패·부분 완료 근거 보존을 비교한다.
6. 5.5 → 5.7: 목적별 라우팅과 부하 분산 구분, 병목 측정, 동시성 제한/캐시/수평 확장 판단. 작은 변경 전후 결과·요청/오류·시간을 비교하고 확장 구조를 설계한다. 실제 클러스터 구축은 선택이다.
7. 5.1 연계 실습: Azure 없이 Python Microsoft Agent Framework와 MCP Server를 실제 연결하는 보충 경로를 기본으로 제안한다. 기존 NIM의 OpenAI-compatible API를 우선 사용하되 해당 수업 전 framework/SDK/모델의 버전·도구 호출 호환을 확인한다. 프레임워크의 학습 범위는 한 Agent의 MCP 도구 사용까지이다.
8. README Exercise: 대표 사례의 멀티모달 요구·보안·변동 부하 구조·AI 연계·병목/완화를 한 설계로 묶는다. 이미 실습한 근거를 재사용하며 운영 환경 전체 구축을 종료 조건으로 추가하지 않는다.

## 단원별 분류

| 단원 | 제안 분류 | 범위와 근거 |
| --- | --- | --- |
| 5.1 Enterprise Integration | 핵심 필수, Azure 구현 선택 | 목표4. 연계 책임/도구 흐름과 한 프레임워크 실제 연결; Azure ML/Foundry 구축은 특정 플랫폼 선택이다. |
| 5.2 Multi-modality | 필수 | 목표1 직접 구현. 이미지+텍스트를 기본으로 하며 모든 매체/API 구현을 요구하지 않는다. |
| 5.3 OAuth2 Demo | 핵심 개념 필수, Java 구축 선택 | 목표3. 기존 JWT 검증과 OAuth 발급 흐름을 구분한다. Spring/클라우드 구축은 Python 기본 경로의 조건이 아니다. |
| 5.4 Roots | 선택, 호환/이전 검토 | deprecated이며 접근 통제와의 구분은 기존 기록에 있다. 상태/대안은 필수 과정에서 짧게 고지한다. |
| 5.5 Routing | 핵심 필수 | 목표2·4·5. 적절한 처리 경로와 부하 분산/권한 검사의 책임 구분을 배운다. |
| 5.6 Sampling | 선택, 호환/이전 검토 | deprecated. 직접 모델 API와의 차이는 이미 학습했으며 신규 legacy 구현은 요구하지 않는다. |
| 5.7 Scaling | 필수 | 목표2·5 직접 대응. 측정/개선과 구조 설계; Kubernetes/Redis 클러스터 전체 구축은 선택이다. |
| 5.8 Security | 핵심 필수 | 목표3·5. 신뢰 경계/권한/관측 근거 적용; 모든 Azure 보안 제품 설치는 선택이다. |
| 5.9 Web Search sample | 선택 | 검색 도메인의 종합 예제. 외부 API·오류·다중 도구 흐름은 Module04 경험과 겹친다. |
| 5.10 Realtime Streaming | 선택 | Kafka/Pulsar의 지속 이벤트 처리 요구가 있을 때 필요하다. 일반 MCP 진행 알림과 구분한다. |
| 5.11 Realtime Web Search | 선택 | 검색 신선도·다중 검색원·순위화라는 특정 요구. 일반 문맥/성능 목표는 핵심 과정에서 다룬다. |
| 5.12 Entra ID | 선택 | 특정 조직 IdP 적용. 기본 인증/인가 목표를 대체하지 않으며 조직 SSO가 필요할 때 진행한다. |
| 5.13 Foundry Agent | 선택, 5.1의 플랫폼 대안 | Azure 계정/서비스가 필요한 실제 연계 방법. 기본 프레임워크 연계의 대안이지 별도 필수 플랫폼이 아니다. |
| 5.14 Context Engineering | 핵심 필수 | 목표1·4·5 지원. 전달할 내용의 관련성/비용/정확성 판단이며 MCP 자체의 자동 기억 기능이 아니다. |
| 5.15 Custom Transport | 선택 | 기존 메시지 인프라 등의 특별한 조건이 있을 때 양쪽 구현/호환 부담을 감수한다. 표준 transport로 기본 목표를 충족한다. |
| 5.16 Protocol Features | 새 내용 필수, 기존 내용 복습 | 목표3·5. 취소/정리/오류 계약이 핵심; 진행/템플릿 반복 실습과 Tasks 확장 구축은 필수가 아니다. |
| 5.17 Adversarial Agents | 선택 | 특정 다중 Agent 판단 방식. 동일 도구/토론/판정 Agent만으로 정확성이 보장되지 않는다. |

## 원문 교정과 공식 근거

- [2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog): handshake/프로토콜 session 제거, Roots/Sampling/Logging deprecated, Tasks 확장 분리. 기존 session affinity·레거시 메시지 예제를 현행 설계의 기본으로 사용하지 않는다. 업무 상태/사용자별 권한은 여전히 별도 설계 대상이다.
- [공식 SDK v2](https://py.sdk.modelcontextprotocol.io/): 5.1/5.2/5.7의 일부 wrapper/가상 API를 실행 가능한 공식 예제로 간주하지 않는다. 5.2의 PIL 단색 이미지는 실제 AI 이미지 생성이 아니며 임의 imageBase64 JSON과 표준 이미지 content를 구분한다.
- [SDK cancellation](https://py.sdk.modelcontextprotocol.io/handlers/cancellation/): 취소 전파/스레드의 협력적 중단/정리와 transport 설정을 확인한다. HTTP json_response=True에서는 현행 연결의 handler 취소가 전파되지 않는 한계를 실습 설계에 반영한다. 취소와 이미 수행한 업무의 복원은 별개다.
- [HTTP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization): 인증 기능 선택 여부와 인증 지원 시 지켜야 할 요구를 구분한다. stdio에 HTTP OAuth 요구를 그대로 붙이지 않는다. 5.3의 client_credentials와 사용자 위임 Code+PKCE 흐름을 구분한다.
- [MSAL client types](https://learn.microsoft.com/en-us/entra/msal/msal-client-applications): public/confidential 기준은 credential을 안전하게 보관/사용할 수 있는 능력이다. 5.12의 local/remote만으로 구분하는 설명을 교정한다. 외부 Graph 자격과 MCP 접근 자격도 구분한다.
- [Agent Framework MCP](https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools), [compatible provider](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/openai): 5.1의 Azure 사례를 대체하는 Python 보충 경로. SDK/모델의 실제 조합은 아직 실행 검증하지 않았다.
- 라우팅/검색 신선도/캐시/메시지 브로커/판정 Agent의 기능을 MCP가 자동 보장한다고 설명하지 않는다. 선택 단원은 핵심 과정 이후 해당 요구가 있을 때 연결한다.

## 재개와 기록

- 요청 취소·자원 정리와 Error Handling 보강, 2026-10-13 승인된5.3 핵심+5.8 선택 범위 수업을 마쳤다. 다음은5.2 Multi-modality이며 Tasks Extension은 선택으로 유지한다. 실제 SDK async 정리·공유 자원 lifespan의 독립 구현과 HTTP 취소 실행은 확인하지 않았다. OAuth·보안 완료 범위와 한계는 아래 요약과 개념 기록에 둔다.
- 최신 개념 근거: [Python 비동기·정리](../understanding/python-client.md), [취소 관찰](../understanding/transports.md), [Server 자원 수명](../understanding/tools-resources-prompts.md). 2026-10-12 수업 종료 시 구조를 점검하고 대기 중/미실행 문구와 라우팅을 갱신했다. 별도 파일 이동은 필요하지 않았다.
- 기존 상태 참조: [Architecture](../understanding/architecture.md), [Transports](../understanding/transports.md), [Security](../understanding/security/INDEX.md), [Client Primitives](../understanding/client-primitives.md). 이번 계획 검토만으로 이해 등급을 변경하지 않았다.
- 검사는 약속한 계약·대표 사례에 맞춰 수행한다. 테스트 수를 성취 기준으로 쓰거나 실행 가능한 결과를 학습자에게 중복 전사하게 하지 않는다. 개념 판단과 협업 구현/실행 경험은 구분한다.
- 2026-10-12 범위 설명 보완: 첫 수업 완료는 원문의 모든 항목을 새로 가르쳤다는 뜻이 아니다. Progress/Resource Templates는 기존 실습 근거를 재사용하고 Error Handling의 기본 실패 구분도 반복하지 않았다. 오류 코드 선택·예외 변환 설계 전체는 미학습 범위로 남긴다. Logging Control은 deprecated이므로 신규 구현을 생략하고 실제 stderr/파일 로그를 사용했다. Tasks 확장 구현은 선택이며 asyncio.Task와 별개다. Tool Annotations의 권한 비보장 근거는 기존 기록을 유지하고 신뢰 경계는 이후 보안 수업과 연결한다. TypeScript와 실제 DB/cache 구축은 Python 중심 범위에서 제외했다.

## 첫 수업 상세 계획 — 2026-10-12

- 추가 승인 범위: Error Handling Patterns를 지금 보강한다. 목표는 JSON-RPC error/도구 isError 선택 이유, 예상 실패를 보존하는 작은 Python 예외 처리 분석·수정, 응답과 로그의 정보 분리이다. 교사는 현행 SDK 확인·연결 보조 코드를 맡고 학습자는 분류와 핵심 수정 이유를 판단한다. 완료 기준은 다른 사례의 설명과 해당 코드의 작은 수정·대표 동작 확인이며 대규모 오류 클래스/테스트 구축은 요구하지 않는다. 첫 설명은 요청 구조/이름 문제와 도구 입력/실행 실패의 구분이며 답변 전 새 이해 등급을 부여하지 않는다. 원문 예외 이름만으로 JSON-RPC 코드에 매핑하는 방식을 현행 tools 오류 계약으로 교정한다.
- Error Handling 완료: 요청 형식 누락/외부 API 실패의 분류와 이유를 확인했다(Transports). MCP2.3.0과 [공식 SDK 오류 처리](https://py.sdk.modelcontextprotocol.io/servers/handling-errors/)를 대조했다. 학습자가 ToolError 재전파를 먼저 추가했고 교사가 들여쓰기만 정렬한 실제 stdio 호출(-1 실패 설명 유지/2 성공)을 확인했다. 응답의 비밀값 노출 문제를 지적하고 구체적 로그 설명 보충 뒤 도구·요청ID·예외 종류를 선별하는 로그를 작성했다(Tools 기록). 클래스/예외 객체의 이름 문법은 교사가 교정했으며 정확한 문법은 채점 조건이 아니었다. 예상 밖 SDK 경로와 마스킹 체계의 전체 구현은 미확인으로 유지한다. 종료 시 구조를 점검해 중복 평가를 만들지 않고 진행 위치·라우팅만 갱신했다.

- 상태: Task/취소 설명과 학습자의 finally 수정, 교사의 실제 파일 닫힘 검사를 확인했다. 관찰 사례의 평가 오류는 위 정정 근거를 따른다. open 실패 대응은 채점 범위 밖 보강이며 실제 SDK 실습은 아래 환경/검증을 따른다.
- 목표 역량: Client 대기 중단·Server 작업 중단·정리 완료를 구분하고 코드/로그/실제 임시 파일 상태로 정리 누락을 진단·부분 수정한다. 실행 성공과 개인 분석/수정 능력은 별도 평가한다.
- 선수 설명: handler, async def/await, 실행 중인 Task, 취소와 timeout, try/finally. 필요한 예제를 먼저 제공하며 AnyIO 전반이나 스레드 구현 경험을 전제하지 않는다.
- 진행: Host/Client/Server 그림 → transport별 취소·handler·정리 시간축 → 정상 실행 → 사용자 중단/timeout 비교 → 작은 정리 누락의 판단·수정 → 요청 자원과 Server lifespan 구분.
- 실습: 독립 Python SDK v2 서버/클라이언트, stdio, async 도구 한 개, 항목별 모의 처리와 임시 파일. 정상 완료·사용자 중단·timeout에서 Client 상태, Server 처리/정리 로그, 실제 파일 잔류를 비교한다. 중단은 처리 시작/진행을 확인한 뒤 수행해 우연한 완료를 줄인다.
- 분담: 교사는 환경·연결·로그·자동 확인 보조 코드를 준비/검사한다. 학습자는 관찰 결과와 핵심 코드를 분석하고 설명 후 작은 정리 누락을 판단·수정한다. 코드/문서/로그는 허용하고 AI가 핵심 진단을 먼저 대신하지 않는다. 받은 도움을 구분한다.
- 완료 근거: Client 출력만으로 중단을 확정하지 않고 Server 동작/자원 상태와 연결; 정상/중단/timeout의 자원 처리 확인; 배운 범위의 다른 누락 사례에서 핵심 판단/수정 이유 제시. 타이핑 분량·모든 테스트 개인 승인·전체 독립 서버 작성은 조건이 아니다.
- 보강: 취소와 rollback 구분, 완료/취소 경합, finally의 적용 범위, await가 필요한 정리의 제한된 shield. 동기 def의 협력적 취소는 개념 비교이며 전체 스레드 구현은 선택이다. 강제 종료·프로세스 장애 내구성은 이번 완료 조건에서 제외한다.
- 교정: 원문의 Server/@tool 혼용·mcp.types.CancelledError·ctx.is_cancelled·asyncio.Task.request_id를 공식 v2 코드로 간주하지 않는다. 취소를 잡아 정상 반환/부분 결과 전달하는 예제를 취소 결과 계약으로 사용하지 않는다. lifespan의 yield 뒤 정리는 finally와 정상 shutdown 조건을 함께 설명한다.
- [현행 취소 명세](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation): stdio는 notifications/cancelled에 요청 ID를 참조; HTTP는 해당 SSE 응답 스트림 종료가 신호이며 취소 알림을 보내지 않는다. 경합과 최종 응답 부재의 한계를 함께 다룬다.
- [SDK cancellation](https://py.sdk.modelcontextprotocol.io/handlers/cancellation/), [lifespan](https://py.sdk.modelcontextprotocol.io/handlers/lifespan/): Client Task 취소/read_timeout_seconds와 handler 전파를 사용한다. HTTP json_response=True(현행)/stateless_http=True(레거시) 제한을 구분한다. await 정리는 시간 제한을 둔 shield로 보호한다. HTTP 실제 비교는 stdio 핵심 관찰 이후 선택 보강이다.

## OAuth·보안 상세 수업 제안 — 2026-10-12

- 상태/자료: 학습자가 상세 계획과 선택 범위를 승인해 2026-10-12 수업을 시작했다. 원문 5.3/5.8, [현행 인가](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization), [발견](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery), [M2M 확장](https://modelcontextprotocol.io/extensions/auth/oauth-client-credentials), [SDK 서버](https://py.sdk.modelcontextprotocol.io/run/authorization/), [SDK Client](https://py.sdk.modelcontextprotocol.io/client/oauth-clients/)과 설치된 MCP2.3.0을 대조했다. 역할과 grant 및 발급 주소 확인, issuer/audience 거부 이유를 확인했다(인증 기록). well-known 주소 구성과 OAuth resource/MCP Resource 구분, 발견한 값과 발급 요청의 연결을 보충했다. 교사가 아래 실제 OAuth 실습을 준비·검증했고 학습자는 실행을 보고했다. 현재 SDK에 위임된 코드 흐름을 보충한다.
- 목표/순서: AS/Client/RS 역할과 OAuth/OIDC 구분 → 사용자 위임 Code+PKCE 대 M2M client_credentials → 401/PRM/AS 메타데이터 발견 → 서명/issuer/audience/resource/scope 각각의 판단 → 로컬 Python 발급·발견·실제 MCP HTTP 호출 관찰 → 작업/대상 권한과 외부 정보의 신뢰 경계·최소 감사 근거. 관련 단위를 묶어 의미 있는 지점에서 질문하고 답변을 기다린다.
- 시각 자료: 역할 배치도와 번호 있는 시간축, 두 grant의 사용자/브라우저/Client 레인 비교, 서로 다른 메타데이터의 목적지 지도, 토큰/검사 비교 카드, 실제 HTTP 헤더·서버 로그의 같은 요청 비교, 단계 선택/조건 변경이 도움이 되는 구간의 상호작용 자료를 사용한다. 가상 시뮬레이션과 실제 실행 자료를 구분한다.
- 재개 보충: well-known과 OAuth resource/MCP Resource 구분 설명 뒤 학습자가 메타데이터 조회와 발급 요청의 연결을 요청했다. 문서를 찾는 단계와 그 값으로 요청을 만드는 단계를 따로 설명한 한계를 보완한다. MCP 메타데이터의 resource는 보호 대상, 인가 서버 메타데이터의 token_endpoint는 발급 요청 주소로 연결하고 실제 Client 자격·scope 검사와 토큰 사용까지 한 흐름으로 보여준다. 새 연결 판단 근거가 없으므로 기존 등급을 유지하고 실습 완료로 간주하지 않는다.
- 실습/분담: Python 독립 practice에서 교사가 학습용 발급 서비스·SDK 연결/관찰 코드를 준비하고 현재 SDK 인자를 검사한다. 학습자는 발급/발견 응답과 토큰 대상·권한의 핵심 조건을 분석하고 새 사례를 판단한다. 설치형 Client의 브라우저 Code+PKCE 전체 구현, Java/Spring·Azure/Entra 구축은 선택이다. 실제 기본 실행은 발견→M2M 토큰 발급→MCP tools 호출이며 HTTP auth를 건너뛰는 in-memory/stdio로 검증을 대체하지 않는다. 기존 JWT 변조/만료 반복·대규모 테스트/AS 독립 개발은 요구하지 않는다.
- 교정: /hello HTTP 데모를 MCP tools 호출의 증거로 간주하지 않는다. client_credentials는 OAuth의 M2M grant이며 MCP에서는 별도 인가 확장이다. OAuth는 인가, 사용자 로그인/신원은 관련 인증 처리와 구분하고 JWT는 토큰 형식의 선택이다. aud를 Client ID로 고정하지 않고 MCP 대상 식별자/검증 설정과 맞춘다. 서명 유효만으로 수락하지 않는다. HTTP 인가 거부(401/403)와 도구 업무 실패의 isError를 구분하며 기존 수업의 tool-scope 예외 설계를 규범으로 일반화하지 않는다.
- 현행 범위: HTTP 인가 지원 시 발견/대상 검증과 매 요청 credentials를 적용하고 stdio에 같은 흐름을 붙이지 않는다. Client 등록은 실습에서 사전 등록을 사용한다. 기존 사전 등록 정보가 있으면 먼저 사용하고, 없으면 지원되는 CIMD, 이후 호환용 DCR 순서이며 DCR은 deprecated라고 고지한다. 브라우저 흐름의 authorization response iss 검사와 Access Token issuer 검사는 서로 다른 위치로 설명한다. 설치된 ClientCredentialsOAuthProvider는 scope(단수)·issuer를 받으며 웹 확장 예제 scopes 표기를 그대로 복사하지 않는다. audience/resource 검사는 검증기 또는 AuthSettings의 명시 설정으로 준비하고 자동 보장으로 설명하지 않는다.
- 완료/평가: 역할·grant 선택의 이유, 발견 단계의 다음 목적지, 신뢰된 서명이 있어도 잘못된 대상의 토큰 거부 이유, 사용자/작업/대상 권한의 검사 위치를 배운 범위의 다른 사례로 설명한다. 준비된 실제 Python 발급·발견·MCP 호출을 관찰하고 성공/거부를 연결하는 근거를 구분한다. 전체 IdP 구현 숙달은 주장하지 않는다. 로그 항목 선택은 앞선 Error Handling 근거를 재사용하며 외부 API 자격과 MCP 자격, 외부 응답과 작업 지시의 신뢰 경계를 보안 수업에 연결한다.
- 2026-10-12 제외 범위 설명: OAuth 원문의 Java/Maven Quick start·Testing은 Python의 실제 MCP 흐름으로 대체한다. Container build는 기존 Docker 학습 재사용으로 선택, Production Security는 기본 보관/권한/운영과의 차이를 개요로 다루되 운영 IdP·키 회전·Key Vault 전체 구축은 선택이다. Azure Container Apps와 API Management는 계정·특정 배포/게이트웨이 기술이므로 선택으로 둔다. 보충 Code+PKCE는 개념 필수/브라우저 전체 구현 선택이다.
- Security 섹션별 범위: Entra/.NET/Java의 제품 구현, Prompt Shields/Content Safety 연계, Application Insights/Log Analytics 구축은 선택이며 인증/신뢰 경계/감사 원리는 핵심에 남긴다. Confused Deputy와 Token Passthrough 예방의 구간·동의/권한 판단은 핵심, 전체 OAuth 프록시·토큰 교환 구축은 선택이다. Session Hijacking의 레거시 프로토콜 세션 구현은 현행 업무 상태 식별자 접근 통제로 교정하고 Redis/세션 암호화 구축은 요구하지 않는다.
- 운영 확장: Advanced Threat Detection Pipeline의 위험 점수·이상 탐지·자동 대응은 운영 근거가 필요한 별도 주제로 유보한다. Supply Chain Security Integration의 기본 위험은 Module02 근거를 연결하고 GitHub Advanced Security/Defender/SBOM 자동 통합은 선택이다. Best Practices Checklist는 프로토콜 요구/배포 조건/제품 선택을 구분해 개요에 사용하고 Microsoft Security Ecosystem Benefits는 참고로 둔다. 학습목표의 운영 샌드박스 전체 구축도 선택이다. 이번 계획은 두 README의 모든 제품 구현 목표를 완료하는 과정이라고 주장하지 않는다.

## 실제 실습 준비·교사 검증 — 2026-10-12

- OAuth 위치/분담: [OAuth practice](../../05-AdvancedTopics/mcp-oauth2-demo/practice/README.md)에 독립 Python3.12.10/MCP2.3.0 환경·uv.lock·자격 생성·발급 서비스·보호 MCP 서버·관찰 Client를 교사가 준비했다. 학습자는 발견/발급 요청과 도구 결과의 연결을 관찰하며 전체 보조 코드 검토를 요구하지 않는다. 실습의 opaque 토큰은 별도 자격으로 보호된 Token Introspection을 통해 검증하므로 기존 JWT 변조 실습을 반복하지 않는다.
- OAuth 실제 검증: 별도 loopback 프로세스(AS9100/MCP8100)의 초기401→PRM→AS 메타데이터→resource와 scope를 포함한 발급→MCP get_quote(is_errorFalse, total20.00USD)를 확인했다. 잘못된 Client 자격401/다른 발급 대상400 거부도 확인했고 검사 후 교사 소유 프로세스만 종료했다. 자격/토큰 값을 출력하지 않았고 .env/.venv는 Git 제외를 확인했다. 학습자의 안내된 실행·독립 이해는 이 검사 성공과 별개다.
- OAuth 학습자 실행/보완: SDK에 감춰진 흐름의 설명을 요청한 뒤 실제 PRM 조회 로그를 설명한 구간과 연결했다. 2026-10-13에는 Tools=['get_quote']/is_errorFalse/데모 상품 수량2·총액20.00USD의 최종 결과도 제출했다. 제공된 실제 발급·발견·보호 MCP 호출의 정상 관찰을 확인했고 인증 기록에 최신 근거를 보존했다. 독립 전체 구현/운영 보안 숙달로 일반화하지 않는다.
- OAuth 흐름 보충의 경위/적용 범위: 학습자는 SDK에 숨겨진 중간 단계가 개념 흐름과 연결되지 않고 표준/실습 정의도 구분하기 어렵다고 설명했다. 이번 프로그램은 전체→단계→실제 코드→세부 규칙과 다양한 시각 자료로 재구성한다. 학습자는 이를 전체 학습 선호로 확장하지 말라고 정정했고 교사가 공통 RULES에 추가했던 두 항목을 삭제했다. 이 방식은 이번 프로그램에만 적용한다. 승인된 전체 지도에서 접근 준비(토큰 없는 첫 요청/401/두 메타데이터/발급·저장)부터 실제 코드에 대응한다. 기존 등급을 유지하며 앞서 제시한 set_quote 권한 질문은 맥락 보완 동안 보류한다.
- OAuth 교정/한계: SDK2.3.0 OAuthMetadata가 client_credentials만 지원하는 서비스에도 authorization_endpoint를 필수로 요구한다. RFC8414의 선택 조건과 구분하여 브라우저 grant를 거부하는 호환 endpoint를 제공하고 지원 목록은 client_credentials/빈 response_types로 유지했다. Client는 이 endpoint를 호출하지 않는다. 학습 서비스는 메모리·loopback HTTP이며 운영 IdP 전체 구축이나 장애 분류까지 구현한 것으로 간주하지 않는다.
- 2026-10-13 도구별 권한 보충: opaque 토큰 전달과 SDK 검사·실제 호출을 연결하고 최종 결과를 확인했다. 도구별 scope 구분을 지적한 답변에 부족했던 API 설명을 보완했다. 설치 SDK의 tool()에는 scope 설정 인자가 없으며 get_access_token()은 검증된 요청 정보를 읽고 ContextVar로 동시 요청의 문맥을 구분한다고 설명했다. 이후 도구별 검사 위치·조건·작업 전 순서의 이해를 확인했다(인증 기록). 실제 확장 구현·HTTP403 거부 응답·독립 운영 숙달은 미확인이다. OAuth scope 거부와 업무 ToolError의 구분을 유지한다.

- 2026-10-13 대상별 접근 보충: OAuth 범위와 업무 접근 정책의 연결을 먼저 설명했다. 요청 입력과 서버 조회 값의 출처 혼동을 보충한 뒤 다른 부서 문서 사례에서 정보 출처와 거부 근거를 확인했다. 상세 답변과 교정 이력은 인증 기록에 보존한다. 전체 서버 확장은 구현하지 않았다.
- 2026-10-13 OAuth·보안 핵심 수업 마무리: 기존 Token Passthrough 근거와 연결해 외부 API 자격 분리, 외부 데이터/작업 지시의 경계·자료형 검증의 한계·권한 검사만으로 작업 목적을 보장하지 못함을 보충했다. 이 구간은 설명과 이해 자기 보고이며 새 독립 적용 평가는 하지 않았다. 최소 감사 이벤트와 안전한 정보 선별을 설명하고 제공된 로그의 권한 허용/작업 timeout 실패 해석을 확인했다(인증 기록). 실제 실행은 준비된 기본 OAuth 발급·발견·도구 호출이며 권한 확장·공격 차단·감사 시스템이나 운영 IdP를 구축한 것으로 간주하지 않는다. 종료 시 현재 위치와 인덱스 라우팅을 점검했고 파일 분리·이동은 필요하지 않았다. 다음은 승인된 순서의5.2이다.

- 2026-10-13 계획 대조 재검토: 주요 개념과 기본 실제 HTTP 실습은 다뤘지만 모든 세부 고지를 충분히 설명했다고 일반화한 완료 문구를 구체화했다. OAuth/OIDC 구분, 사전 등록/CIMD/호환 DCR 선택, 브라우저 인가 응답의 issuer 검사와 서버의 토큰 issuer 검사의 위치, OAuth 프록시의 클라이언트별 사용자 동의 연결을 마무리 정리에서 개요로 보강한다. 보강은 설명이며 독립 이해 평가로 쓰지 않는다. 등록 우선순위는 공식 명세와 대조해 기존 사전 등록이 있으면 그것을 먼저 사용하는 것으로 명확히 했다. Code+PKCE·등록/프록시·운영 제품 전체 구축은 승인된 선택 범위로 유지한다.

- 2026-10-13 첫 OAuth 노트 작성·가독성 보완: 학습자가 전체 학습을 하나의 노트에 합치지 않고 구현과 독립적인 역할·발견·발급·사용/검증 흐름을 첫 문서로 정하기를 요청했다. 내용 논의와 파일명·제목·구성을 승인한 뒤 GPT-6.1 Sol/High 서브에이전트가 [접근 흐름 노트](../../notes/oauth2/mcp-oauth2-flow.md)를 작성했고 주 에이전트가 공식 명세와 흐름·용어·Markdown 구조를 검토·보완했다. 학습자의 긴 설명 문단에 대한 피드백에 섹션2/3 샘플을 제시하고 승인 후 문서 전체를 핵심 한 줄·그림·짧은 설명 블록·목록·메모·비교표로 수정했다. 공식 용어의 한글/영문 병기와 섹션별 첫 등장 설명을 유지했다. 이는 이번 노트의 작성 요구이며 공통 학습 규칙을 확장하지 않는다. 문서 작성이나 동의 답변만으로 이해 등급을 변경하지 않았다.

- Error Handling 정보 분리 설명 보완: 학습자가 비밀값 노출 문제는 지적했으나 로그 항목/방법의 구체적 설명을 받지 못했다고 알렸다. 교사가 설명 부족을 인정해 예시·선별 로깅을 보충했고 이후의 로그 선택 근거는 Tools 기록에 보존했다. 설명 부족을 학습자의 오개념으로 평가하지 않는다.

- 위치: [practice/README](../../05-AdvancedTopics/mcp-protocol-features/practice/README.md). 독립 Python3.12.10/MCP2.3.0/AnyIO4.15.1 환경과 uv.lock을 생성했다. Server 도구 process_items 한 개, Client normal/cancel/timeout, stderr 로그와 요청별 임시 파일 관찰을 준비했다. 학습자의 finally 적용을 처리 블록에 반영했으며 주변 코드는 교사 작성이다.
- 실제 검증: 별도 프로세스 간 stdio/MCP2026-07-28. normal은 세 항목/structured result3/is_errorFalse, cancel은 첫 진행 후 명시 Task 취소, timeout은 asyncio.wait_for의1.5초 기한. 세 경우 모두 파일 닫힘/삭제와 정리 뒤 tools/list 응답, 종료코드0을 확인했다. 런타임에 파일 잔류가 없었다. 직접 HTTP 비교/동기 도구/await 정리 보호는 이번 실행에 포함하지 않았다.
- 학습자 실행/진단 능력은 교사의 검사 성공과 별개다. 전체 JSON 전사를 요구하지 않았다. 마지막 progress callback은 Server 정리 후 실행될 수 있어 파일 상태 문구는 관찰 시점을 표시한다. stdout/stderr 결합 순서를 프로토콜 추적으로 간주하지 않는다.
- 학습자 정상 관찰: 안내한 normal 실행에서 Tool result는 result3, 정리 후 파일 존재는False를 제출했다. 준비된 코드 실행을 독립 구현으로 평가하지 않는다. 취소/timeout 관찰의 최신 근거는 아래에 둔다.
- 로그 보완: 학습자의 Server 로그 미표시 보고에 따라 명시 INFO logger로 stderr와 runtime/server.log에 기록하도록 교사가 수정했다. Client는 종료 후 절대 로그 경로를 안내한다. 실제 원인은 미확정이므로 학습자의 잘못으로 판단하지 않는다. stderr를 숨긴 cancel 실행에서 Server 취소/정리 로그가 파일에 저장되고 .part 잔류없음/Server후속응답True/종료코드0을 검증했다. server.log는 최신 실행 기록으로 남기고 새 Server 시작 시 덮어쓰며 작업용 임시 파일과 구분한다.
- 학습자 cancel 관찰: 로그 보완 뒤 재실행을 보고했고 교사가 alpha1/3→취소로 중단→정리 완료(file.closedTrue)/.part 잔류없음을 읽었다. 학습자는 Server still responds=True를 제출하고 작업 취소·정리 완료·Server 후속 요청 가능을 설명했다. 제공된 실행/로그 조건의 판단이며 전체 독립 구현으로 일반화하지 않는다.
- 학습자 timeout 관찰: Call deadline reached/정리 후 파일 존재False를 제출했다. 교사가 현재 Server 취소·정리 완료 기록과 .part 잔류없음을 확인했다. 종료 기한에 의한 안내된 실행 경험이며 timeout 독립 구현/판단으로 일반화하지 않는다.
- await 정리 보강: 공식 SDK와 AnyIO4.15.1 문서/설치된 jsonrpc_dispatcher의 CancelScope를 대조했다. 교사가 별도 짧은 AnyIO 모의 취소 범위에서 보호없는 await 정리완료False, shield있는 정리완료True를 실행 확인했다. 실제 Server 도구의 자원정리 코드는 여전히 동기 close/unlink이며 MCP 전체 async cleanup 실습을 했다고 기록하지 않는다. 자체 기한/외부 취소 구분의 학습자 판단은 Python 개념 기록에 둔다.
- lifespan 보강: 요청 파일과 공용 API Client의 소유·수명을 그림과 가정한 생성 함수의 구조 코드로 설명했다. 학습자는 공유 Client를 도구에서 닫아 다음 호출이 실패한다고 진단하고 Server 종료 때 닫아야 한다고 설명했다. 자원 수명 판단의 근거이며 실제 공용 API/DB를 구축하거나 lifespan을 독립 구현한 근거는 아니다.
