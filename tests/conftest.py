import pytest
from dotenv import load_dotenv

# Reason variable for skipped tests
reason = "Unit tests using mocks; conversion binaries are not required"


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    # rom-manager is a local tool with no credentials; just pin a working dir.
    monkeypatch.setenv("ROM_DIRECTORY", ".")
    monkeypatch.setenv("ROM_ISO_TYPE", "chd")
