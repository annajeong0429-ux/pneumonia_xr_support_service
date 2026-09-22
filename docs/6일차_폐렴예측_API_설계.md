# 6일차 - AI 폐렴 예측 API 설계

`6일차 - AI 폐렴 예측 사용자 요구사항 정의서`를 기반으로 설계한 AI 폐렴 예측 API 명세입니다.

## 공통 사항

- Base URL: `/api/v1`
- 인증: JWT 토큰 기반 (`Authorization: Bearer {token}`)
- 접근 권한: 모든 로그인 유저 (부서: 의료/개발/연구 무관), `PENDING`은 접근 불가(기존 공통 규칙)
- 사용 모델: `Step 1`에서 작성한 `worker/model.py`의 `predict_pneumonia()` (ConvNeXt-Tiny + DenseNet121 OR 앙상블, 서버 시작 시 메모리 고정 로드)

## REQ-PRED-001 AI 모델 활용 폐렴 예측

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 (의료인/개발팀/연구자, PENDING 제외) |
| CRUD | Create(신규 예측 시) 또는 Read(기존 결과 재사용 시) — 혼합 |
| HTTP | POST |
| Endpoint | `/api/v1/records/{record_id}/ai-analysis` |
| Path Parameter | record_id (진료기록 고유 ID) |
| Request Body | 없음 |
| Response | `{id, record_id, is_pneumonia, confidence, heatmap_url, ai_model, created_at}` |
| 인증필요 | O |
| 비고 | - X-ray 이미지는 진료기록 저장 시 업로드된 이미지를 그대로 사용 (`xray_images`에서 record_id로 조회)<br>- 같은 `ai_model`로 이미 저장된 예측 결과가 있으면 재추론 없이 기존 결과 반환(200 OK), 없으면 새로 추론 후 저장(201 Created)<br>- `heatmap_url`은 **선택사항**(nullable) — Grad-CAM 등 히트맵 생성은 이번 단계에서 구현하지 않고 `null`로 저장 가능 → Stage 3 DB 컬럼이 NOT NULL로 되어 있어 **nullable로 마이그레이션 필요**<br>- 에러: 진료기록에 X-ray 이미지 없으면 400, 진료기록 없으면 404, 미인증 401 |

## REQ-PRED-002 AI 모델 활용 폐렴 예측 결과 조회

| 항목 | 내용 |
|---|---|
| 누가 | 모든 로그인 유저 |
| CRUD | Read |
| HTTP | GET |
| Endpoint | `/api/v1/records/{record_id}/ai-analysis` |
| Path Parameter | record_id |
| Response | `[{id, is_pneumonia, confidence, heatmap_url, created_at, ai_model}, ...]` |
| 인증필요 | O |
| 비고 | 목록 확인 가능 필드: 고유ID, 폐렴여부, Confidence, Heatmap Image URL, 예측 수행일시, 사용한 모델<br>record_id가 존재하지 않으면 404 |

## 데이터 모델 관련 — Stage 3 DB 모델 수정 필요

`ai_analysis_results` 테이블에 두 가지 마이그레이션이 필요합니다.

1. **`confidence`**: 현재 `DECIMAL(precision=5, scale=2)`(소수점 2자리)인데, 실제 모델 예측값은 소수점 4자리까지 나옵니다 (예: `0.9986`). `DECIMAL(precision=5, scale=4)`로 변경 필요.
2. **`heatmap_url`**: 현재 `nullable=False`(NOT NULL)인데, 이번 요구사항에서 heatmap은 선택사항입니다. `nullable=True`로 변경 필요.

## 공통 비기능 요구사항

- **NFR-PRED-001 (AI 모델 평가 기준)**: Recall(민감도) ≥ 0.90~0.95(최소 0.90), Accuracy ≥ 0.80~0.90(보조 지표). 폐렴 환자를 정상으로 오진(FN)하는 것이 가장 위험하므로 Recall을 핵심 지표로 관리
- **NFR-PRED-002 (API 성능)**: 모든 API는 3초 이내에 응답. (Step 1 테스트 시 실측 0.78초로 여유 있음)
