#!/usr/bin/env python
import sys
import glob
from util import run, log


TIMEOUT = 600
total = 0
failed = []

tests = sys.argv[1:]
if not tests:
    tests = set(glob.glob('test_*.py')) - set(['test_support.py'])
    tests = sorted(tests)

for filename in tests:
    total += 1
    if run([sys.executable, '-u', filename], TIMEOUT):
        failed.append(filename)


if failed:
    log('%s/%s tests failed:\n- %s', len(failed), total, '\n- '.join(failed))
    sys.exit(1)
else:
    log('%s tests passed', total)
