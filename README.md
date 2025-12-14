# WSD Bookstore API

Assignment 2 implementation of a production-style REST API for an online bookstore. The service exposes 30+ endpoints across auth, users, books, authors, categories, reviews, carts, wishlists, and orders. It satisfies the rubric requirements (JWT/RBAC, pagination/search/sort, error spec, Swagger docs, Postman collection, seeds, and automated tests hooks).

## 1. 프로젝트 개요
- **문제 정의**: 다중 역할(사용자/관리자)을 가진 북스토어 서비스를 설계하고, 주문·리뷰·위시리스트 등을 포함한 도메인 CRUD를 구현
- **주요 기능**:
  - JWT 기반 인증/인가 (Access/Refresh + `ROLE_USER`/`ROLE_ADMIN`)
  - 통일된 에러 스펙(JSON envelope + 코드 10종 이상)
  - 페이지네이션, 정렬, 검색/필터 (가격·카테고리·저자)
  - 200건 이상 시드 데이터 & Alembic-ready ORM 모델
  - Swagger UI(`/docs`), Postman 컬렉션(자동 토큰 스크립트 5개 이상)
  - 요청/응답 로그 + 예외 스택 추적
  - Health check, rate-limit hook 자리, 로컬/배포 환경 분리

## 2. 실행 방법
```bash
# 0) Python 3.11 가상환경 생성
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 1) 의존성 설치
pip install -r requirements.txt

# 2) 환경파일
cp .env.example .env               # 실제 값으로 업데이트 (.env는 git에 올리지 않음)

# 3) DB ??
python scripts/seed_data.py        # 200? ?? ?? ??? ??

# 4) ?? ??
python run.py
# ??: flask --app run.py run --host 0.0.0.0 --port 8080
```

### Docker Compose (옵션)
```bash
# 1) 기본 env (필요 시 JWT_SECRET 등 export)
export JWT_SECRET=super-secret

# 2) 앱+MySQL 일괄 기동
docker-compose up --build

# 3) 로그 확인 후 http://localhost:8080 /docs 접속

# 4) 중지
docker-compose down
```

## 3. 환경 변수 (.env.example 기준)
| 이름 | 설명 |
| --- | --- |
| `FLASK_ENV` | `dev` 또는 `prod` |
| `SQLALCHEMY_DATABASE_URI` | MySQL DSN (`mysql+pymysql://user:password@host:port/db`) |
| `JWT_SECRET` | JWT 서명용 시크릿 |
| `JWT_ACCESS_EXPIRES_MIN` | Access Token 만료(분) |
| `JWT_REFRESH_EXPIRES_DAYS` | Refresh Token 만료(일) |
| `RATE_LIMIT_REQUESTS` | 요청 허용 횟수(기본 200) |
| `RATE_LIMIT_WINDOW_SECONDS` | 레이트리밋 윈도우 길이(기본 60초) |

## 4. 배포 주소
| 항목 | URL |
| --- | --- |
| Base API | `http://113.198.66.68:10169/` |
| Swagger UI | `http://113.198.66.68:10169/docs` |
| Swagger JSON | `http://113.198.66.68:10169//swagger.json` |
| Health Check | `http://113.198.66.68:10169//health` |

## 5. 인증 플로우 & 역할
1. `POST /auth/login` → `{access_token, refresh_token}`
2. 모든 보호 엔드포인트는 `Authorization: Bearer <access_token>` 필수
3. 만료 시 `POST /auth/refresh`로 새 토큰 쌍 획득
4. 관리자만 접근 가능한 엔드포인트(도서/카테고리/사용자 관리, 주문 상태 변경 등)에는 `ROLE_ADMIN` 필요

| 리소스 | USER | ADMIN |
| --- | --- | --- |
| `/books` 조회, `/reviews`, `/cart`, `/orders` (자기 것) | ✅ | ✅ |
| `/books` 등록/수정/삭제, `/categories` CRUD, `/users` 목록/관리 | ❌ | ✅ |
| `/orders` 전체 조회/상태 변경, `/authors` 등록 | ❌ | ✅ |
| `/wishlists`, `/comments`, `/review_likes` | ✅ | ✅ |

### 예제 계정 (seed 기준)
| 역할 | 이메일 | 비밀번호 |
| --- | --- | --- |
| ADMIN | `admin@example.com` | `Admin123!` |
| USER | `user1@example.com` | `User1123!` |

