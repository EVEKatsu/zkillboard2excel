import sys
import threading
import inspect
import ctypes
import builtins

import zerorpc

import zkillboard2excel


# Quote from: https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread
def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class ThreadWithExc(threading.Thread):
    '''A thread class that supports raising exception in the thread from
       another thread.
    '''
    def _get_my_tid(self):
        """determines this (self's) thread id

        CAREFUL : this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        # TODO: in python 2.6, there's a simpler way to do : self.ident

        raise AssertionError("could not determine the thread's id")

    def raiseExc(self, exctype):
        """Raises the given exception type in the context of this thread.

        If the thread is busy in a system call (time.sleep(),
        socket.accept(), ...), the exception is simply ignored.

        If you are sure that your exception should terminate the thread,
        one way to ensure that it works is:

            t = ThreadWithExc( ... )
            ...
            t.raiseExc( SomeException )
            while t.isAlive():
                time.sleep( 0.1 )
                t.raiseExc( SomeException )

        If the exception is to be caught by the thread, you need a way to
        check that your thread has caught it.

        CAREFUL : this function is executed in the context of the
        caller thread, to raise an excpetion in the context of the
        thread represented by this instance.
        """
        _async_raise( self._get_my_tid(), exctype )
# Quote end


class Api:
    def __init__(self, _resources_path):
        self._script = None
        self._resources_path = _resources_path
        self._texts = []
        builtins.print = self._append

    def _append(self, text):
        s = str(text)
        if not s.startswith('Cached:'):
            s = s.replace('Download:', '').strip()
            if s.startswith('https://raw.githubusercontent.com'):
                return

            s = s.replace('https://zkillboard.com/api', 'zkb: ')
            s = s.replace('https://esi.evetech.net/latest', 'esi: ')
            self._texts.append(s)

    def export(self):
        if self._script:
            self._append('The script is already running.')
            return 'running'
        else:
            self._script = ThreadWithExc(target=zkillboard2excel.run, args=(self._resources_path,))
            self._script.start()
            self._append('Start')
            return 'start'

    def terminate(self):
        if self._script:
            self._script.raiseExc(Exception)
            self._script = None
            self._append('Stop')
        else:
            self._append('The script is not running.')

        return 'stop'

    def log(self):
        if self._script and not self._script.is_alive():
            self._script = None
            self._append('Done')

        if self._texts:
            text = '&#13;'.join(self._texts)
            self._texts[:] = []
            return text
        else:
            return ''

    def echo(self, text):
        return text

def main():
    resources_path = '.'
    if len(sys.argv) >= 2:
        resources_path = sys.argv[1]

    api = Api(resources_path)

    server = zerorpc.Server(api)
    server.bind('tcp://127.0.0.1:4242')
    server.run()

if __name__ == '__main__':
    main()
