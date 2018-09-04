
import pytest
from cogs.math import do_math
from manage import run_as_test

import os, signal, time, threading, asyncio

# def test_bot_exists():
#     assert Effribot(command_prefix=get_prefix)

# def test_bot_runs():
#     class TestThread(threading.Thread):
#         def __init__(self):
#             threading.Thread.__init__(self)
#             self.daemon = True
#             self.bot = Effribot(command_prefix=get_prefix)
#         def run(self):
#             return self.bot.run()
#         def __del__(self):
#             pass
#     t = TestThread()
#     t.start()
#     time.sleep(10)
#     del t
#     assert True

def test_do_math():
    assert do_math('2*2') == '4'
    assert do_math('3+3') == '6'
    assert do_math('3*2+3') == '9'
    

# def test_math_run_math()
#     loop = asyncio.new_event_loop()
#     assert exec_math('333^333^333^333^333').startswith('Error')