# Module 04 — Practical Implementation 완료 요약

- 완료일: 2026-10-09. README 기본 깊이에 맞춘 과제1·2·3의 조정된 필수 범위를 완료했다. 완료는 협업 실습과 확인된 이해의 범위이며 모든 구현의 독립 작성/숙달 판정은 아니다.
- 원문: [Practical Implementation](../../04-PracticalImplementation/README.md). 과제/시험/제출 조건 교정과 당시 공식 자료는 [상세 이력](history/04-practical-implementation-2026-10-09.md)에 보존했다. 재개할 때 이력을 기본적으로 읽지 않는다.

## 학습 방식과 제출물

- 학습자 요청으로 이 모듈은 강의 대신 과제 제시·검토 방식으로 진행했다. Python을 사용하고 기존 VS Code Host/Client 활용을 허용했다. 새 Client 전체 작성·Azure 배포는 필수 조건이 아니다. 이후 모듈의 진행 방식은 새 계획에서 정한다.
- 실습: [practice](../../04-PracticalImplementation/practice/), [설계](../../04-PracticalImplementation/practice/docs/DESIGN.md), [실행 안내](../../04-PracticalImplementation/practice/README.md). Python3.12.10/MCP2.3.0/HTTPX0.28.1/pytest9.1.1을 사용했다.
- 기능: search_products, check_stock, calculate_quote; quote://policy; prepare_quote. 서버는 stdio, 실제 데이터는 DummyJSON API를 사용했다. SDK 입력 검증과 ToolError/isError 오류 계약, 정책 단일 원본, Decimal 단계별 반올림을 검토했다.

## 목표별 성과와 확인 범위

- 설계: 역할·입력 출처·상품 ID 연결·업무 부적합/실행 실패·부분 완료·정책 불일치 중단·조회/보장 구분을 설계 시험에서 확인했다. 책임 구분과 정책 불일치는 보충 후 집중 확인한 근거이며 처음부터 독립 설계한 능력으로 일반화하지 않는다.
- 구현/검사: 과제2 전체125개 및 과제3 전반 전체390개 pytest 통과를 검토자가 확인했다. 실제 API/stdio와 모의 외부 실패 검사를 포함하며 제출 코드·문서의 계약 일치를 검토했다. 테스트 개수 자체는 성취 기준이 아니다.
- Host 활용: VS Code1.141.0 Local/Agent에서 실제 Prompt 메시지와 정책 Resource를 문맥에 포함했다. 두 사례 모두 검색1→재고16→견적15. 수량3/예산2000에서 적합12·재고 부족1·초과3의 정렬 표/내역/시각/안내기간/예약 없음 안내를 확인했다. 예산0.01의 적합0·부족1·초과15는 관찰 요약으로 인정했고 마지막 안내는 후속 요청 보완이다. 변경 관련 Prompt45개 검사를 확인했다.
- 측정 개선: PAGE_SIZE10→20으로 같은16개 후보(ID121–136)의 목록/순서/count를 유지하고 검색 내부 HTTP 요청3→2를 실제 API로 재현했다. 별도 limit0 전체 원본과 대조했으며 관련 검색122개가 통과했다. 참조 조회는 비교 요청 수에서 제외했다. 시간 단축·모든 규모의 최적값은 검증하지 않았다.
- 신뢰성: 기존 timeout·입력/원본 검증·오류 분리·중간 페이지 실패 거부와 검사 근거를 인정한다. 자동 재시도와 별도 실패 서버/네 Host 사례는 선택 보강으로 정정했으며 미구현을 완료한 것으로 표시하지 않는다. 잠정 과제4·별도 MCP cursor/운영 계획을 미출제 필수 과제로 추가하지 않는다.

## 이어갈 한계와 협업 원칙

- 최신 개념 평가: [Architecture](../understanding/architecture.md), [Tools/Resources/Prompts](../understanding/tools-resources-prompts.md), [Testing & Debugging](../understanding/testing-and-debugging.md). 기록 정리나 모듈 완료를 이유로 이해 등급을 변경하지 않았다.
- 학습자는 실행 흐름 파악이 아니라 구현/테스트의 정확성을 검토하는 양이 어렵다고 명확히 했다. 구현 세부 숙달은 미평가이나 이를 흐름 이해 부족으로 판단하지 않는다. 요구·검증 기준/명명·테스트 분류 판단과 구현·반복 검사 위임을 구분한다.
- 협업 제출을 독립 코드 작성의 증거로 해석하지 않는다. Tool 원본 결과 전체 대조, 동률 정렬, Host의 부분 실패/정책 오류/제한적 재시도 준수, SDK HTTP 세션 구분은 독립 확인하지 않았다. 필요한 다음 주제에서 관련 부분만 재확인한다.
- 실행 가능한 검사는 검토자가 실행한다. 같은 결과를 다시 수동 실행/전사하거나 모든 코드와 테스트의 개인 승인 기록을 제출하도록 요구하지 않는다. 원문 밖 보강을 필수 과제로 자동 확장하지 않는다.

## 마무리와 다음 위치

- 학습 목표별 성과/한계를 정리해 Module04를 완료 처리했다. 추가 구현·배포·새 시험은 종료 조건으로 요구하지 않는다.
- 다음은 [Module05 Advanced Topics](../../05-AdvancedTopics/README.md)의 단원 구성 검토와 필요한 학습 범위 선택이다. 아직 Module05 수업 계획/실습은 시작하지 않았다. 중복·선택·버전 의존 내용을 검토한 뒤 범위와 진행 방식을 정한다.
- 기록 구조 변경(2026-10-09): 누적 요구·교정 경위를 history/로 보존하고 이 문서를 재개 요약으로 축약했다. 상대 링크를 이동 위치에 맞게 수정하고 부모 INDEX와 PROGRESS를 갱신했다. 평가 날짜/근거/기존 등급은 유지했다.
