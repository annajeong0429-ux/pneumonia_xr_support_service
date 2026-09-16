# 5일차 - 환자 관리 및 진료기록 API 설계

`5일차 - 진료기록 사용자 요구사항 정의서`를 기반으로 설계한 환자(Patient)/진료기록(MedicalRecord) API 명세입니다.

## 공통 인증/인가 규칙

- **로그인 필요**: 아래 모든 API는 로그인(JWT 인증) 필요
- **PENDING 접근 금지**: role이 `PENDING`인 유저는 마이페이지 외 모든 서비스 접근 불가 (기존 규칙) → 아래 모든 API는 role이 `STAFF` 또는 `ADMIN`이어야 함
- **등록(Create) API 전용 제한**: 환자 등록(PTNT-001), 진료기록 등록(MDR-001)은 `department`가 `MEDICAL`인 유저만 가능
- 구현 시 `require_staff_or_admin`(role 체크), `require_medical_staff`(department=MEDICAL 체크) 의존성 함수를 새로 만들어 재사용

## REQ-PTNT-001 환자 정보 등록

| 항목 | 내용 |
|---|---|
| 누가 | department가 MEDICAL인 로그인 유저 |
| CRUD | Create |
| HTTP | POST |
| Endpoint | `/api/v1/patients` |
| Request Body | name, age, gender, phone |
| Response | 201 Created + 생성된 환자 정보(id, name, age, gender, phone, created_at) |
| 인증필요 | O (department=MEDICAL 전용) |
| 비고 | gender는 이 API에서는 필수 입력(DB 컬럼 자체는 nullable이지만 API 레벨에서 필수로 검증)<br>role이 PENDING이면 403, department가 MEDICAL이 아니면 403 |

## REQ-PTNT-002 환자 목록 조회

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저(department 무관, PENDING 제외) |
| CRUD | Read |
| HTTP | GET |
| Endpoint | `/api/v1/patients` |
| Query Parameter | name(이름 검색), gender(필터), min_age, max_age(나이 범위 필터) |
| Response | 환자 고유ID, 이름, 나이, 성별, 연락처, 생성일시, 수정일시 |
| 인증필요 | O |
| 비고 | min_age/max_age 둘 다 없으면 전체 나이 대상, 하나만 있어도 그 기준으로만 필터링 |

## REQ-PTNT-003 환자 정보 상세 조회

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Read |
| HTTP | GET |
| Endpoint | `/api/v1/patients/{patient_id}` |
| Path Parameter | patient_id |
| Response | 이름, 성별, 연락처, 나이 |
| 인증필요 | O |
| 비고 | 존재하지 않는 patient_id면 404 |

## REQ-PTNT-004 환자 정보 수정

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Update |
| HTTP | PATCH |
| Endpoint | `/api/v1/patients/{patient_id}` |
| Path Parameter | patient_id |
| Request Body | name, phone (둘 다 선택적, 수정 가능한 항목은 이름/연락처뿐) |
| Response | 성공 메시지("수정되었습니다") + 200 OK |
| 인증필요 | O |
| 비고 | 대상 없으면 404, name/phone 둘 다 안 보내면 400 |

## REQ-PTNT-005 환자 정보 삭제

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Delete |
| HTTP | DELETE |
| Endpoint | `/api/v1/patients/{patient_id}` |
| Path Parameter | patient_id |
| Response | 성공 메시지("환자 정보가 삭제되었습니다") + 200 OK |
| 인증필요 | O |
| 비고 | 대상 없으면 404<br>DB FK가 `medical_records.patient_id`, `xray_images.record_id` 둘 다 `ON DELETE CASCADE`로 설계되어 있어, 환자 삭제 시 관련 진료기록·X-ray 이미지가 DB 레벨에서 자동 연쇄 삭제됨 (별도 코드 불필요) |

## REQ-MDR-001 진료기록 등록

| 항목 | 내용 |
|---|---|
| 누가 | department가 MEDICAL인 로그인 유저 |
| CRUD | Create |
| HTTP | POST |
| Endpoint | `/api/v1/medical-records` |
| Request (multipart/form-data) | patient_id, chart_number, symptoms (텍스트 필드) + xray_image (파일) |
| Response | 201 Created + 생성된 진료기록 정보(id, chart_number, symptoms, created_at) + 등록된 X-ray 이미지 URL |
| 인증필요 | O (department=MEDICAL 전용) |
| 비고 | patient_id가 존재하지 않으면 404<br>chart_number 중복이면 409 (DB unique 제약)<br>X-ray 파일은 서버 `media/` 폴더에 저장 후 URL을 xray_images.image_url에 기록<br>xray_images.uploader_id는 요청자(current_user)로 자동 설정<br>xray_images.shooting_datetime은 업로드 시각으로 자동 기록 (요구사항에 별도 입력 필드 없음) |

## REQ-MDR-002 진료기록 목록 조회

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Read |
| HTTP | GET |
| Endpoint | `/api/v1/patients/{patient_id}/medical-records` |
| Path Parameter | patient_id |
| Response | 진료기록 ID, 진료차트넘버, 증상(100자 초과 시 뒷부분 생략하고 "..." 표시), 생성일시 |
| 인증필요 | O |
| 비고 | 원본 문서엔 "비기능"으로 분류되어 있으나 실제로는 조회 기능이라 기능 요구사항으로 설계함 (문서상 분류 오기로 보임)<br>patient_id가 존재하지 않으면 404 |

## REQ-MDR-003 진료기록 상세 조회

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Read |
| HTTP | GET |
| Endpoint | `/api/v1/medical-records/{record_id}` |
| Path Parameter | record_id |
| Response | 진료기록ID, 차트넘버, 증상(전체), 흉부 X-Ray 이미지 URL, 생성일시 |
| 인증필요 | O |
| 비고 | 존재하지 않으면 404<br>X-ray 이미지는 xray_images 테이블에서 record_id로 조회하여 image_url 포함 |

## 공통 비기능 요구사항

- **NFR-PTNT-001 / NFR-MDR-001 (API 성능)**: 본 문서에 정의된 모든 환자/진료기록 API는 응답시간 3초 이내를 목표로 한다
