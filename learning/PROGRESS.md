# Learning Progress

에이전트의 수업 재개 지점이다. 전체 문서 라우팅은 [INDEX.md](INDEX.md), 학습·기록 규칙은 [RULES.md](RULES.md)를 참고한다.

## 현재 위치

- 마지막 학습일: 2026-10-05 (Asia/Seoul)
- 현재 모듈: [03 — Deployment](../03-GettingStarted/09-deployment/README.md), 핵심 학습·실습 완료.07은 선택 보류이다.
- 현재 수업 기록: [Module 03](lessons/03-getting-started.md)
- 진행: 학습자가 Render /mcp의 정상 divide 응답(HTTP200·isError:false·result2.5)과 0 분모 오류 응답(HTTP200·isError:true·Cannot divide by zero)을 제출했다. 두 응답의 서버 이름은 deployment-practice-v2이다. 원격 목록은 에이전트 확인, 두 호출은 학습자 실행 근거이다.
- 실습 위치: 09-deployment/practice/의 server.py·requirements.txt·Dockerfile·.dockerignore, 로컬 이미지 v1/v2와 Render Web Service.
- 다음 행동: 로컬 컨테이너 중지 방법을 안내한다(실행 미확인). Render는 유지하며 삭제는 요청되지 않았다. 다음 단원은 학습자 요청에 따라 README를 읽고 계획한다.
- 필요한 개념 기록: [Deployment](understanding/deployment.md), [Transports](understanding/transports.md), [Python Client](understanding/python-client.md).
- 이어갈 미해결 항목: 종료 코드0의 정확성 한계는 보충 후 다른 사례에서 재확인, async with·asyncio.run의 독립 설명, LLM에 실패 결과 전달·복수/반복 호출 구현. 기존 안내 실습을 전체 독립 구현 능력으로 일반화하지 않는다.
