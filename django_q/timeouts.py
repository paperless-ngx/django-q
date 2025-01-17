"""
Using signal, implements a alarm based callback after a certain amount of time.
Borrowed from rq: https://github.com/rq/rq/blob/master/rq/timeouts.py
"""
import signal


class JobTimeoutException(SystemExit):
    """Raised when a job takes longer to complete than the allowed maximum
    timeout value.  Inherits from SystemExit to prevent user code which catches
    Exception from not timing out correctly.
    """
    pass


class BaseDeathPenalty:
    """Base class to setup job timeouts."""

    def __init__(self, timeout, exception=JobTimeoutException, **kwargs):
        # If signal.alarm timeout is 0, no alarm will be scheduled
        # by signal.alarm
        if timeout is None:
            timeout = 0
        self._timeout = timeout
        self._exception = exception

    def __enter__(self):
        self.setup_death_penalty()

    def __exit__(self, type, value, traceback):
        # Always cancel immediately, since we're done
        try:
            self.cancel_death_penalty()
        except JobTimeoutException:
            # Weird case: we're done with the with body, but now the alarm is
            # fired.  We may safely ignore this situation and consider the
            # body done.
            pass

        # __exit__ may return True to supress further exception handling.  We
        # don't want to suppress any exceptions here, since all errors should
        # just pass through, BaseTimeoutException being handled normally to the
        # invoking context.
        return False

    def setup_death_penalty(self):
        raise NotImplementedError()

    def cancel_death_penalty(self):
        raise NotImplementedError()


class UnixSignalDeathPenalty(BaseDeathPenalty):

    def handle_death_penalty(self, signum, frame):
        raise self._exception('Task exceeded maximum timeout value '
                              '({0} seconds)'.format(self._timeout))

    def setup_death_penalty(self):
        """Sets up an alarm signal and a signal handler that raises
        an exception after the timeout amount (expressed in seconds).
        """
        signal.signal(signal.SIGALRM, self.handle_death_penalty)
        signal.alarm(self._timeout)

    def cancel_death_penalty(self):
        """Removes the death penalty alarm and puts back the system into
        default signal handling.
        """
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
