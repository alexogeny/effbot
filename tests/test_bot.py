import sqlite3
import pytest
import peewee
from bot import Effribot, get_prefix

def test_bot_exists():
    assert Effribot(command_prefix=get_prefix)

def test_bot_runs():
    assert Effribot(command_prefix=get_prefix).run()
