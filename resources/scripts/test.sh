#!/bin/bash
set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_BLUE=`tput setaf 4;`
COLOR_NC=`tput sgr0;` # No Color

cd "$(dirname "$0")/../.."

export DJANGO_SETTINGS_MODULE="config.settings.local"
echo "${COLOR_BLUE}Starting mypy${COLOR_NC}"
poetry run dmypy run -- .
echo "OK"

TEST_TARGET=${1:-apps}
[[ "$TEST_TARGET" != apps* ]] && TEST_TARGET="apps/$TEST_TARGET"
COVERAGE_SOURCE=$(echo "$TEST_TARGET" | cut -d'/' -f1,2)

echo "${COLOR_BLUE}Starting Django Test with coverage${COLOR_NC}"
echo "- Coverage Source: $COVERAGE_SOURCE"
echo "- Test Target: $TEST_TARGET"
poetry run coverage run --source="$COVERAGE_SOURCE" manage.py test "$TEST_TARGET"
poetry run coverage report -m
poetry run coverage html

echo "${COLOR_GREEN}Successfully Run Mypy and Test for $TEST_TARGET!!"