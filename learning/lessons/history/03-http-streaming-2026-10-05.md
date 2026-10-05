# HTTP Streaming 학습 이력 — 2026-10-05

단원 요약의 누적 내용을 보존했다. 아래 미래형 계획·미확인 문구는 당시 상태이며 최신 상태는 상위 모듈 요약과 개념 기록을 따른다. 문서 이동만으로 평가를 변경하지 않는다.

## HTTP Streaming 단원 계획

- 보안 설명 보충: Origin 검증·CORS와 브라우저 집행을 설명했으나 웹페이지가 다른 서버에 요청한다는 배경이 부족했다. 학습자가 응답 링크·서버의 날씨 API 이용 표시인지 질문해 Client→MCP Server→외부 API의 통신 구간으로 재설명한다. CORS 이해는 아직 미확인이며 인증 등 과거 평가를 변경하지 않는다.
- 목록 과제 완료: 학습자가 files:list[str] 입력·enumerate·total=len(files)·join 반환을 구현했다. 네 항목 알림1/4~4/4와 정상 결과 확인 후 두 번째 입력에 네 항목이 남아 있음을 피드백했다. 수정한 두 항목 실행은1.02초1/2·2.03초2/2·최종2.09초·is_error=False·두 이름을 반환했다. 요구사항과 기존 코드 기반 수정이며 독립 전체 구현으로 일반화하지 않는다. 다음으로 README 보안 역할 구분을 설명한다.
- MCP 실행: practice/mcp_server.py·mcp_client.py의 URL 연결·add result21 확인 후 report_progress/progress_callback으로 세 파일 처리 시뮬레이션을 실행했다. 학습자 출력은 진행1/3=1.02초·2/3=2.04초·3/3=3.05초, 최종결과3.11초·is_error=False였다. Progress/Notification 관계를 보충하고 진행3/3 후 저장 실패의 최종 응답을 근거로 전체 실패 판단을 확인했다. 입력files:list[str]·가변 길이 목록 과제를 안내하며 실제 파일 I/O·독립 전체 구현 능력으로 일반화하지 않는다.
- 비교 확인: response.text에서 5.06초에 본문 전체가 출력되었고, 학습자는 줄 완성 시 반환하는 iter_lines와 전체 응답을 기다리는 읽기 방식의 표시 차이를 설명했다. 일반 streaming 코드를 복원하고 MCPServer/Client의 URL 연결·목록·add 기본 호출을 안내한다. 진행 알림은 다음 단계이다.
- 일반 HTTP 실습: 별도06 .venv Python3.12.10·MCP2.2.0·imports 성공과 practice/http_server.py·http_client.py의 Message1~5 순차 출력(0.07~4.11초), 종료5.11초를 확인했다. README Simple Example에 asyncio.sleep·작은 iter_lines chunk_size·경과 시간 표시를 보충했다. chunk_size=1의 바이트 단위 질문에 읽기 크기와 줄·네트워크 패킷의 구분을 설명하고 response.text 비교를 안내한다. 독립 설명 평가는 아직 하지 않았다.
- 계획 승인 후 첫 수업: 독립 HTTP 서버·URL endpoint·streaming·SSE와 진행 알림/최종 결과를 설명했다. 학습자는 현재 처리 이미지·완료 개수 표시를 제안하고 후속 사례의 최종 실패 응답으로 이미지1 완료·이미지2 실패를 구분했다. 상세 근거와 확인 한계는 Transports에 둔다. 이후 별도06 .venv와 MCP2.2.0·fastapi·uvicorn·requests 설치를 안내했다.
- 2026-10-05: README·Python solution과 공식 2026-07-28 Streamable HTTP·Progress·Deprecated Features, Python asyncio·Requests·Parallel 문서를 검토했다. 별도 Learning Objectives 목록은 없으며 주요 절과 항목 처리 과제를 기준으로 수업 목표를 구성한다.
- 범위·순서: streaming·SSE·HTTP endpoint와 async/await의 필요한 전제 → 일반 FastAPI/requests streaming 비교 → MCPServer/Client의 URL 연결·목록·정상 호출 → Context.report_progress/progress_callback와 최종 결과 관찰 → 목록 처리 Tool·실시간 표시 과제 → localhost·Origin·CORS·HTTPS·인증 개념과 구형 HTTP+SSE migration. Parallel hosted 연결은 원문의 선택 확장으로 둔다.
- 실습 계획: 별도06 .venv·SDK 2.2.0을 사용하고 practice/에 일반 HTTP와 MCP 예제를 분리한다. local HTTP의127.0.0.1·포트·경로를 명시하고 서버/Client를 별도 터미널에서 실행한다. 기존 solution/python 코드는 참고·migration 대상으로 삼으며 원본 교육 문서는 이 계획 단계에서 변경하지 않았다.
- 교정: 구형 initialize·protocol Session ID·GET event stream·resumption을 현재 요청별 POST·버전/메서드/이름 헤더로 설명한다. Logging notification(ctx.info)을 Progress 알림과 구분하고 주 실습은 report_progress로 바꾼다. stdio도 알림을 지원한다. JSON 표기 오류·로그 레벨을 알림 종류로 취급한 표현·일반 HTTP streaming의 형식 일반화를 바로잡는다.
- Python 보완: async generator의 time.sleep은 await asyncio.sleep으로 교정한다. 작은 일반 streaming 예제에서는 requests.iter_lines의 buffering 조건을 조절해 도착 시점을 관찰한다. 실행 디렉토리는 solution/python이며 /stream과 /mcp, HTTP와 HTTPS, Starlette ASGI와 FastAPI 예제를 구분한다. 구형 ClientSession·FastMCP·LoggingCollector는 현재 Client·MCPServer·진행 callback으로 보완한다.
- 검증 근거·한계: 기존05 환경에서 현재 Client의 mode='2026-07-28', mcp.server.mcpserver.Context·report_progress와 progress_callback을 사용한 in-process 확인이 진행1/3·2/3·3/3과 최종result3·is_error=False를 반환했다. mode='modern'은 SDK2.2에서 허용 값이 아니었다. HTTP 네트워크 streaming을 실습·검증한 것으로 일반화하지 않는다. 새 개념 이해 평가는 아직 없다.

## 마지막 보안 확인과 마무리 범위

- 학습자는 팀원이 아닌 Python Client의 호출을 HTTPS·CORS만으로 막을 수 없으며 사용자 인증과 해당 요청 권한 검사가 필요하다고 답했다. 인증·인가 역할은 확인했으나 CORS 구현·원격 배포를 확인한 것은 아니다.
- 마지막 수업에서 구형 HTTP+SSE와 현재 Streamable HTTP를 구분하고 서버 transport·Client URL/SDK·진행 callback·최종 결과 및 실패 응답의 호환 검증을 설명한다. 실제 구형 Client 전환은 수행하지 않았다.

