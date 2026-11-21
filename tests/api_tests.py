"""
Alias module for test_api.py to support naming requirement `tests/api_tests.py`.
"""

from tests.test_api import (
    test_get_users_list_success,
    test_get_single_user_content_and_structure,
    test_create_user_success,
    test_register_missing_password_error,
    test_get_non_existent_user_not_found,
)

__all__ = [
    "test_get_users_list_success",
    "test_get_single_user_content_and_structure",
    "test_create_user_success",
    "test_register_missing_password_error",
    "test_get_non_existent_user_not_found",
]
