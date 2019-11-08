# check_postfix_mailq

## About

This nagios/icinga plugin collects information about the postfix mail queue by running the `mailq` command.
It runs different checks on the `mailq` output and provides detailed perfdata.

## Example

```bash
$ ./check_postfix_mailq.py --count-warning 5 --count-critical 10
WARNING: mailq count >5 | active=1;;;; count=7;5;10;; deferred=5;;;; hold=1;;;; recipients=10;0;0;; size=107800B;0;0;;

$ ./check_postfix_mailq.py --count-warning 5 --count-critical 10 --perfdata-details
WARNING: mailq count >5 | active=1;;;; count=7;5;10;; count[MAILER-DAEMON]=1 count[sender1@domain1.com]=2 count[sender2@domain2.com]=1 count[sender3@domain2.com]=1 count[sender3@domain3.com]=1 count[sender4@domain4.com]=1 deferred=5;;;; hold=1;;;; recipients=10;0;0;; recipients[MAILER-DAEMON]=1 recipients[sender1@domain1.com]=4 recipients[sender2@domain2.com]=1 recipients[sender3@domain2.com]=1 recipients[sender3@domain3.com]=1 recipients[sender4@domain4.com]=2 size=107800B;0;0;; size[MAILER-DAEMON]=18636B size[sender1@domain1.com]=33217B size[sender2@domain2.com]=20786B size[sender3@domain2.com]=495B size[sender3@domain3.com]=34176B size[sender4@domain4.com]=490B
```

## Requirements

* Standard modules of Python2 or Python3
* Permission to read postfix queues, see `authorized_mailq_users` of `postconf(5)`
* Command `mailq` can be found in `PATH` variable

## Why a new plugin

* Provide more details about the mail queue
* Should be runnable out of the box, don't depend on externals libraries
* Personal interest to get familiar with python unit tests

## Development and Testing

Run unit tests:

```bash
# Run in git directory of check_postfix_mailq
$ python2 -m unittest discover -s tests
$ python3 -m unittest discover -s tests
```

Run a short performance test (mailq output read from a local file):

```bash
# Run in git directory of check_postfix_mailq
$ export PATH=$PWD/tests/performance:$PATH
$ time ./check_postfix_mailq.py --count-warning 5 --count-critical 10 --perfdata-details
CRITICAL: mailq count >10 | count=4676;5;10;; count[MAILER-DAEMON]=668 count[sender1@domain1.com]=1336 count[sender2@domain2.com]=668 count[sender3@domain2.com]=668 count[sender3@domain3.com]=668 count[sender4@domain4.com]=668 recipients[MAILER-DAEMON]=668 recipients[sender1@domain1.com]=2672 recipients[sender2@domain2.com]=668 recipients[sender3@domain2.com]=668 recipients[sender3@domain3.com]=668 recipients[sender4@domain4.com]=1336 size=72010400B;0;0;; size[MAILER-DAEMON]=12448848B size[sender1@domain1.com]=22188956B size[sender2@domain2.com]=13885048B size[sender3@domain2.com]=330660B size[sender3@domain3.com]=22829568B size[sender4@domain4.com]=327320B

real    0m0.169s
user    0m0.148s
sys     0m0.012s
```

## Alternative monitoring solutions

* https://github.com/kumina/postfix_exporter
* https://github.com/google/mtail
