# 상품 견적 MCP 실습

[Practical Implementation](../README.md) 과제 2의 최소 Python MCP 서버다.
기능과 정책의 설계는 [DESIGN.md](./docs/DESIGN.md)를 참고한다.

제공 기능은 재고 조회 Tool `check_stock`, 정책 Resource `quote://policy`,
작업 지시 Prompt `prepare_quote`다. Prompt 조회는 메시지를 반환하는 단계이며,
전체 견적을 실행하지 않는다. `search_products`, `calculate_quote`, 자동 재시도와
배포는 후속 과제의 범위다.

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
