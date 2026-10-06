# Learning Progress

에이전트의 수업 재개 지점이다. 전체 문서 라우팅은 [INDEX.md](INDEX.md), 학습·기록 규칙은 [RULES.md](RULES.md)를 참고한다.

## 현재 위치

- 마지막 학습일: 2026-10-06 (Asia/Seoul)
- 현재 모듈: [03 — MCP Inspector](../03-GettingStarted/13-mcp-inspector/README.md), 보충 수업 완료(2026-10-06).Module03은 선택한 학습 범위를 마무리했으며07·12는 선택 보류이다.
- 현재 수업 기록: [Module 03](lessons/03-getting-started.md)
- 진행: Inspector UI 정상 호출·Resource/Prompt 확인과 CLI 실패 비교를 마쳤다. 가상 저장 실패와 성공 표시가 있지만 계산값이 틀린 사례에서 조사 대상을 설명했다. 안내된 실행·목적 보충 뒤 진단의 한계는 Python Client 기록에 둔다.
- 실습 위치: 기존10-advanced/practice/server.py·10 .venv를 재사용하는 stdio 연결. 앞서 사용한 Inspector2.9.0을 기준으로 시작한다. 새 서버/가상환경은 만들지 않는다.
- 다음 행동: 학습자의 질문 또는 Module04 README 검토 요청을 기다린다. Inspector 종료를 안내하며 실제 중지 출력은 미확인이다.11 reader 복원·서버 중지 출력도 미확인이고 issuer/audience의 독립 검사 이유·실제 OAuth 발급/배포는 미평가/미실습으로 이어간다. 이전 로컬 배포 정리는 미확인이며 Render 삭제는 요청되지 않았다.
- 필요한 개념 기록: [Authentication and Access](understanding/security/authentication-and-access.md), [Python Client](understanding/python-client.md).
- 이어갈 미해결 항목: 종료 코드0의 정확성 한계는 보충 후 다른 사례에서 재확인, async with·asyncio.run의 독립 설명, LLM에 실패 결과 전달·복수/반복 호출 구현. 기존 안내 실습을 전체 독립 구현 능력으로 일반화하지 않는다.