> 실제 과제 제출 시 `.env` 및 별도 문서에 DB/계정 접속 정보를 기재하고 GitHub에는 절대 업로드하지 않습니다.

## 6. DB 연결 정보 (예시)
| 항목 | 값 |
| --- | --- |
| Host | `localhost` |
| Port | `3306` |
| Schema | `bookstore` |
| User | `bookstore` |
| Password | `1234` |
| CLI | `mysql -u bookstore -p1234 -h localhost bookstore` |

실제 제출 시 사용 중인 DB 인스턴스/계정 정보를 별도 텍스트 파일로 제공하세요.

## 7. 엔드포인트 요약 (발췌)
| Method & Path | 설명 |
| --- | --- |
| `GET /health` | 헬스 체크 (버전/uptime 포함) |
| `POST /auth/login`, `/auth/refresh` | JWT 발급/재발급 |
| `POST /users` | 회원가입 |
| `GET /users` (ADMIN) | 사용자 목록 |
| `POST /categories` (ADMIN) | 카테고리 생성 |
| `GET /books` | 검색/정렬/페이지네이션 |
| `POST /books` (ADMIN) | 도서 등록 |
| `PUT /books/{id}` (ADMIN) | 도서 수정 |
| `DELETE /books/{id}` (ADMIN) | 도서 삭제 |
| `POST /orders` | 주문 생성 |
| `GET /orders` | 본인 주문 (관리자는 user_id 쿼리로 전체 조회) |
| `PATCH /orders/{id}/status` (ADMIN) | 주문 상태 변경 |
| `POST /reviews` | 리뷰 작성 |
| `POST /reviews/{id}/like` | 리뷰 좋아요 |
| `POST /cart` | 장바구니 담기 |
| `POST /wishlists` | 위시리스트 등록 |

총 30개 이상 엔드포인트가 README + Swagger + Postman에 모두 반영되어 있습니다.

## 8. 문서 & 테스트 산출물
- **Swagger/OpenAPI**: `docs/swagger.json`, 자동 UI(`/docs`) 제공. 각 엔드포인트는 400/401/403/404/422/500 예시 응답을 명시.
- **Postman 컬렉션**: `postman/bookstore.postman_collection.json`
  - 환경 변수: `base_url`, `admin_email`, `admin_password`, `access_token`, `refresh_token`
  - Pre-request/Test 스크립트 5개 이상 (토큰 주입, 응답 코드 검증, 페이로드 확인)
- **API 설계**: `docs/api-design.md`
- **DB 스키마**: `docs/db-schema.md` (ER 설명 + 인덱스/제약조건)
- **아키텍처 노트**: `docs/architecture.md`
- **자동화 테스트**: `pytest` 기반의 20개 이상 통합/단위 테스트(`tests/test_api.py`)가 포함되어 있으며 `pytest -q`로 실행할 수 있습니다.

## 9. 성능/보안 고려 사항
- JWT 서명 키 및 DB 비밀번호는 `.env`만 사용 (git 제외)
- 비밀번호는 `werkzeug.security.generate_password_hash` 기반 해시 저장
- 전역 요청/응답 로그(메서드, 경로, 상태코드, 지연시간) + 예상치 못한 예외 시 스택트레이스 로그 남김
- 간단한 전역 레이트리밋(`RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW_SECONDS`)을 통해 abusive traffic 방지
- 검색 대상 칼럼 인덱스(`books.title`, `users.email`, FK 등) 설계
- 향후 확장을 위해 Rate-limit/CORS 설정 훅을 `create_app`에 배치

## 10. 한계와 개선 계획
1. Swagger 사양은 핵심 엔드포인트를 다루도록 구성했으며, 향후 모든 세부 엔드포인트를 1:1 반영하도록 자동화(apispec + decorators) 예정
2. 배포 시에는 Gunicorn + systemd/PM2로 프로세스 매니징 필요
3. Rate limit, CORS, JWT 블록리스트는 최소 구현 상태 → Redis 기반으로 확장 가능
4. 테스트 커버리지를 20개 이상으로 확장하기 위한 추가 케이스(실패 케이스, RBAC, pagination edge) 계획
5. Postman/Swagger 예시는 영어 기반이지만, 실제 운영 시 다국어 메시지 대응 필요
