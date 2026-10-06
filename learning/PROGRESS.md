# Learning Progress

에이전트의 수업 재개 지점이다. 전체 문서 라우팅은 [INDEX.md](INDEX.md), 학습·기록 규칙은 [RULES.md](RULES.md)를 참고한다.

## 현재 위치

- 마지막 학습일: 2026-10-06 (Asia/Seoul)
- 현재 모듈: [03 — Simple Auth](../03-GettingStarted/11-simple-auth/README.md), 핵심 학습·실습과 OAuth 보충 설명을 마무리했다(2026-10-06).07은 선택 보류이다.
- 현재 수업 기록: [Module 03](lessons/03-getting-started.md)
- 진행: Bearer/JWT·변조/만료/issuer/audience 거부·세 역할의 도구 권한·visitor HTTP403을 실제 HTTP로 확인했다. 학습자가 새 operator 정책과 권한 검사 전 상태 변경의 가상 오류를 설명했다. OAuth 발견·브라우저/콜백·Code/PKCE·토큰 사용, JWT가 필수가 아님과 실습 scope가 자체 정의임을 보충했다. 보충 범위의 독립 이해 평가는 없다.
- 실습 위치: 11-simple-auth/practice/·별도 .venv, localhost Streamable HTTP. .env MCP_ACCESS_TOKEN·server.py와 client.py의 안내된 실제 실행을 확인했다. 이전 배포 실습의 로컬 정리 실행은 미확인이고 Render 삭제는 요청되지 않았다.
- 다음 행동: 학습자의 질문 또는 다음 단원 요청을 기다린다. 요청 시 README와 관련 기록을 읽어 계획한다. reader 복원·서버 중지는 안내했으나 실행 출력은 미확인이다. issuer/audience의 독립 검사 이유·실제 OAuth 발급/배포는 미평가/미실습으로 이어간다.
- 필요한 개념 기록: [Authentication and Access](understanding/security/authentication-and-access.md), [Python Client](understanding/python-client.md).
- 이어갈 미해결 항목: 종료 코드0의 정확성 한계는 보충 후 다른 사례에서 재확인, async with·asyncio.run의 독립 설명, LLM에 실패 결과 전달·복수/반복 호출 구현. 기존 안내 실습을 전체 독립 구현 능력으로 일반화하지 않는다.
