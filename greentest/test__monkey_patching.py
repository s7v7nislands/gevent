import sys
import os
import glob
import subprocess
import time


def wait(popen, name, timeout=120):
    endtime = time.time() + timeout
    try:
        while True:
            if popen.poll() is not None:
                return popen.poll()
            time.sleep(0.5)
            if time.time() > endtime:
                break
    finally:
        if popen.poll() is None:
            sys.stderr.write('\nKilling %s (timed out)\n' % name)
            try:
                popen.kill()
            except OSError:
                pass
            sys.stderr.write('\n')
    return 'TIMEOUT'


def run(command):
    popen = subprocess.Popen(command)
    name = ' '.join(command)
    return wait(popen, name)


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


for test in tests:
    total += 1
    if run([sys.executable, '-u', '-m', 'monkey_test', test]):
        failed.append(test)

    if 'Event' in open(test).read():
        total += 1
        if run([sys.executable, '-u', '-m', 'monkey_test', '--Event', test]):
            failed.append(test + '/Event')

os.system('rm -f @test_*_tmp')


if failed:
    sys.stderr.write('%s/%s tests failed: %s\n' % (len(failed), total, failed))
    sys.exit(1)
else:
    sys.stderr.write('%s tests passed\n' % total)
