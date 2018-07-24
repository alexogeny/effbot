import sqlite3
import pytest
import peewee
from bot import Effbot, get_prefix


def test_bot_exists():
    with pytest.raises(peewee.OperationalError, message="Expected no tables to exist"):
        assert Effbot(get_prefix())

# def test_bot_runs():
#     assert bot.run()
#     assert bot.logout()