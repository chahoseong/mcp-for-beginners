# Learning Progress

에이전트의 수업 재개 지점이다. 전체 문서 라우팅은 [INDEX.md](INDEX.md), 학습·기록 규칙은 [RULES.md](RULES.md)를 참고한다.

## 현재 위치

- 마지막 학습일: 2026-10-06 (Asia/Seoul)
- 현재 모듈: [03 — Sampling](../03-GettingStarted/14-sampling/README.md), 개념·설계 비교 수업 완료(2026-10-06). 레거시 구현은 미실습이다.07·12는 선택 보류이며15-mcp-apps가 남아 있다.
- 현재 수업 기록: [Module 03](lessons/03-getting-started.md)
- 진행: Sampling이 아닌 Host 조언 사례의 판단 근거와 직접 NIM 상품 설명 도구의 흐름/Server 키 관리 설계를 확인했다. NIM→Server 응답 단계를 보충했다. 실제 새 코드/API 실행과 전체 독립 구현으로 일반화하지 않는다.
- 실습 위치: 기존10-advanced/practice/server.py·10 .venv를 재사용하는 stdio 연결. 앞서 사용한 Inspector2.9.0을 기준으로 시작한다. 새 서버/가상환경은 만들지 않는다.
- 다음 행동: 학습자의 질문 또는15-mcp-apps README 검토 요청을 기다린다. Sampling 레거시 유지보수나 Server 직접 NIM 구현은 선택 확장으로 남긴다. 이전 서버 중지·reader 복원·로컬 배포 정리는 미확인이며 Render 삭제는 요청되지 않았다.
- 필요한 개념 기록: [Authentication and Access](understanding/security/authentication-and-access.md), [Python Client](understanding/python-client.md).
- 이어갈 미해결 항목: 종료 코드0의 정확성 한계는 보충 후 다른 사례에서 재확인, async with·asyncio.run의 독립 설명, LLM에 실패 결과 전달·복수/반복 호출 구현. 기존 안내 실습을 전체 독립 구현 능력으로 일반화하지 않는다.
