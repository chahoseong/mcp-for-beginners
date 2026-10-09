# Module05 — Advanced Topics

- 계획 검토일: 2026-10-09. [원문](../../05-AdvancedTopics/README.md)과 17개 단원의 범위·예제, 공식 명세/SDK/플랫폼 문서를 검토했다. 현재는 계획 제안 단계이며 수업·실습·새 이해 평가는 시작하지 않았다.
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

- 다음 수업은 전체 구조 개관과 5.16의 새 운영 동작부터 시작하는 계획이다. 현재 계획은 제안이며 사용자 승인/조정 전 구현하지 않는다.
- 기존 상태 참조: [Architecture](../understanding/architecture.md), [Transports](../understanding/transports.md), [Security](../understanding/security/INDEX.md), [Client Primitives](../understanding/client-primitives.md). 이번 계획 검토만으로 이해 등급을 변경하지 않았다.
- 검사는 약속한 계약·대표 사례에 맞춰 수행한다. 테스트 수를 성취 기준으로 쓰거나 실행 가능한 결과를 학습자에게 중복 전사하게 하지 않는다. 개념 판단과 협업 구현/실행 경험은 구분한다.
