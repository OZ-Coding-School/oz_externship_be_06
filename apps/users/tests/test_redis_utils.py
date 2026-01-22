from django.test import TestCase

from apps.users.utils.redis_utils import (
    delete_email_code,
    delete_email_token,
    get_email_by_token,
    get_email_code,
    save_email_code,
    save_email_token,
)


class EmailCodeRedisUtilsTest(TestCase):
    def test_save_and_get_email_code(self) -> None:
        email = "test@example.com"
        code = "ABC123"
        save_email_code(email, code)
        result = get_email_code(email)
        self.assertEqual(result, code)

    def test_get_email_code_not_exists(self) -> None:
        result = get_email_code("notexist@example.com")
        self.assertIsNone(result)

    def test_delete_email_code(self) -> None:
        email = "test@example.com"
        code = "ABC123"
        save_email_code(email, code)
        delete_email_code(email)
        result = get_email_code(email)
        self.assertIsNone(result)


class EmailTokenRedisUtilsTest(TestCase):
    def test_save_and_get_email_token(self) -> None:
        token = "test_token_12345"
        email = "test@example.com"
        save_email_token(token, email)
        result = get_email_by_token(token)
        self.assertEqual(result, email)

    def test_get_email_by_token_not_exists(self) -> None:
        result = get_email_by_token("notexist_token")
        self.assertIsNone(result)

    def test_delete_email_token(self) -> None:
        token = "test_token_12345"
        email = "test@example.com"
        save_email_token(token, email)
        delete_email_token(token)
        result = get_email_by_token(token)
        self.assertIsNone(result)
