> 2026-10-02 단원 완료 시 보존한 정리 전 기록이다. 아래의 대기·미확인·다음 행동은 당시 상태이며 최신 상태는 [모듈 요약](../03-getting-started.md)을 따른다.

# Module 03 — Getting Started 수업 요약

- 현재 원문: [첫 서버 README](../../../03-GettingStarted/01-first-server/README.md)
- 실습 위치: [practice/](../../../03-GettingStarted/01-first-server/practice/)
- 진행: 2026-10-02 서버 기능과 Client·Inspector의 흐름을 설명하고 README 화면을 소개했다. 학습자가 이해했다고 응답했으나 독립 설명·적용 근거는 아직 없다. 가상환경·SDK 준비는 학습자가 제출한 실행 출력으로 확인했다. 최소 서버와 stdio 설명으로 진행한다.
- 순서: 서버 전체 모습 → 개발 환경 → 최소 서버와 stdio → Tool·Resource 등록 → Inspector 검증 → 작은 응용 과제.
- 다음 행동: 학습자가 add의 Field required와 divide의 division by zero가 발생한 단계의 차이를 설명하면 평가한다. 오류 실행 결과는 받았으나 비교 질문은 미응답이다. 이후 단원 완료와 기록 구조를 점검한다.
- 실습 폴더는 시작 시 비어 있었다. 2026-10-02 제출 출력에서 sys.executable이 practice/.venv/Scripts/python.exe이고 FastMCP import OK가 표시되어 가상환경 사용·FastMCP import를 확인했다. 설치 명령 전체 로그나 서버 기능 실행은 확인하지 않았다.

## 원문 주의사항

- 일반적인 HTTP·포트 안내와 stdio 예제를 구분하여 설명한다.
- Python 예제의 구현 범위는 add Tool과 greeting Resource이다. Prompts는 앞부분의 구조 소개에 포함되며 Python 최종 예제에는 없다.
- 실제 설치·실행 단계에서 SDK·Inspector의 공식 안내를 확인한다. 버전 교정·원문 밖 보충은 명시한다.
- 2026-10-02 공식 SDK 문서 확인: 현재 main은 MCPServer를 사용하는 v2 안내이며 원문의 FastMCP는 v1.x 예제이다. 원문 실습에는 공식 v1.x 안내의 mcp[cli]<2를 사용한다. 로컬 python은 3.12.10, node는 24.13.1이며 py launcher는 Python을 찾지 못했다. 설치 안내는 python 명령을 사용한다.

## 관련 기록

- [Tools, Resources, Prompts](../../understanding/tools-resources-prompts.md): 기존 개념 평가와 확인 방식의 한계. 실제 구현 경험과 구분하며 새 답변 없이 상태를 올리지 않는다.

## 교수 맥락 보완

- 2026-10-02: Inspector 화면을 소개하기 전에 사용 행동을 질문했다. 학습자가 화면을 모른다고 지적하여 README 스크린샷으로 연결·목록 조회·입력·호출·결과 표시를 먼저 설명한다. 이전 미응답은 이해 부족의 근거로 삼지 않는다. 실제 조작은 설치 단계 이후 진행한다.

## 주요 확인

- 2026-10-02: 학습자가 divide(5,0)의 Error executing tool divide: division by zero를 제출했다. 오류 경로 실습을 확인했다. 함께 요청한 add 필수 인자 누락과의 단계 비교는 아직 답변되지 않아 개념 이해를 추가 확인으로 판정하지 않는다.
- 2026-10-02: 실제 server.py에서 divide의 decorator·int 입력·float 반환형·docstring·return a / b를 확인했다. 학습자가 안내한 세 입력의 계산값 1.5,-3,0을 보고하여 정상 입력 실습을 확인했다(원시 응답은 미제출). 별도의 0 분모 처리 코드는 없으며 Python의 실행 오류를 다음 단계에서 살펴본다.
- 2026-10-02: 학습자가 divide의 목적(두 수 나눗셈), 입력 a:int·b:int, 반환 float, 테스트 3/2→1.5를 제안했다. 예제와 다른 기능의 기본 명세 설계를 적용 확인으로 기록했다. 0으로 나누는 경우는 아직 가르치거나 평가하지 않았으며 구현 후 별도 확인한다.
- 2026-10-02: 학습자는 abc가 입력되지 않아 한글 ㅇ을 넣고 실행했다고 설명했다. 오류의 input_value에는 b만 있으므로 ㅇ의 자료형 검증 성공 사례가 아닌 a 누락 거부 사례로 해석한다. 입력칸 또는 요청 구성 과정에서 a가 제외된 정확한 경로는 미확인이며 추가 UI 내부 분석을 학습 진행 조건으로 삼지 않는다. 숫자 입력과 필수 입력 누락 확인을 마치고 응용 Tool 설계로 진행한다.
- 2026-10-02: 학습자는 다른 입력도 제대로 계산된다고 보고했다(개별 결과 미제출). 잘못된 입력 시 addArguments의 a에 Field required, type=missing, input_value={'b': 7}이 표시된 오류를 제출했다. 필수 인자 a 누락 검증은 확인했으나 abc 문자열이 서버에 전달되어 자료형 검증을 받은 증거는 아니다. UI에서 a가 누락된 경위는 미확인이다.
- 2026-10-02: 학습자가 greeting://Mina Resource 읽기 결과를 제출했다. contents에 해당 URI, mimeType text/plain, text Hello, Mina!가 있어 안내에 따른 템플릿 Resource 읽기를 확인했다. 독립 Resource 설계·구현까지 평가한 것은 아니다.
- 2026-10-02: 학습자가 Inspector의 Connected 상태와 add(7, 9)의 Tool Result {"result": 16}을 제출하여 첫 연결·Tool 호출 실습을 확인했다. 안내한 입력의 단일 성공 사례이며 다양한 입력·Resource 읽기는 아직 확인하지 않았다.
- 2026-10-02: server.py에서 add Tool과 greeting Resource 작성을 확인했고 SDK는 1.30.0이었다. List Tools는 목록·명세 조회이며 실행은 아니라는 답변을 확인했다. README 화면·명령 흐름에 맞추어 공식 Inspector의 v1-latest 태그를 명시하고 가상환경 Python으로 server.py를 실행하는 안내를 제공한다. 실제 연결·호출 결과는 대기 중이다.
- 2026-10-02: practice/server.py에서 최소 FastMCP 서버 코드를 확인했다. 학습자는 출력이 없는 상황을 표준 입력 대기 상태로 설명했다. 직전 설명과 가까운 사례의 이해 확인이며 실행 로그나 독립 오류 진단을 확인한 것은 아니다. Tool·Resource 등록 설명으로 진행한다.
- 관련 전송 기록: [Transports](../../understanding/transports.md).

