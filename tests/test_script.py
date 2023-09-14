#!/usr/bin/env python

import unittest
import os
from subprocess import check_output, CalledProcessError

class TestScript(unittest.TestCase):
    def test_script_okay(self):
        input = check_output(['env', 'PATH=./tests:%s' % os.environ['PATH'], './check_postfix_mailq.py', '--count-warning', '10', '--count-critical', '20'])
        self.assertEqual(input, b'OK: 7 items in mail queue using 105.27KiB | active=1;;;; count=7;10;20;; deferred=5;;;; hold=1;;;; recipients=10;0;0;; size=107800B;0;0;;\n')

    def test_script_critical(self):
        with self.assertRaises(CalledProcessError) as error:
            check_output(['env', 'PATH=./tests:%s' % os.environ['PATH'], './check_postfix_mailq.py', '--count-warning', '1', '--count-critical', '2'])
        self.assertEqual(error.exception.returncode, 2)

    def test_script_sender_filter(self):
        input = check_output(['env', 'PATH=./tests:%s' % os.environ['PATH'], './check_postfix_mailq.py', '--count-warning', '10', '--count-critical', '20', '--sender-filter', 'sender1@domain1.com'])
        self.assertEqual(input, b'OK: 2 items in mail queue using 32.44KiB | active=0;;;; count=2;10;20;; deferred=2;;;; hold=0;;;; recipients=10;0;0;; size=33217B;0;0;;\n')

if __name__ == '__main__':
    unittest.main()
