# 4일차 - User API 설계

`4일차 - User 사용자 요구사항 정의서`를 기반으로 설계한 User API 명세입니다.

## REQ-USER-001 회원가입

| 항목 | 내용 |
|---|---|
| 누가 | 가입하려는 사람 |
| CRUD | Create |
| HTTP | POST |
| Endpoint | `/api/v1/users/signup` |
| Request Body | email, password, name, department, gender, phone_number |
| Response | 201 Created + 생성된 회원 정보 |
| 인증필요 | X (누구나 접근 가능) |
| 비고 | 비밀번호는 해싱해서 저장, 이메일/휴대폰 중복 체크 필요 |

## REQ-USER-002 로그인

| 항목 | 내용 |
|---|---|
| 누가 | 회원가입이 된 사용자 |
| CRUD | Create (토큰 발급) |
| HTTP | POST |
| Endpoint | `/api/v1/auth/login` |
| Request Body | email, password |
| Response | Access Token(JSON), Refresh Token(httpOnly 쿠키) |
| 인증필요 | X (아직 토큰이 없는 사람이 토큰을 받으러 오는 행위이므로 인증 없이도 호출 가능) |
| 비고 | 로그인 성공 시 JWT 발급 (NFR-USER-001 참고)<br>- Access Token(30분 만료): 응답 body로 반환<br>- Refresh Token(7일 만료): httpOnly 쿠키로 전달<br>- JWT payload엔 user_id만 포함<br>- 이메일/비밀번호 불일치 시 401 Unauthorized 반환 |

## REQ-USER-003 로그아웃

| 항목 | 내용 |
|---|---|
| 누가 | 로그인 유저 |
| CRUD | Delete |
| HTTP | POST |
| Endpoint | `/api/v1/auth/logout` |
| Request Body | 없음 |
| Response | 성공 메시지 `{"message": "로그아웃 되었습니다."}`, 200 OK |
| 인증필요 | O |
| 비고 | 성공 시 서버는 refresh token 쿠키를 만료시킴(삭제). 클라이언트는 응답 성공 후 보유 중인 토큰을 폐기하고 로그인 페이지로 리다이렉트 |

## REQ-USER-004 회원 목록 조회

| 항목 | 내용 |
|---|---|
| 누가 | 관리자 권한 유저 |
| CRUD | Read |
| HTTP | GET |
| Endpoint | `/api/v1/users` |
| Query Parameter | search(이메일 또는 이름 검색어), department(부서 필터) |
| Response | 고유ID, 이메일, 이름, 부서(연구, 의료, 개발), 성별(M/F), 휴대폰 번호, 계정 활성화 여부 |
| 인증필요 | O |
| 비고 | 목록 조회 시 필터 드롭다운을 적용하여 부서별 조회 가능<br>목록 조회 시 검색 기능을 활용하여 검색할 수 있다<br>Admin 권한만 접근 가능, 그 외 role은 403 Forbidden 반환 |

## REQ-USER-005 회원 권한 변경

| 항목 | 내용 |
|---|---|
| 누가 | 관리자 권한 유저 |
| CRUD | Update |
| HTTP | PATCH |
| Endpoint | `/api/v1/users/{user_id}` |
| Path Parameter | user_id (권한을 변경할 대상 회원의 고유 ID) |
| Request Body | role (PENDING/STAFF/ADMIN 중 하나) |
| Response | 변경된 회원 정보(ID, Name, Role 등) 또는 성공 메시지 |
| 인증필요 | O |
| 비고 | role 값이 PENDING/STAFF/ADMIN 중 하나가 아니면 400 반환<br>Admin 권한만 접근 가능, 그 외 role은 403 Forbidden 반환 |

## REQ-USER-006 마이페이지 조회

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Read |
| HTTP | GET |
| Endpoint | `/api/v1/users/me` |
| Request Body | 없음 |
| Response | 조회 가능한 항목(이름, 이메일, 부서, 성별, 휴대폰번호, 권한) |
| 인증필요 | O |
| 비고 | 요청자가 누구인지는 JWT 토큰에서 추출 (URL에 별도 ID 불필요) |

## REQ-USER-007 회원 정보 수정

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Update |
| HTTP | PATCH |
| Endpoint | `/api/v1/users/me` |
| Request Body | 수정 가능한 항목(부서, 휴대폰 번호) |
| Response | 성공 메시지("수정되었습니다") + 200 OK |
| 인증필요 | O |
| 비고 | phone_number가 다른 회원이 이미 사용 중이면 409 Conflict 반환<br>department는 MEDICAL/DEV/RESEARCH 중 하나가 아니면 400 반환<br>부서, 휴대폰번호 둘 다 안 보내면 400 반환 |

## REQ-USER-008 비밀번호 변경

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Update |
| HTTP | PUT |
| Endpoint | `/api/v1/users/me/password` |
| Request Body | 기존 비밀번호, 새로운 비밀번호 |
| Response | 성공 메시지("비밀번호가 변경되었습니다") + 200 OK |
| 인증필요 | O |
| 비고 | 기존 비밀번호 불일치 시 401 반환<br>새 비밀번호도 가입 시 비밀번호 정책(대소문자+특수문자 포함, 8~20자) 동일 적용 |

## REQ-USER-009 회원 탈퇴

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Delete |
| HTTP | DELETE |
| Endpoint | `/api/v1/users/me` |
| Request Body | password (요구사항에는 없지만 보안을 위해 추가) |
| Response | 성공 메시지("회원탈퇴 되었습니다.") + 200 OK |
| 인증필요 | O |
| 비고 | 회원 탈퇴 시 users 테이블 레코드 즉시 삭제<br>업로드했던 xray_images는 삭제하지 않고 uploader_id만 null 처리 (ON DELETE SET NULL)<br>비밀번호 재확인 요구 (요구사항에는 없으나 보안상 추가) |

## 공통 비기능 요구사항

- **NFR-USER-002 (비밀번호 입력 보안)**: 프론트엔드 UI 요구사항(비밀번호 마스킹/토글) — 백엔드 API 설계 대상 아님
- **NFR-USER-003 (API 성능)**: 본 문서에 정의된 모든 User API는 응답시간 3초 이내를 목표로 한다
