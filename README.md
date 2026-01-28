## Makefile

이 프로젝트는 자주 사용하는 작업을 `make`로 실행할 수 있습니다.

```bash
make help # 이용 가능한 모든 명령어 확인 가능

# 명령어 이용 예시
make run # Django 개발 서버 실행
make dtest qna # 도커 컨테이너에서 qna 앱 테스트 실행
make logs django # Docker django service 로그만 확인
```

주요 타겟:

- Local 환경 커맨드
   - `make run` - Django 개발 서버 실행
   - `make format` - 코드 포맷팅 실행 (black + isort + mypy)
   - `make test [app_name]` - mypy 및 테스트를 커버리지와 함께 실행 [특정 앱 지정 가능]
   - `make makemigrations [app_name]` - 마이그레이션 생성 [특정 앱 지정 가능]
   - `make migrate [app_name]` - 마이그레이션 적용 [특정 앱 지정 가능]
   - `make shell` - Django 셸 실행
   - `make dbshell` - 데이터베이스 셸 실행
- Docker 환경 커맨드
   - `make dtest [app_name|path]` - 컨테이너에서 테스트 & 커버리지 실행 [특정 앱 | 폴더 지정 가능]
   - `make dmakemigrations [app_name]` - 컨테이너에서 마이그레이션 생성 [특정 앱 지정 가능]
   - `make dmigrate [app_name]` - 컨테이너에서 마이그레이션 적용 [특정 앱 지정 가능]
   - `make dshell` - 컨테이너에서 Django 셸 실행
   - `make ddbshell` - 컨테이너에서 데이터베이스 셸 실행
- Docker 관리
   - `make build [service_name]` - Docker 이미지 빌드 [특정 서비스 지정 가능]
   - `make up [service_name]` - Docker 서비스 시작 [특정 서비스 지정 가능]
   - `make down` - Docker 서비스 종료
   - `make restart` - Docker 서비스 재시작
   - `make logs [service_name]` - Docker 로그 확인 [특정 서비스 지정 가능]
   - `make ps` - Docker 서비스 목록 확인
- 기타 유틸리티
   - `make dmypy-reset` - dmypy 데몬 중지 및 캐시 삭제
   - `make push-f [branch_name]` - 강제 푸시 실행 [특정 브랜치 지정 가능]
   - `make fetch` - 원격(origin) 최신 내역 가져오기
   - `make sync-develop` - 원격 최신 내역 가져오기 + develop 브랜치로 이동 + pull develop 브랜치
   - `make rebase` - 로컬 develop 기준으로 리베이스

## Mock 응답 설정

개발 편의를 위해 환경변수로 mock 응답을 사용할 수 있습니다.

- 환경변수: `USE_EXAM_MOCK`
  - `true`  → mock 데이터 반환
  - `false` → DB 조회 결과 반환 (기본값)

로컬에서 사용 예시:

```bash
USE_EXAM_MOCK=true
```

테스트는 환경에 영향받지 않도록 `override_settings(USE_EXAM_MOCK=False)`로 고정되어 있습니다.
