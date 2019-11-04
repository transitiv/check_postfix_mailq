#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Icinga/Nagios plugin to check the postfix mailq
# For details see: $0 --help

import __future__
import sys
from os import linesep
import argparse
import re
from subprocess import check_output, CalledProcessError

def default_re_email():
    return '[a-z0-9\.-]{1,64}|[a-z0-9\.-]{0,64}@[a-z0-9\.-]{2,254}'

def validate_email(input):
    pattern=re.compile('^(%s)$' % default_re_email(), re.IGNORECASE)
    if not pattern.match(input):
        print('UNKNOWN: Failed to validate sender filter, expecting "%s"' % default_re_email())
        sys.exit(3)
    if input[0] == '@':
        input = '.*%s' % input
    return input

def validate_int(input):
    if int(input) < 0:
        print('UNKNOWN: Integer parameters must not be negative')
        sys.exit(3)
    return int(input)

def check_mailq(input, sender_filter, perfdata_details, count_warning, count_critical, size_warning, size_critical):
    mailq_count = {}
    mailq_size = {}
    mailq_recipients = {}
    current_sender = None

    re_sender = re.compile('^[0-9A-F]{10}([!\*]?)\s+([0-9]+)\s+.*\s+(%s)$' % sender_filter, re.IGNORECASE)
    re_recipient = re.compile('^\s+(%s)$' % default_re_email())

    for line in input.decode('utf-8').split('\n'):
        sender_match = re.search(re_sender, line.rstrip(linesep))
        if sender_match:
            current_sender = sender_match.group(3)
            try:
                mailq_count[current_sender] += 1
            except KeyError:
                mailq_count[current_sender] = 1
            try:
                mailq_size[current_sender] += int(sender_match.group(2))
            except KeyError:
                mailq_size[current_sender] = int(sender_match.group(2))
        else:
            recipient_match = re.search(re_recipient, line.rstrip(linesep))
            if recipient_match:
                try:
                    mailq_recipients[current_sender] += 1
                except KeyError:
                    mailq_recipients[current_sender] = 1

    perfdata = ['count=%i;%i;%i;;' % (sum(mailq_count.values()), count_warning, count_critical), 'size=%iB;%i;%i;;' % (sum(mailq_size.values()), size_warning, size_critical)]
    if perfdata_details:
        for k, v in mailq_count.items():
            perfdata += ['count[%s]=%i' % (k, v)]
        for k, v in mailq_size.items():
            perfdata += ['size[%s]=%iB' % (k, v)]
        for k, v in mailq_recipients.items():
            perfdata += ['recipients[%s]=%i' % (k, v)]
    perfdata = ' '.join(sorted(perfdata))

    if sum(mailq_count.values()) >= count_critical:
        return 2, 'CRITICAL: mailq count >%i | %s' % (count_critical, perfdata)

    if sum(mailq_count.values()) >= count_warning:
        return 1, 'WARNING: mailq count >%i | %s' % (count_warning, perfdata)

    if size_critical > 0 and sum(mailq_size.values()) >= size_critical:
        return 2, 'CRITICAL: mailq size >%i | %s' % (size_critical, perfdata)

    if size_warning > 0 and sum(mailq_size.values()) >= size_critical:
        return 1, 'WARNING: mailq size >%i | %s' % (size_critical, perfdata)

    return 0, 'OKAY: mailq count and size okay | %s' % perfdata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check postfix mailq nagios/icinga plugins')
    parser.add_argument('--sender-filter', type=validate_email, required=False, help='Check only mailq entries which given email address or domain, e.g. "noreply@example.com" or "@example.net')
    parser.add_argument('--count-warning', type=validate_int, required=True, help="Generate warning if mailq entries exceeds this threshold")
    parser.add_argument('--count-critical', type=validate_int, required=True, help="Generate critical if mailq entries exceeds this threshold")
    parser.add_argument('--size-warning', type=validate_int, default=0, required=False, help="Generate warning if size in bytes of mails in mailq exceeds this threshold")
    parser.add_argument('--size-critical', type=validate_int, default=0, required=False, help="Generate critical if size in bytes of mails in mailq exceeds this threshold")
    parser.add_argument('--perfdata-details', action='store_true', help='Print details about single sender addresses in perfdata')
    args = parser.parse_args(sys.argv[1:])

    if args.count_warning >= args.count_critical:
        print('UNKNOWN: count warning must be greater than critical')
        sys.exit(3)

    if args.size_warning > 0 and args.size_warning >= args.size_critical:
        print('UNKNOWN: size warning must be greater than critical')
        sys.exit(3)

    try:
        sender_filter = args.sender_filter if args.sender_filter else default_re_email()
        re.compile(sender_filter, re.IGNORECASE)
    except:
        print('UNKNOWN: Failed to compile regex to match mailq entries')
        sys.exit(3)

    try:
        mailq = check_output(['mailq'])
    except CalledProcessError:
        # check_output already wrote to STDERR - just exit here
        sys.exit(3)

    ret = check_mailq(mailq, sender_filter, args.perfdata_details,args.count_warning, args.count_critical, args.size_warning, args.size_critical)
    print(ret[1])
    sys.exit(ret[0])