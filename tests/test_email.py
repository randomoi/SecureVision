import unittest
from unittest.mock import patch
from app.email_notifications.password_reset_notifications import send_password_reset_email, send_change_of_password_confirmation_email
from app.database_models.models import User

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class TestResettingEmails(unittest.TestCase):
    def tearDown(self):
        patch.stopall()

    @patch('app.email_notifications.password_reset_notifications.compose_and_send_email')
    def est_send_password_change_email_confirmation(self, send_email_mock):
        user = User(email='test@some_example.com')
        send_change_of_password_confirmation_email(user)
        expected_subject = "Password Change Confirmation"
        
        self.assertEqual(send_email_mock.call_count, 1)
        self.assertEqual(send_email_mock.call_args[0][0], "Security System <sender.demo2020@gmail.com>")
        self.assertEqual(send_email_mock.call_args[0][1], user.email)
        self.assertEqual(send_email_mock.call_args[0][2], expected_subject)

    @patch('app.email_notifications.password_reset_notifications.compose_and_send_email')
    def test_send_password_reset_email(self, send_email_mock):
        user = User(email='test@some_example.com')
        reset_link = 'random_reset_link'
        reset_url = f"http://127.0.0.1:5003/reset_password/{reset_link}"

        send_password_reset_email(user, reset_link)

        expected_subject = "Password Reset"

        self.assertEqual(send_email_mock.call_count, 1)
        self.assertEqual(send_email_mock.call_args[0][0], "Security System <sender.demo2020@gmail.com>")
        self.assertEqual(send_email_mock.call_args[0][1], user.email)
        self.assertEqual(send_email_mock.call_args[0][2], expected_subject)


if __name__ == '__main__':
    unittest.main()

# References:
# https://docs.python.org/3/library/unittest.mock.html
# https://docs.python.org/3/library/unittest.mock-examples.html
# https://www.toptal.com/python/an-introduction-to-mocking-in-python
# https://datageeks.medium.com/python-unittest-a-guide-to-patching-mocking-and-magicmocks-40f2c0738981
# https://flask.palletsprojects.com/en/2.3.x/testing/
# https://pytest-flask.readthedocs.io/en/latest/
# https://circleci.com/blog/testing-flask-framework-with-pytest/
# https://pypi.org/project/pytest-flask/
# https://stackoverflow.com/questions/12187122/assert-a-function-method-was-not-called-using-mock
# https://realpython.com/python-mock-library/
# https://flask-restless.readthedocs.io/en/0.9.2/customizing.html
# https://stackoverflow.com/questions/29834693/unit-test-behavior-with-patch-flask
# https://stanford-code-the-change-guides.readthedocs.io/en/latest/guide_flask_unit_testing.html
# https://stackoverflow.com/questions/20242862/why-python-mock-patch-doesnt-work
# https://github.com/pydantic/pydantic/discussions/7741
# https://www.fugue.co/blog/2016-02-11-python-mocking-101
# https://fgimian.github.io/blog/2014/04/10/using-the-python-mock-library-to-fake-regular-functions-during-tests/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""