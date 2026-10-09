# 상품 견적 MCP 실습

[Practical Implementation](../README.md) 과제 2·3에서 구현한 Python MCP 서버다.
기능과 정책의 설계는 [DESIGN.md](./docs/DESIGN.md)를 참고한다.

제공 기능은 상품 검색 Tool `search_products`, 재고 조회 Tool `check_stock`,
견적 계산 Tool `calculate_quote`, 정책 Resource `quote://policy`,
작업 지시 Prompt `prepare_quote`다. Prompt 조회는 메시지를 반환하는 단계이며,
전체 견적을 실행하지 않는다. 자동 재시도와 배포는 후속 과제의 범위다.

## 구현 판단과 협업 범위

- Tool 입력은 선언된 제약을 SDK의 Pydantic 검증에 맡겨 함수 실행 전에 거절한다. 도구 본문에서 검증을 빠뜨리는 문제를 줄이기 위한 선택이다. Prompt 이름·인자는 middleware, 수량·예산 등의 문자열 값은 Prompt 함수에서 검사한다.
- 재고 부족은 확인된 조회 결과이고, 조회 실패는 재고를 확인하지 못한 상태다. 실패에는 `ToolError`를 발생시켜 MCP의 오류 표시로 전달한다. 실제 응답 형식과 최초 설계의 차이는 [DESIGN.md](./docs/DESIGN.md)의 과제 2 오류 계약에 정리했다.
- 정책 원본은 `app/policy.py` 한곳에서 관리한다. Resource가 이 원본으로 안내를 생성하며, `calculate_quote`도 같은 원본을 참조해 견적을 계산한다. 정책 변경이 일부 기능에만 반영되는 실수를 방지하기 위해서다.

학습자는 주제·사용자·검색 방식·후보 제시 방향을 승인하고, 작업 단위별로
구현을 검토했다. 테스트 목적과 분류·이름, 입력 오류 응답, middleware 적용과
문서 범위에 대해 질문하고 수정 방향을 결정했다. 에이전트는 코드·테스트·실행
안내를 작성하고 검증·수정을 수행했으며, 서브에이전트는 독립 리뷰를 담당했다.
이 분담은 대화에서 확인한 결정·검토·작성 활동을 기록한 것이다.

## 대표 요청과 기대 결과

| 요청 | 기대 결과 |
|---|---|
| `check_stock(product_id=1, quantity=1)` | 조회 성공. 재고 값과 `in_stock == (stock >= 1)` 확인 |
| 확인 재고가 S개일 때 수량 S+1 요청 | 조회 성공, `status: "ok"`, `in_stock: false` |
| `check_stock(product_id=1, quantity=0)` 또는 문자열 수량 | SDK 입력 검증 오류, `is_error: true`, 성공 데이터 없음 |
| 없는 상품 ID 조회 또는 모의 시간 초과 | `is_error: true`, 오류 텍스트에 `PRODUCT_NOT_FOUND` 또는 `UPSTREAM_TIMEOUT`, 성공 데이터 없음 |
| `quote://policy` 읽기 | `text/markdown`으로 v1 정책 제공 |
| `prepare_quote(category="smartphones", quantity="3", budget="2000.00")` | `keyword` 기본값을 적용한 user 메시지 하나 |
| Prompt 수량 `"3.0"` 또는 필수 인자 누락 | `-32602`와 수정할 인자 안내 |

실제 API의 재고는 조회 시점에 따라 달라진다. 시간 초과 등 반복 가능한
실패 시나리오는 모의 HTTP 응답으로 확인한다.

## 환경 준비

Python 3.12와 `uv`가 필요하다. 아래 명령은 PowerShell 기준이다.

```powershell
Set-Location 'C:\Users\chahoseong\mcp-for-beginners\04-PracticalImplementation\practice'
uv sync --locked --no-python-downloads --cache-dir .uv-cache
```

확인한 환경은 Python 3.12.10, MCP SDK 2.3.0, HTTPX 0.28.1, pytest 9.1.1이다.
의존성은 `uv.lock`으로 재현한다. 이후 명령도 이 작업 디렉토리에서 실행한다.

## 실행과 테스트

서버를 직접 실행하려면 다음 명령을 사용한다.

```powershell
.\.venv\Scripts\python.exe -m app
```

stdio 입력을 기다리는 상태가 정상이다. pytest와 Inspector는 서버를 직접 실행하므로
테스트 전에 별도 서버를 켜 둘 필요는 없다.

```powershell
# 외부 통신 없는 unit test
.\.venv\Scripts\python.exe -m pytest -q tests/unit/

# 실제 DummyJSON API 및 MCP stdio integration test
.\.venv\Scripts\python.exe -m pytest -q tests/integration/

# 전체 테스트
.\.venv\Scripts\python.exe -m pytest -q
```

