from setuptools import setup
from bot import bot

setup(
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)