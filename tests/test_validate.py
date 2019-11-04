#!/usr/bin/env python

import unittest
from check_postfix_mailq import validate_email, validate_int

class TestValidators(unittest.TestCase):
    def test_validate_int_negative(self):
        with self.assertRaises(SystemExit) as error:
            validate_int(-1)
        self.assertEqual(error.exception.code, 3)

    def test_validate_int_zero(self):
        self.assertEqual(validate_int(0), 0)

    def test_validate_int_positive(self):
        self.assertEqual(validate_int(1), 1)

    def test_validate_email_wrong_format(self):
        with self.assertRaises(SystemExit) as error:
            validate_email('invalid_email')
        self.assertEqual(error.exception.code, 3)

    def test_validate_email_local(self):
        self.assertEqual(validate_email('MAILER-DAEMON'), 'MAILER-DAEMON')

    def test_validate_email_domain(self):
        self.assertEqual(validate_email('@example.net'), '.*@example.net')

    def test_validate_email_complete(self):
        self.assertEqual(validate_email('user@example.net'), 'user@example.net')

if __name__ == '__main__':
    unittest.main()