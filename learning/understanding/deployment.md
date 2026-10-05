# Deployment — 최신 이해 기록

- 학습 근거: [Module 03](../lessons/03-getting-started.md)
- 기준: [RULES.md](../RULES.md). 배포 위치·패키징·실제 연결 검증의 최신 근거를 묶는다.

## 개념별 최신 상태

| 개념 | 상태 | 답변 근거와 확인 방식 | 마지막 확인일 | 후속 확인 |
| --- | --- | --- | --- | --- |
| 요구사항에 따른 배포 위치 선택 | 이해 확인 | 개인 문서 접근 사례에는 로컬 프로세스, 개발자 컴퓨터 종료 후 팀 공유 사례에는 클라우드를 선택했다. 이유를 묻는 집중 후속 질문에 사용자 컴퓨터 문서 접근과 지속 실행·원격 접속을 설명했다. 실행 위치 비교를 설명한 뒤 주어진 요구사항에 적용한 근거이다. 클라우드가 자동으로 무중단을 보장하지 않고 원격 접근도 허가 사용자로 제한할 수 있음을 평가 시 보충한다. | 2026-10-05 | 로컬 Docker·Render 배포 실행은 확인했다. 독립 운영 설계·고가용성 구현은 미평가이다. |
| Image와 Container | 이해 확인 | Image/Container·Dockerfile build/run을 설명하고 v1 생성·실제 호출을 수행했다. 호스트 코드 수정 후 기존 Container restart만 하는 사례에서 반영되지 않으며 COPY는 이미지 생성 시 실행돼 그 시점 파일을 복사한다고 설명했다. 질문에서 COPY를 판단 근거로 제시한 집중 확인이다. v2 build·교체 안내 후 실제 응답의 deployment-practice-v2 이름과 계산값2.5를 제출했다. | 2026-10-05 | 독립 전체 배포 설계·갱신 실패 진단은 미평가이다. |
| 원격 코드 갱신의 점검 경로 | 이해 확인 | 로컬에만 multiply가 발견되는 새 사례에서 GitHub에 갱신한 스크립트가 업로드됐는지 확인하고 Render 재배포를 제안했다. 점검 경로를 직접 제안했으며 build·배포 성공 로그 확인은 평가 피드백으로 보충한다. | 2026-10-05 | 실제 원격 갱신 실패 재현·복구와 독립 운영 진단은 미평가이다. |

## 실습 위치와 한계

- 2026-10-05: Docker Client/Engine29.8.0·Desktop4.92.0·desktop-linux·Server linux/amd64·OSType linux 출력을 제출했다. CLI에서 Linux Engine 연결을 확인했다. Azure 구독 없음이며 무료 계정/Consumption 무료량은 안내했지만 가입·원격 리소스 생성은 하지 않았다. Image build와 Container 실행은 아직 미실습이다.
- 2026-10-05 이미지 생성: Dockerfile·requirements·server HTTP 실행 블록 안내 후 mcp-deployment-practice:v1 목록(ID daa6ef05ab94·175MB)을 제출했다. 안내된 Image build의 결과이며 Container 실행·실제 MCP 호출·독립 개념 설명과 구분한다.
- 2026-10-05 Container 실행: 안내한 docker run 뒤 docker ps의 f9b32af99b31·image:v1·Up33초·127.0.0.1:8080→8000/tcp를 제출했다. 실행과 포트 publish 설정의 근거이며 실제 MCP 처리·로그 확인은 아직 미완료이다.
- 2026-10-05 실제 배포 검증: 시작 완료·Uvicorn0.0.0.0:8000 로그와 curl.exe의 호스트8080/mcp 정상 응답(HTTP200·isError:false·result2.5), 0 분모 응답(HTTP200·isError:true·ToolError 설명)을 제출했다. 안내된 Container 배포의 실제 HTTP 정상/실패 경로를 확인했으며 독립 포트 설계·배포 실패 진단 능력으로 일반화하지 않는다.
- 2026-10-05 갱신 검증: v2 build·v1 Container stop·별도 v2 Container run 안내 뒤 실제 응답의 serverInfo.name deployment-practice-v2·result2.5·isError:false를 제출했다. 새 Container 목록/ID는 미제출이다. Azure 확장 여부는 질문 후 결정 전이다.
- 2026-10-05 Render 배포: 대안 비교 후 Render 선택에 동의하고 GitHub 실습 저장소·Render HTTPS 주소를 제출했다. 에이전트가 https://mcp-deployment-practice.onrender.com/mcp의 tools/list HTTP200·add/divide 명세와 deployment-practice-v2를 확인했다. 학생의 원격 정상/실패 호출 출력은 아직 미제출이며 원격 도구 발견은 에이전트 확인과 구분한다.
- 2026-10-05 원격 호출 검증: 이후 학습자가 Render /mcp의 정상2.5·isError:false와 0 분모 오류·isError:true 응답을 제출했다. 두 응답은 HTTP200이며 서버 이름은 deployment-practice-v2이다. 안내된 원격 배포의 정상/오류 경로 실행을 확인했으며 독립 배포 실패 진단은 아직 미평가이다. 이후 가상 사례의 점검 경로 답변은 위 최신 상태에 반영했다.

- 2026-10-05 구조 정리: 누적 단계별 학습 기록은 lessons/history/03-deployment-2026-10-05.md에 보존했다. 이 파일은 최신 이해 상태와 안내 실행의 근거를 유지하며, 단원 핵심 완료와 정리 실행 미확인을 구분한다.
