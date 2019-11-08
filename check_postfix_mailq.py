#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Icinga/Nagios plugin to check the postfix mailq
# For details see: $0 --help

import __future__
from sys import argv, exit
from os import linesep
from argparse import ArgumentParser
from re import compile, search, IGNORECASE
from collections import Counter
from subprocess import check_output, CalledProcessError

def default_re_email():
    return '[a-z0-9\.-]{1,64}|[a-z0-9\.-]{0,64}@[a-z0-9\.-]{2,254}'

def validate_email(input):
    pattern=compile('^(%s)$' % default_re_email(), IGNORECASE)
    if not pattern.match(input):
        print('UNKNOWN: Failed to validate sender filter, expecting "%s"' % default_re_email())
        exit(3)
    if input[0] == '@':
        input = '.*%s' % input
    return input

def validate_int(input):
    if int(input) < 0:
        print('UNKNOWN: Integer parameters must not be negative')
        exit(3)
    return int(input)

def check_mailq(input, sender_filter, perfdata_details, count_warning, count_critical, size_warning, size_critical, recipients_warning, recipients_critical):
    mailq_count = Counter()
    mailq_size = Counter()
    mailq_recipients = Counter()
    mailq_state_active = 0
    mailq_state_hold = 0
    mailq_state_deferred = 0
    current_sender = None

    re_sender = compile('^[0-9A-F]{10}([!\*]?)\s+([0-9]+)\s+.*\s+(%s)$' % sender_filter, IGNORECASE)
    re_recipient = compile('^\s+(%s)$' % default_re_email())

    for line in input.decode('utf-8').split('\n'):
        line = line.rstrip(linesep)
        if len(line) > 0:
            if line[0] in ['A', 'B', 'C', 'D', 'E', 'F', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                sender_match = search(re_sender, line)
                if sender_match:
                    current_sender = sender_match.group(3)
                    mailq_count[current_sender] += 1
                    mailq_size[current_sender] += int(sender_match.group(2))
                    if sender_match.group(1) == '!':
                        mailq_state_hold += 1
                    elif sender_match.group(1) == '*':
                        mailq_state_active += 1
                    else:
                        mailq_state_deferred += 1
            else:
                if search(re_recipient, line):
                    mailq_recipients[current_sender] += 1

    sum_mailq_count = sum(mailq_count.values())
    sum_mailq_size = sum(mailq_size.values())
    sum_mailq_recipients = sum(mailq_recipients.values())
    perfdata = ['count=%i;%i;%i;;' % (sum_mailq_count, count_warning, count_critical), 'active=%i;;;;' % mailq_state_active, 'hold=%i;;;;' % mailq_state_hold, 'deferred=%i;;;;' % mailq_state_deferred, 'size=%iB;%i;%i;;' % (sum_mailq_size, size_warning, size_critical), 'recipients=%i;%i;%i;;' % (sum_mailq_recipients, recipients_warning, recipients_critical)]
    if perfdata_details:
        for k, v in mailq_count.items():
            perfdata += ['count[%s]=%i' % (k, v)]
        for k, v in mailq_size.items():
            perfdata += ['size[%s]=%iB' % (k, v)]
        for k, v in mailq_recipients.items():
            perfdata += ['recipients[%s]=%i' % (k, v)]
    perfdata = ' '.join(sorted(perfdata))

    if sum_mailq_count >= count_critical:
        return 2, 'CRITICAL: mailq count >%i | %s' % (count_critical, perfdata)

    if sum_mailq_count >= count_warning:
        return 1, 'WARNING: mailq count >%i | %s' % (count_warning, perfdata)

    if recipients_critical >0 and sum_mailq_recipients >= recipients_critical:
        return 2, 'CRITICAL: recipient count in mailq for filtered sender >%i | %s' % (recipients_critical, perfdata)

    if recipients_warning >0 and sum_mailq_recipients >= recipients_warning:
        return 1, 'WARNING: recipient count in mailq for filtered sender >%i | %s' % (recipients_warning, perfdata)

    if size_critical > 0 and sum_mailq_size >= size_critical:
        return 2, 'CRITICAL: mailq size >%i | %s' % (size_critical, perfdata)

    if size_warning > 0 and sum_mailq_size >= size_critical:
        return 1, 'WARNING: mailq size >%i | %s' % (size_critical, perfdata)

    return 0, 'OKAY: mailq count and size okay | %s' % perfdata


if __name__ == '__main__':
    parser = ArgumentParser(description='Check postfix mailq nagios/icinga plugins')
    parser.add_argument('--sender-filter', type=validate_email, required=False, help='Check only mailq entries which given email address or domain, e.g. "noreply@example.com" or "@example.net')
    parser.add_argument('--count-warning', type=validate_int, required=True, help="Generate warning if mailq entries exceeds this threshold")
    parser.add_argument('--count-critical', type=validate_int, required=True, help="Generate critical if mailq entries exceeds this threshold")
    parser.add_argument('--size-warning', type=validate_int, default=0, required=False, help="Generate warning if size in bytes of mails in mailq exceeds this threshold")
    parser.add_argument('--size-critical', type=validate_int, default=0, required=False, help="Generate critical if size in bytes of mails in mailq exceeds this threshold")
    parser.add_argument('--recipients-warning', type=validate_int, default=0, required=False, help='Generate warning if sum of all recipients exceeds this threshold (recipients that belong to sender that match the defined filter; default is to match all senders)')
    parser.add_argument('--recipients-critical', type=validate_int, default=0, required=False, help='Generate critical if sum of all recipients exceeds this threshold (recipients that belong to sender that match the defined filter; default is to match all senders)')
    parser.add_argument('--perfdata-details', action='store_true', help='Print details about single sender addresses in perfdata')
    args = parser.parse_args(argv[1:])

    if args.count_warning >= args.count_critical:
        print('UNKNOWN: count warning must be greater than critical')
        exit(3)

    if args.size_warning > 0 and args.size_warning >= args.size_critical:
        print('UNKNOWN: size warning must be greater than critical')
        exit(3)

    if args.recipients_warning > 0 and args.recipients_warning >= args.recipients_critical:
        print('UNKNOWN: recipients warning must be greater than critical')
        exit(3)

    try:
        sender_filter = args.sender_filter if args.sender_filter else default_re_email()
        compile(sender_filter, IGNORECASE)
    except:
        print('UNKNOWN: Failed to compile regex to match mailq entries')
        exit(3)

    try:
        mailq = check_output(['mailq'])
    except CalledProcessError:
        # check_output already wrote to STDERR - just exit here
        exit(3)

    ret = check_mailq(mailq, sender_filter, args.perfdata_details,args.count_warning, args.count_critical, args.size_warning, args.size_critical, args.recipients_warning, args.recipients_critical)
    print(ret[1])
    exit(ret[0])