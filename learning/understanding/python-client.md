# Python MCP Client — 최신 이해 기록

- 학습 근거: [Module 03](../lessons/03-getting-started.md)
- 기준: [RULES.md](../RULES.md). 최신 SDK를 사용하는 Client 단원의 개념·구현 근거를 묶는다.

## 개념별 최신 상태

| 개념 | 상태 | 답변 근거와 확인 방식 | 마지막 확인일 | 후속 확인 |
| --- | --- | --- | --- | --- |
| tool_call_id와 실행 결과의 연결 | 이해 확인 | 두 get_stock 호출에 stock=8·0 결과를 각각 연결하고 ID는 모델에서 받은 것을 사용한다고 답했다. 예시의 call_A/B 대신 id-1/2로 표현해 실제 ID 보존을 명확히 보충했다. ID만 바꿔 전달하는 후속 사례에서 P17/P18을 0·8로 이해하게 된다고 정확히 진단했다. ID 보충 후 집중 질문의 답변이며 독립 복수 호출 구현까지 평가하지 않는다. | 2026-10-04 | 여러 Tool 중 선택 실습으로 이어가며 복수 호출 구현은 별도 확인한다. |
| 모델용 Tool 정의와 입력 schema 보존 | 이해 확인 | required 누락 시 필수 파라미터 정보가 전달되지 않아 모델이 값을 생략할 수 있고 서버 호출은 실패한다고 설명했다. 설명 직후의 진단이다. 이후 안내한 변환에서 integer·required 보존 출력과 모델의 add/subtract 인자를 확인했다. 전체 독립 구현으로 일반화하지 않는다. | 2026-10-04 | 상세 schema 제약·호환성의 독립 처리는 미평가이다. |
| LLM의 Tool 선택·Client 실행·결과 전달 | 이해 확인 | get_stock 사례에서 모델의 요청만으로 조회가 되지 않으며 Application의 MCP 호출·결과 재전달로 최종 답변을 만든다고 설명했다. 흐름 안내 직후의 확인이다. 이후 add와 새 subtract의 선택·실행·최종 답변 출력을 제출해 정상 흐름 실습을 확인했다. 전체 코드·검증 요청은 안내했으며 독립 구현 또는 오류 경로 적용까지 평가하지 않는다. | 2026-10-04 | 실패 결과 재전달·추가 호출 반복의 실제 처리는 미평가이다. |
| await와 순차 실행 | 이해 확인 | 두 await 호출의 코드에 첫 호출→first 저장→둘째 호출→second 저장→print 순서를 직접 표시했다. 요청·응답 수신의 내부 구분은 에이전트가 평가 시 보충했다. 직전 설명의 실행 순서 확인이며 독립 병렬 처리 설계의 증거는 아니다. | 2026-10-02 | 실제 Client 호출로 연결한다. 병렬 실행 구현은 평가하지 않았다. |
| async with의 연결 관리·asyncio.run | 미확인 | 연결 준비·정리와 event loop 실행을 설명했으나 독립 답변 근거는 없다. | 2026-10-02 | 연결 코드 수정·실행 시 필요한 범위에서 확인한다. |
| 실패 결과와 예외의 Client 처리 | 이해 확인 | get_weather 사례에서 except만 있는 코드는 성공 문구를 출력하며 result.is_error를 검사해야 한다고 설명했다. 직접 작성한 응용 메서드에 is_error 분기를 넣었고, 지적 후 Tool·Resource 두 요청을 하나의 try로 감싸도록 수정했다. 보완 후 코드 확인이며 예외 범위의 독립 적용으로 일반화하지 않는다. | 2026-10-04 | 새 사례의 독립 예외 처리와 종료 코드·기능 정확성 구분은 아직 평가하지 않았다. |

## 실습 근거

