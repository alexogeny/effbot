import sqlite3
import pytest
import peewee
from bot import Effbot, get_prefix
from models.base import BaseModel

@pytest.fixture(autouse=True)
def mock_models(monkeypatch):
    def mock_server():
        class Server(BaseModel):
            data = peewee.BlobField()
        return Server()
    def mock_user():
        class User(BaseModel):
            data = peewee.BlobField()
        return User()
    monkeypatch.setattr(models, 'Server', mock_server)
    monkeypatch.setattr(models, 'User', mock_user)

def test_bot_exists():
    assert Effbot(command_prefix=get_prefix)

# def test_bot_runs():
#     assert bot.run()
#     assert bot.logout()