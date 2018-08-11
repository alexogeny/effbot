
import pytest
from bot import Effribot, get_prefix
from manage import run_as_test

import os, signal, time, threading

def test_bot_exists():
    assert Effribot(command_prefix=get_prefix)

def test_bot_runs():
    class TestThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.daemon = True
            self.bot = Effribot(command_prefix=get_prefix)
        def run(self):
            return self.bot.run()
        def __del__(self):
            pass
    t = TestThread()
    t.start()
    time.sleep(10)
    del t
    assert True
