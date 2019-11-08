#!/usr/bin/env python

import unittest
from subprocess import check_output
from check_postfix_mailq import check_mailq, default_re_email

class TestCheckMailq(unittest.TestCase):
    def test_default_re_email(self):
        self.assertEqual(default_re_email(), '[a-z0-9\.-]{1,64}|[a-z0-9\.-]{0,64}@[a-z0-9\.-]{2,254}')

    def test_check_mailq_count_okay(self):
        input = check_output(['cat', 'tests/mailq.test'])
        self.assertEqual(check_mailq(input, default_re_email(), False, 10, 20, 0, 0, 0, 0), (0, 'OKAY: mailq count and size okay | active=1;;;; count=7;10;20;; deferred=5;;;; hold=1;;;; recipients=10;0;0;; size=107800B;0;0;;'))

    def test_check_mailq_count_warning(self):
        input = check_output(['cat', 'tests/mailq.test'])
        self.assertEqual(check_mailq(input, default_re_email(), False, 5, 10, 0, 0, 0, 0), (1, 'WARNING: mailq count >5 | active=1;;;; count=7;5;10;; deferred=5;;;; hold=1;;;; recipients=10;0;0;; size=107800B;0;0;;'))

    def test_check_mailq_count_critical(self):
        input = check_output(['cat', 'tests/mailq.test'])
        self.assertEqual(check_mailq(input, default_re_email(), False, 1, 2, 0, 0, 0, 0), (2, 'CRITICAL: mailq count >2 | active=1;;;; count=7;1;2;; deferred=5;;;; hold=1;;;; recipients=10;0;0;; size=107800B;0;0;;'))

    def test_check_mailq_recipients_warning(self):
        input = check_output(['cat', 'tests/mailq.test'])
        self.assertEqual(check_mailq(input, default_re_email(), False, 10, 20, 0, 0, 10, 20), (1, 'WARNING: recipient count in mailq for filtered sender >10 | active=1;;;; count=7;10;20;; deferred=5;;;; hold=1;;;; recipients=10;10;20;; size=107800B;0;0;;'))

    def test_check_mailq_recipients_critical(self):
        input = check_output(['cat', 'tests/mailq.test'])
        self.assertEqual(check_mailq(input, default_re_email(), False, 10, 20, 0, 0, 1, 2), (2, 'CRITICAL: recipient count in mailq for filtered sender >2 | active=1;;;; count=7;10;20;; deferred=5;;;; hold=1;;;; recipients=10;1;2;; size=107800B;0;0;;'))

    def test_check_mailq_domain(self):
        input = check_output(['cat', 'tests/mailq.test'])
        self.assertEqual(check_mailq(input, 'sender1@domain1.com', False, 5, 10, 0, 0, 0, 0), (0, 'OKAY: mailq count and size okay | active=0;;;; count=2;5;10;; deferred=2;;;; hold=0;;;; recipients=10;0;0;; size=33217B;0;0;;'))

    def test_check_mailq_perfdata_details(self):
        input = check_output(['cat', 'tests/mailq.test'])
        self.maxDiff = 2048
        self.assertEqual(check_mailq(input, default_re_email(), True, 5, 10, 0, 0, 0, 0), (1, 'WARNING: mailq count >5 | active=1;;;; count=7;5;10;; count[MAILER-DAEMON]=1 count[sender1@domain1.com]=2 count[sender2@domain2.com]=1 count[sender3@domain2.com]=1 count[sender3@domain3.com]=1 count[sender4@domain4.com]=1 deferred=5;;;; hold=1;;;; recipients=10;0;0;; recipients[MAILER-DAEMON]=1 recipients[sender1@domain1.com]=4 recipients[sender2@domain2.com]=1 recipients[sender3@domain2.com]=1 recipients[sender3@domain3.com]=1 recipients[sender4@domain4.com]=2 size=107800B;0;0;; size[MAILER-DAEMON]=18636B size[sender1@domain1.com]=33217B size[sender2@domain2.com]=20786B size[sender3@domain2.com]=495B size[sender3@domain3.com]=34176B size[sender4@domain4.com]=490B'))

if __name__ == '__main__':
    unittest.main()