| 선택할 범위 | 확인하는 경계 | 외부 API 필요 |
|---|---|---|
| `tests/unit/` | 우리 함수의 로직과 모의 HTTP 실패 처리 | 없음 |
| `tests/integration/test_dummyjson_api.py` | 우리 조회 코드 → DummyJSON | 있음 |
| `tests/integration/test_tools.py` | MCP Client → stdio 서버 → DummyJSON | 정상 조회·없는 상품 조회에 필요 |
| `tests/integration/test_resources.py`, `test_prompts.py` | MCP Client → stdio 서버 | 없음 |

실제 API 테스트는 네트워크 실패를 건너뛰지 않는다. 재고 숫자는 고정하지 않는다.
MCP 테스트의 서버 로그는 pytest 임시 디렉토리의 `server.stderr.log`에서 확인한다.

## VS Code Host에서 사용

VS Code에서 저장소 루트 `C:/Users/chahoseong/mcp-for-beginners`를 연다.
루트의 `.vscode/mcp.json`에 `product-quote-practice` 서버가 등록되어 있다.
VS Code가 기존 가상환경의 Python으로 서버를 실행하므로 별도로 서버를 켜지 않는다.

1. 명령 팔레트에서 `MCP: List Servers`를 실행하고 `product-quote-practice`를
   선택해 시작한다. 연결에 실패하면 같은 메뉴의 `Show Output`으로 로그를 확인한다.
2. 새 채팅에서 `Session Target`을 **Local**로 선택하고 Agent 모드를 사용한다.
   `Copilot` 대상도 컴퓨터에서 실행되지만, 여기서 필요한 **Local** 대상과는 다르다.
   `Configure Tools`에서 `search_products`, `check_stock`, `calculate_quote`를 활성화한다.
3. 작업을 전송하기 전에 `Add Context > MCP Resources`에서 `quote://policy`를
   첨부한다. 메뉴를 찾기 어려우면 명령 팔레트에서 `MCP: Browse Resources...`를
   실행하고, `견적 정책` (`quote://policy`) 항목의 종이클립 버튼으로 채팅에 첨부한다.
   항목 자체를 선택해 정책을 열어 보기만 한 상태와 채팅 문맥에 첨부한 상태를 구분한다.
4. 채팅 입력창에 `/mcp.`를 입력하고 상품 견적 서버의 `prepare_quote`를 선택한다.
   확인한 VS Code 1.141.0에서는 `/mcp.product-quote-practice.prepare_quote`로 표시된다.
   직접 입력해 전송하는 대신 자동 완성 항목을 선택해야 서버의 Prompt를 조회한다.
   화면 안내에 따라 `category`, `quantity`, `budget` 문자열을 입력한다.
   `keyword`를 생략하면 추가 검색 조건이 없다. 서버가 반환한 메시지로 작업을
   시작하며, Prompt 메시지나 정책을 직접 작성해 대체하지 않는다.

채팅에서 Prompt 선택·인자와 정책 Resource 첨부를 확인한 뒤 작업을 전송한다.
주요 Tool 호출과 최종 답변은 해당 채팅에서 확인한다.
UI의 정확한 명령 표기는 버전에 따라 달라질 수 있으므로 `/` 자동 완성 목록에서
서버와 Prompt 이름을 확인한다.
확인한 VS Code 1.141.0에서는 `Copilot` 대상의 Agent Host 세션에서 MCP Prompt
자동 완성이 제외된다. 모델의 Auto 선택과 별개로 `Session Target`을 확인한다.
Resource 첨부 지원도 채팅 세션 종류에 따라 달라진다.

## Inspector로 수동 확인

Inspector를 사용하려면 Node.js 22.19 이상이 필요하다. 확인한 Inspector 버전은
2.10.0이며, 의존성은 `inspector/package-lock.json`으로 재현한다.

```powershell
npm --prefix inspector ci --ignore-scripts --cache inspector/.npm-cache --no-audit --no-fund
$practiceDir = (Get-Location).Path
$practicePython = (Resolve-Path '.venv/Scripts/python.exe').Path
$inspectorLauncher = 'inspector/node_modules/@modelcontextprotocol/inspector/clients/launcher/build/index.js'
$env:MCP_STORAGE_DIR = Join-Path $practiceDir 'inspector/.state'
```

### CLI

Inspector 2.10.0은 서버 명령을 `--` 앞에, Inspector 옵션을 뒤에 둔다.

