## Makefile

이 프로젝트는 자주 사용하는 작업을 `make`로 실행할 수 있습니다.

```bash
make help # 이용 가능한 모든 명령어 확인 가능

# 명령어 이용 예시
make run # Django 개발 서버 실행
```

주요 타겟:

- `make format` - 코드 포맷팅 실행 (black + isort + mypy)
- `make test` - mypy 및 테스트를 커버리지와 함께 실행
- `make run` - Django 개발 서버 실행
- `make makemigrations` - 마이그레이션 생성
- `make makemigrations APP=app_name` - 마이그레이션 생성 (선택적으로 앱 지정)
- `make migrate` - 마이그레이션 적용
- `make migrate APP=app_name` - 마이그레이션 적용 (선택적으로 앱 지정)
- `make shell` - Django 셸 실행
- `make dbshell` - 데이터베이스 셸 실행
- `make build` - Docker 이미지 빌드
- `make up` - Docker 서비스 시작
- `make down` - Docker 서비스 종료
- `make restart` - Docker 서비스 재시작
- `make logs` - Docker 로그 확인
- `make ps` - Docker 서비스 목록 확인
- `make dtest` - Docker 컨테이너에서 테스트 실행
- `make dmypy-reset` - dmypy 데몬 중지 및 캐시 삭제
- `make push-force` - 안전한 강제 푸시 실행
- `make fetch` - 원격(origin) 최신 내역 가져오기
- `make rebase-develop` - origin/develop 기준으로 리베이스
