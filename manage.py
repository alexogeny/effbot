import subprocess
import os, signal, time

def run_as_test():
    proc = subprocess.Popen('python ./bot.py')
    time.sleep(10)
    if getattr(signal, 'SIGKILL', None):
        os.kill(proc.pid, signal.SIGKILL)
    else:
        os.kill(proc.pid, signal.SIGTERM)
    return True

# def run_as_live():
#     proc = subprocess.Popen('python bot.py')
#     try:
#         while True:
#             time.sleep(10)
#     except KeyBoardInterrupt:
#         os.kill(proc.pid, signal.SIGKILL)
