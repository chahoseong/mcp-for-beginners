# Python MCP Client — 최신 이해 기록

- 학습 근거: [Module 03](../lessons/03-getting-started.md)
- 기준: [RULES.md](../RULES.md). 최신 SDK를 사용하는 Client 단원의 개념·구현 근거를 묶는다.

## 개념별 최신 상태

| 개념 | 상태 | 답변 근거와 확인 방식 | 마지막 확인일 | 후속 확인 |
| --- | --- | --- | --- | --- |
| await와 순차 실행 | 이해 확인 | 두 await 호출의 코드에 첫 호출→first 저장→둘째 호출→second 저장→print 순서를 직접 표시했다. 요청·응답 수신의 내부 구분은 에이전트가 평가 시 보충했다. 직전 설명의 실행 순서 확인이며 독립 병렬 처리 설계의 증거는 아니다. | 2026-10-02 | 실제 Client 호출로 연결한다. 병렬 실행 구현은 평가하지 않았다. |
| async with의 연결 관리·asyncio.run | 미확인 | 연결 준비·정리와 event loop 실행을 설명했으나 독립 답변 근거는 없다. | 2026-10-02 | 연결 코드 수정·실행 시 필요한 범위에서 확인한다. |
| 실패 결과와 예외의 Client 처리 | 이해 확인 | get_weather 사례에서 except만 있는 코드는 성공 문구를 출력하며 result.is_error를 검사해야 한다고 설명했다. 직접 작성한 응용 메서드에 is_error 분기를 넣었고, 지적 후 Tool·Resource 두 요청을 하나의 try로 감싸도록 수정했다. 보완 후 코드 확인이며 예외 범위의 독립 적용으로 일반화하지 않는다. | 2026-10-04 | 새 사례의 독립 예외 처리와 종료 코드·기능 정확성 구분은 아직 평가하지 않았다. |

## 실습 근거

- 2026-10-04 최종 확인: 학습자가 run_custom_requests의 Tool 호출·is_error 분기·예상값 비교·Resource 읽기를 같은 try 블록으로 수정했다. 파일과 에이전트 재실행에서 True·Hello, Mina!를 확인했다. 기존 오류 실습의 is_error 분기와 MCPError catch를 함께 활용하여 기본 응용 과제를 완료했다. Resource exception 출력 문구는 공통 catch에서도 남아 있으며 실행 동작에는 영향이 없다. 실패 분기와 예외 처리 실습은 이전 제출 출력으로 확인했고 새 블록 범위는 코드로 확인했다.
- 2026-10-04: 직접 작성한 run_custom_requests에서 x=5,y=3,expected=8의 add 호출, is_error 분기, structured_content['result'] 비교, greeting://Mina 읽기를 확인했다. 제출 결과는 True와 정상 인사말이다. 입력·이름은 기존 예제와 같고 비교식 문법은 안내했으므로 새 사례의 독립 적용으로 일반화하지 않는다. MCPError 처리는 Resource 읽기만 감싸며 Tool 호출은 try 밖에 있어 과제의 예외 처리 범위가 남았다. 보완 전 전체 구현 완료로 판정하지 않는다.
- 2026-10-04: 학습자가 test_errors 안내를 실행하여 add의 a 누락을 Tool failure(content의 validation error), 미등록 unknown://Mina 읽기를 Resource exception(Unknown resource)과 code -32602로 출력했다. 결과 실패·MCPError의 두 처리 경로 실습을 확인했다. 오류 처리 개념의 독립 설명과 실제 종료 코드는 아직 확인하지 않았다.
- 2026-10-04: profile 템플릿 새 사례의 URI·메서드 선택을 확인했다. 최신 개념 평가는 [Tools, Resources, Prompts](tools-resources-prompts.md)의 Resource의 발견과 읽기에 둔다.
- 2026-10-04: 학습자가 일반 Resource count 0, greeting://{name} 템플릿 목록, greeting://Mina의 TextResourceContents(mime_type='text/plain', text='Hello, Mina!')를 제출했다. 안내에 따른 목록·템플릿 조회·읽기 실습을 확인했다. 이후 profile 새 사례에서 발견·읽기 구분을 확인했으며 최신 평가는 위 연결된 개념 기록에 둔다.
- 2026-10-02: 학습자가 안내에 따라 add(5,3)를 호출하고 content=[TextContent(text='8')], structured_content={'result':8}, is_error=False 출력을 제출했다. 실제 호출·결과 객체 속성 출력 경험을 확인했다. 결과 표현·오류 판단에 대한 독립 설명은 아직 받지 않았다.
- 2026-10-02: 학습자가 Client imports·sys.executable·파일 기준 서버 경로·async with Client 블록·메서드 type hint를 수정했다. 실제 파일을 확인했다. 제출 출력에서 Connected, Protocol: 2026-07-28, add: Add two numbers 목록을 확인했다. 정상 프롬프트로 돌아왔으며 안내한 Connection closed print는 코드에 없었다. 안내를 따른 연결·목록 조회 경험으로 기록하며 연결 관리 개념의 독립 이해를 판정하지 않는다.
