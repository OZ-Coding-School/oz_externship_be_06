#!/bin/bash
set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_BLUE=`tput setaf 4;`
COLOR_RED=`tput setaf 1;`
COLOR_NC=`tput sgr0;` # No Color

cd "$(dirname "$0")/../.."

echo "${COLOR_BLUE}=== CI 체크 사전 검사 ===${COLOR_NC}"
echo ""

# 1. isort 체크
echo "${COLOR_BLUE}1. isort 체크 중...${COLOR_NC}"
if poetry run isort . --check --diff; then
    echo "${COLOR_GREEN}✅ isort 통과${COLOR_NC}"
else
    echo "${COLOR_RED}❌ isort 실패 - 'poetry run isort .' 실행하여 수정하세요${COLOR_NC}"
    exit 1
fi
echo ""

# 2. black 체크
echo "${COLOR_BLUE}2. black 체크 중...${COLOR_NC}"
if poetry run black . --check; then
    echo "${COLOR_GREEN}✅ black 통과${COLOR_NC}"
else
    echo "${COLOR_RED}❌ black 실패 - 'poetry run black .' 실행하여 수정하세요${COLOR_NC}"
    exit 1
fi
echo ""

# 3. mypy 체크
echo "${COLOR_BLUE}3. mypy 체크 중...${COLOR_NC}"
if poetry run mypy .; then
    echo "${COLOR_GREEN}✅ mypy 통과${COLOR_NC}"
else
    echo "${COLOR_RED}❌ mypy 실패${COLOR_NC}"
    exit 1
fi
echo ""

echo "${COLOR_GREEN}=== 모든 CI 체크 통과! ===${COLOR_NC}"
echo "${COLOR_BLUE}참고: 테스트는 로컬 환경(Redis 등) 설정이 필요하므로 CI에서 확인하세요.${COLOR_NC}"
