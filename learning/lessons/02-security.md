# Module 02 — Security 수업 요약

- 원문: [02-Security/README.md](../../02-Security/README.md)
- 진행: 2026-10-02 README 개념 학습 완료. 인증·인가·토큰·최소 권한, AI 공격·방어, Confused Deputy·상태 탈취, 공급망·운영 방어·보안 도구 개요를 다뤘다.
- 범위 결정: 실제 보안 제품 설정·Azure 배포·Sherpa 워크숍은 학습자 요청으로 생략했다. 당시 설치/실행 부재와 이후 Module 03의 Simple Auth 안내 실습을 구분한다. 모듈 완료를 모든 개념의 독립 적용·운영 능력 확인으로 해석하지 않는다.
- 재개 시: 개념별 최신 상태·보충 후 확인 한계는 [Security Index](../understanding/security/INDEX.md)에서 해당 주제를 선택한다. 감사 상세 절차는 가르친 뒤 확인하고 전체 복습을 다음 모듈의 선행 조건으로 강제하지 않는다.

## 원문 주의사항

- 2026-07-28과 구형 세션/DCR 설명이 혼재한다. 프로토콜 절차와 애플리케이션 상태를 구분한다.
- 제품 역할 소개를 공격 차단 보장으로 표현하지 않는다. 사용자 계정 MFA와 비대화형 workload identity를 구분한다.
- 구체적인 MUST·OAuth 흐름·제품 기능은 실제 해당 주제를 다룰 때 공식 근거를 확인한다. Module 01 예시와 원문·보충을 구분한다.

## 필요한 기록

- [Security Index](../understanding/security/INDEX.md): 인증·접근 통제, AI 공격, 공급망·운영 선택
- [Tools, Resources, Prompts](../understanding/tools-resources-prompts.md): 실행 도구 설계·증거와 연결할 때
- [평가 이력](history/02-security-assessments-2026-10-02.md), [완료·범위 결정 이력](history/02-security-completion-2026-10-02.md): 과거 평가·교정·생략 결정의 근거가 필요할 때만 읽는다.

## 구조 변경

- 2026-10-02 보안 기록을 주제별로 분리했다. 2026-10-06 완료/범위 결정의 상세는 history로 옮기고 재개 요약의 중복을 줄였다. 평가를 변경하지 않았다.
