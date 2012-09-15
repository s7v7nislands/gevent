import sys
import os
import glob
from util import run


TIMEOUT = 120


version = '%s.%s.%s' % sys.version_info[:3]
if not os.path.exists(version):
    sys.exit('Directory %s not found in %s' % (version, os.getcwd()))


class ContainsAll(object):
    def __contains__(self, item):
        return True


import test.test_support
test.test_support.use_resources = ContainsAll()

os.environ['PYTHONPATH'] = os.getcwd() + ':' + os.environ.get('PYTHONPATH', '')
os.chdir(version)

total = 0
failed = []


tests = sys.argv[1:]
if not tests:
    tests = set(glob.glob('test_*.py')) - set(['test_support.py'])
    tests = sorted(tests)

for filename in tests:
    total += 1
    if run([sys.executable, '-u', '-m', 'monkey_test', filename], TIMEOUT):
        failed.append(filename)

    total += 1
    if run([sys.executable, '-u', '-m', 'monkey_test', '--Event', filename], TIMEOUT):
        failed.append(filename + '/Event')

os.system('rm -f @test_*_tmp')

if failed:
    sys.stderr.write('%s/%s tests failed: %s\n' % (len(failed), total, failed))
    sys.exit(1)
else:
    sys.stderr.write('%s tests passed\n' % total)