- 2026-10-04 응용 과제 완료: 학습자가 추가한 subtract(a:int,b:int)->int의 등록·docstring·return a-b를 실제 파일로 확인했다. 두 Tool 등록 상태에서 안내한 두 요청을 따로 실행해 subtract(a=141,b=20) 결과121과 add(a=141,b=20) 결과161, 각각 is_error=False·최종 한국어 답변을 제출했다. 새 함수는 학습자가 선택·구현했고 입력·선택 로그 검증은 안내했다. 기본 과제 완료이며 독립 전체 Client 구현·LLM 오류 대응으로 일반화하지 않는다.
- 2026-10-04 LLM Client: 학습자가 안내한 add(20,2) 흐름에서 첫 모델 응답 tool_calls, MCP is_error=False·result=22, 두 번째 모델 응답 stop·최종 한국어 답변 22를 제출했다. 정상 경로의 명세 변환·모델 선택·MCP 실행·결과 재전달 실습을 확인했다. 코드는 단계별로 안내했으며 독립 구현 또는 실패·복수 호출 처리의 증거로 일반화하지 않는다.
- 2026-10-04 최종 확인: 학습자가 run_custom_requests의 Tool 호출·is_error 분기·예상값 비교·Resource 읽기를 같은 try 블록으로 수정했다. 파일과 에이전트 재실행에서 True·Hello, Mina!를 확인했다. 기존 오류 실습의 is_error 분기와 MCPError catch를 함께 활용하여 기본 응용 과제를 완료했다. Resource exception 출력 문구는 공통 catch에서도 남아 있으며 실행 동작에는 영향이 없다. 실패 분기와 예외 처리 실습은 이전 제출 출력으로 확인했고 새 블록 범위는 코드로 확인했다.
- 2026-10-04: 직접 작성한 run_custom_requests에서 x=5,y=3,expected=8의 add 호출, is_error 분기, structured_content['result'] 비교, greeting://Mina 읽기를 확인했다. 제출 결과는 True와 정상 인사말이다. 입력·이름은 기존 예제와 같고 비교식 문법은 안내했으므로 새 사례의 독립 적용으로 일반화하지 않는다. MCPError 처리는 Resource 읽기만 감싸며 Tool 호출은 try 밖에 있어 과제의 예외 처리 범위가 남았다. 보완 전 전체 구현 완료로 판정하지 않는다.
- 2026-10-04: 학습자가 test_errors 안내를 실행하여 add의 a 누락을 Tool failure(content의 validation error), 미등록 unknown://Mina 읽기를 Resource exception(Unknown resource)과 code -32602로 출력했다. 결과 실패·MCPError의 두 처리 경로 실습을 확인했다. 오류 처리 개념의 독립 설명과 실제 종료 코드는 아직 확인하지 않았다.
- 2026-10-04: profile 템플릿 새 사례의 URI·메서드 선택을 확인했다. 최신 개념 평가는 [Tools, Resources, Prompts](tools-resources-prompts.md)의 Resource의 발견과 읽기에 둔다.
- 2026-10-04: 학습자가 일반 Resource count 0, greeting://{name} 템플릿 목록, greeting://Mina의 TextResourceContents(mime_type='text/plain', text='Hello, Mina!')를 제출했다. 안내에 따른 목록·템플릿 조회·읽기 실습을 확인했다. 이후 profile 새 사례에서 발견·읽기 구분을 확인했으며 최신 평가는 위 연결된 개념 기록에 둔다.
- 2026-10-02: 학습자가 안내에 따라 add(5,3)를 호출하고 content=[TextContent(text='8')], structured_content={'result':8}, is_error=False 출력을 제출했다. 실제 호출·결과 객체 속성 출력 경험을 확인했다. 결과 표현·오류 판단에 대한 독립 설명은 아직 받지 않았다.
- 2026-10-02: 학습자가 Client imports·sys.executable·파일 기준 서버 경로·async with Client 블록·메서드 type hint를 수정했다. 실제 파일을 확인했다. 제출 출력에서 Connected, Protocol: 2026-07-28, add: Add two numbers 목록을 확인했다. 정상 프롬프트로 돌아왔으며 안내한 Connection closed print는 코드에 없었다. 안내를 따른 연결·목록 조회 경험으로 기록하며 연결 관리 개념의 독립 이해를 판정하지 않는다.
