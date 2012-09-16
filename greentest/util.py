import sys
import os
import subprocess
import time
import traceback


def log(message, *args):
    try:
        string = message % args
    except Exception:
        traceback.print_exc()
        try:
            message = '%r %% %r\n\n' % (message, args)
        except Exception:
            pass
        try:
            sys.stderr.write(message)
        except Exception:
            traceback.print_exc()
    else:
        sys.stderr.write(string + '\n')


def killpg(pid):
    if not hasattr(os, 'killpg'):
        return
    try:
        return os.killpg(pid, 9)
    except OSError, ex:
        if ex.errno != 3:
            log('killpg(%r, 9) failed: %s: %s', pid, type(ex).__name__, ex)
    except Exception, ex:
        log('killpg(%r, 9) failed: %s: %s', pid, type(ex).__name__, ex)


def kill_processtree(pid):
    ignore_msg = 'ERROR: The process "%s" not found.' % pid
    err = subprocess.Popen('taskkill /F /PID %s /T' % pid, stderr=subprocess.PIPE).communicate()[1]
    if err and err.strip() not in [ignore_msg, '']:
        log('%r', err)


def kill(popen):
    try:
        if popen.setpgrp_enabled:
            killpg(popen.pid)
        elif sys.platform.startswith('win'):
            kill_processtree(popen.pid)
    finally:
        try:
            popen.kill()
        except StandardError:
            # AttributeError can happen there: on Python 2.5, there's no kill() method
            try:
                os.kill(popen.pid, 9)
            except EnvironmentError:
                pass


def wait(popen, name, timeout):
    endtime = time.time() + timeout
    try:
        while True:
            time.sleep(0.1)
            if popen.poll() is not None:
                return popen.poll()
            if time.time() > endtime:
                break
    finally:
        # we kill anyway, in case some children continue
        kill(popen)
    return 'TIMEOUT'


def run(command, timeout):
    preexec_fn = None
    if not os.environ.get('GREENTEST_MONITORED_GROUP'):
        preexec_fn = getattr(os, 'setpgrp', None)
    if preexec_fn is not None:
        os.environ['GREENTEST_MONITORED_GROUP'] = '1'
    name = ' '.join(command)
    log('\nRunning %s', name)
    popen = subprocess.Popen(command, preexec_fn=preexec_fn)
    popen.setpgrp_enabled = preexec_fn is not None
    result = wait(popen, name, timeout)
    if result:
        log('\n%s failed with code %s', name, result)
    else:
        log('\n%s succeeded', name)
    return result
