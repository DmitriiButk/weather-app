import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def pytest_configure(config):
    config._inicache["asyncio_default_fixture_loop_scope"] = "function"
