#!/usr/bin/env python

import unittest
from subprocess import check_output, CalledProcessError

class TestScript(unittest.TestCase):
    def test_script_okay(self):
        input = check_output(['check_postfix_mailq.py', '--count-warning', '10', '--count-critical', '20'])
        self.assertEqual(input, b'OKAY: mailq count and size okay | count=7;10;20;; size=107800B;0;0;;\n')

    def test_script_sender_filter(self):
        input = check_output(['check_postfix_mailq.py', '--count-warning', '10', '--count-critical', '20', '--sender-filter', 'sender1@domain1.com'])
        self.assertEqual(input, b'OKAY: mailq count and size okay | count=2;10;20;; size=33217B;0;0;;\n')

if __name__ == '__main__':
    unittest.main()