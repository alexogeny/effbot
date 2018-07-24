
import pytest
import peewee
from bot import Effribot, get_prefix
from manage import run_as_test

def test_bot_exists():
    assert Effribot(command_prefix=get_prefix)

def test_bot_runs():
    assert run_as_test()
