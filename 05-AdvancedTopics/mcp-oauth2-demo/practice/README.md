# OAuth 발견과 MCP 도구 호출 관찰 실습

이 Python 보충 실습은 이번 단원의 `client_credentials` 흐름을 실제로 관찰하기 위한 예제입니다.
로컬 메모리에서 동작하는 Authorization Server와 별도의 보호된 MCP Server를 실행합니다.
학습용 서비스이며 운영용 Identity Provider는 아닙니다. 로컬 컴퓨터의 loopback 주소에서
9100번과 8100번 포트를 사용하며, Azure 계정이나 모델 API는 필요하지 않습니다.

환경과 연결용 코드는 교사가 준비합니다. 학습자는 출력에서 요청의 목적지와
메타데이터의 값이 토큰 발급 요청에 어떻게 들어가는지 관찰합니다.
모든 보조 코드를 검토하거나 전체 로그를 복사할 필요는 없습니다.

## 최초 준비

PowerShell에서 이 실습 폴더로 이동합니다.

```powershell
cd C:\Users\chahoseong\mcp-for-beginners\05-AdvancedTopics\mcp-oauth2-demo\practice
```

가상환경과 로컬 자격 증명 파일을 준비합니다. 이미 준비되어 있다면 이 단계는 건너뜁니다.

```powershell
uv sync --python 3.12
uv run python prepare_env.py
```

생성된 `.env`에는 토큰 발급을 요청하는 Client의 자격 증명과,
토큰 검증 정보를 조회하는 MCP Server의 별도 자격 증명이 들어 있습니다.
이 파일은 Git에서 제외됩니다. 준비 명령을 다시 실행해도 기존 자격 증명은 유지합니다.
각 프로그램은 `--env-file .env` 옵션으로 이 파일을 읽습니다.

## 터미널 세 개에서 실행

터미널 세 개를 열고, 각각 위의 `cd` 명령으로 같은 실습 폴더로 이동합니다.
다음 순서대로 실행합니다.

```powershell
# 터미널 1: Authorization Server를 실행하고 유지합니다.
uv run --env-file .env python authorization_server.py
```

```powershell
# 터미널 2: 보호된 MCP Server를 실행하고 유지합니다.
uv run --env-file .env python server.py
```

```powershell
# 터미널 3: Client를 실행합니다. 예제 견적을 조회하면 종료됩니다.
uv run --env-file .env python client.py
```

관찰을 마치면 서버가 실행 중인 두 터미널에서 `Ctrl+C`로 종료합니다.
Client는 토큰을 해당 실행 동안만 보관하므로, 다시 실행하면 발급 흐름을 다시 관찰할 수 있습니다.
Authorization Server를 재시작하면 메모리에 보관한 토큰 기록은 사라집니다.

## 메타데이터와 요청의 값 연결하기

1. 토큰 없이 보낸 첫 MCP 요청에 대한 HTTP 401 응답은
   Protected Resource Metadata의 위치를 알려줍니다.
2. 이 메타데이터의 `resource`는 보호 대상인 `http://127.0.0.1:8100/mcp`를 식별하고,
   `authorization_servers`는 발급 서버인 `http://127.0.0.1:9100`을 알려줍니다.
3. Client가 조회한 Authorization Server Metadata는 실제 토큰 발급 주소인
   `/oauth2/token` endpoint를 알려줍니다.
4. SDK는 그 주소로 `client_credentials` 발급 요청을 보냅니다.
   요청에는 Client 자격 증명, MCP 대상의 `resource`, 필요한 `scope`가 들어갑니다.
5. Client는 발급받은 토큰을 제시하여 MCP 요청을 다시 보내고 `get_quote`를 호출합니다.

관찰용 hook은 필요한 항목만 출력합니다. 자격 증명, Authorization 헤더의 값,
토큰 값은 출력하지 않습니다. 이 출력은 모의 화면이 아니라 실제 HTTP 통신 관찰입니다.
SDK의 동작에 따라 추가 발견 요청이나 알림이 나타날 수 있습니다.

실행 후 다음 세 줄을 확인하여 제출합니다. 전체 로그는 필요하지 않습니다.

```text
CLIENT | Token request resource: ...
CLIENT | is_error: ...
CLIENT | structured_content: ...
```

## 이번 예제의 토큰 검증

이 예제는 JWT 대신 **opaque token**을 사용합니다.
토큰은 임의의 문자열이며, JWT처럼 내부 payload를 해석하여 정보를 얻는 방식이 아닙니다.
MCP Server는 Authorization Server의 보호된 **Token Introspection** endpoint에 조회하여
토큰의 활성 상태, 발급자, 대상, 만료 시각, Client와 scope를 확인합니다.

검증기는 발급자와 만료를 검사하고, `AuthSettings`는 대상과 필요한 scope를 명시적으로 검사합니다.
Introspection에 사용하는 HTTP Client는 재사용하며 MCP Server의 lifespan에서 닫습니다.
각 도구 호출이 끝날 때 닫지 않습니다.

이렇게 구성한 이유는 이전 JWT 실습을 반복하지 않으면서 발견, 발급,
대상 연결과 MCP 도구 호출을 실제로 관찰하기 위해서입니다.
Introspection 서비스에 연결할 수 없어 검증에 실패하면 접근을 허용하지 않습니다.
운영용 장애 분류, 요청 횟수 제한, 영구 저장, 로그인 화면, 토큰 무효화는 이번 예제에 구현하지 않았습니다.

## SDK 호환성 보충

SDK 2.3.0의 메타데이터 모델은 `authorization_endpoint`를 필수로 요구합니다.
하지만 [RFC 8414의 2절](https://datatracker.ietf.org/doc/html/rfc8414#section-2)은
해당 endpoint를 사용하는 grant를 지원하지 않으면 생략할 수 있도록 규정합니다.

이 예제는 SDK와의 호환을 위해 브라우저 grant를 거부하는 endpoint를 제공합니다.
지원 목록에는 여전히 `client_credentials`만 명시하며 `response_types_supported`는 빈 목록입니다.
이번 `client_credentials` 흐름에서는 해당 endpoint를 호출하지 않습니다.

## 참고 자료

- [SDK 서버 인가](https://py.sdk.modelcontextprotocol.io/run/authorization/)
- [SDK OAuth Client](https://py.sdk.modelcontextprotocol.io/client/oauth-clients/)
- [MCP Client Credentials 확장](https://modelcontextprotocol.io/extensions/auth/oauth-client-credentials)
- [Token Introspection 표준 — RFC 7662](https://datatracker.ietf.org/doc/html/rfc7662)