```powershell
# Tool 목록
node $inspectorLauncher --cli $practicePython -m app -- --method tools/list --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8

# 실제 재고 조회
node $inspectorLauncher --cli $practicePython -m app -- --method tools/call --tool-name check_stock --tool-args-json '{"product_id":1,"quantity":1}' --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8

# 잘못된 Tool 입력
node $inspectorLauncher --cli $practicePython -m app -- --method tools/call --tool-name check_stock --tool-args-json '{"product_id":1,"quantity":0}' --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8
$LASTEXITCODE

# Resource 목록과 정책 읽기
node $inspectorLauncher --cli $practicePython -m app -- --method resources/list --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8
node $inspectorLauncher --cli $practicePython -m app -- --method resources/read --uri quote://policy --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8

# 없는 Resource
node $inspectorLauncher --cli $practicePython -m app -- --method resources/read --uri quote://missing --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8
$LASTEXITCODE

# Prompt 목록과 메시지 조회: keyword 기본값 사용
node $inspectorLauncher --cli $practicePython -m app -- --method prompts/list --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8
node $inspectorLauncher --cli $practicePython -m app -- --method prompts/get --prompt-name prepare_quote --prompt-args 'category="smartphones"' 'quantity="3"' 'budget="2000.00"' --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8

# keyword 지정
node $inspectorLauncher --cli $practicePython -m app -- --method prompts/get --prompt-name prepare_quote --prompt-args 'category="smartphones"' 'quantity="3"' 'budget="2000.00"' 'keyword="Samsung"' --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8

# 잘못된 수량 문자열
node $inspectorLauncher --cli $practicePython -m app -- --method prompts/get --prompt-name prepare_quote --prompt-args 'category="smartphones"' 'quantity="3.0"' 'budget="2000.00"' --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8
$LASTEXITCODE

# 필수 budget 누락
node $inspectorLauncher --cli $practicePython -m app -- --method prompts/get --prompt-name prepare_quote --prompt-args 'category="smartphones"' 'quantity="3"' --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8
$LASTEXITCODE

# 없는 Prompt
node $inspectorLauncher --cli $practicePython -m app -- --method prompts/get --prompt-name missing_prompt --format json --cwd $practiceDir -e PYTHONIOENCODING=utf-8
$LASTEXITCODE
```

| 요청 결과 | Inspector 종료 코드 |
|---|---|
| 정상 결과 | `0` |
| Tool 오류 결과 (`isError: true`) | `5` |
| Resource·Prompt의 MCP 오류 | `1` |

Inspector의 오류 출력 `code: "error"`는 CLI 자체의 표시다.
MCP의 숫자 오류 코드는 SDK Client를 사용하는 integration test에서 확인한다.

**입력 검증 시 주의:** Inspector 2.10.0은 Tool의 숫자 문자열을 숫자로 바꿀 수 있다.
JavaScript의 `3.0`도 정수 표기로 전송된다. 원래 자료형의 거절은 pytest로 확인한다.
Prompt에는 위 예처럼 `'quantity="3.0"'`을 사용해 문자열을 그대로 전달한다.
안쪽 큰따옴표를 생략하면 CLI가 값을 숫자로 해석할 수 있다.

### GUI

```powershell
New-Item -ItemType Directory -Path 'inspector/.state' -Force | Out-Null
$env:MCP_STORAGE_DIR = Join-Path (Get-Location).Path 'inspector/.state'
npm --prefix inspector run inspector -- --web --catalog .state/mcp.json
```

출력된 URL을 열고 다음 값으로 서버를 등록한다.

| 설정 | 값 |
|---|---|
| 서버 이름 | `product-quote-practice` |
| Transport | `stdio` |
| Command | `C:/Users/chahoseong/mcp-for-beginners/04-PracticalImplementation/practice/.venv/Scripts/python.exe` |
| Arguments | `-m`, `app` 두 인자 |
| Working directory / cwd | `C:/Users/chahoseong/mcp-for-beginners/04-PracticalImplementation/practice` |
| Environment | `PYTHONIOENCODING=utf-8` |

연결 후 Tool 실행, Resource 읽기, Prompt 메시지 조회를 확인한다.
GUI 폼이 잘못된 입력이나 인자 생략을 막으면 위 CLI로 서버 오류를 확인한다.
검토를 마치면 연결을 해제하고 Inspector 터미널에서 `Ctrl+C`로 종료한다.

## 참고

- [기능·정책 설계](./docs/DESIGN.md)
- [Python SDK](https://py.sdk.modelcontextprotocol.io/)
- [DummyJSON 상품 API](https://dummyjson.com/docs/products)
- [Inspector CLI](https://github.com/modelcontextprotocol/inspector/blob/main/clients/cli/README.md)
