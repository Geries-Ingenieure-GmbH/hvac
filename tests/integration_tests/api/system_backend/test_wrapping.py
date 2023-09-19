import logging
from unittest import TestCase

from tests.utils.hvac_integration_test_case import HvacIntegrationTestCase


class TestWrapping(HvacIntegrationTestCase, TestCase):
    TEST_AUTH_METHOD_TYPE = "approle"
    TEST_AUTH_METHOD_PATH = "test-approle"

    def setUp(self):
        super().setUp()
        self.client.sys.enable_auth_method(
            method_type=self.TEST_AUTH_METHOD_TYPE,
            path=self.TEST_AUTH_METHOD_PATH,
        )
        self.client.write(
            path=f"auth/{self.TEST_AUTH_METHOD_PATH}/role/testrole",
        )

    def tearDown(self):
        self.client.sys.disable_auth_method(path=self.TEST_AUTH_METHOD_PATH)
        return super().tearDown()

    def test_unwrap(self):
        result = self.client.write(
            path="auth/{path}/role/testrole/secret-id".format(
                path=self.TEST_AUTH_METHOD_PATH
            ),
            wrap_ttl="10s",
        )
        self.assertIn("token", result["wrap_info"])

        unwrap_response = self.client.sys.unwrap(result["wrap_info"]["token"])
        logging.debug("unwrap_response: %s" % unwrap_response)
        self.assertIn(member="secret_id_accessor", container=unwrap_response["data"])
        self.assertIn(member="secret_id", container=unwrap_response["data"])

    def test_unwrap_token_with_token_as_login(self):
        result = self.client.write(
            path="auth/{path}/role/testrole/secret-id".format(
                path=self.TEST_AUTH_METHOD_PATH
            ),
            wrap_ttl="10s",
        )
        self.assertIn("token", result["wrap_info"])
        old_token = self.client.token
        self.client.logout()
        unwrap_response = self.client.sys.unwrap(token=result["wrap_info"]["token"], use_token_to_authenticate=True)
        logging.debug("unwrap_response: %s" % unwrap_response)
        self.assertIn(member="secret_id_accessor", container=unwrap_response["data"])
        self.assertIn(member="secret_id", container=unwrap_response["data"])
        self.client.token = old_token
