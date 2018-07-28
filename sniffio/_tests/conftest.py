# XX this should switch to using pytest-trio as soon as pytest-trio is
# released...

import inspect
import pytest
from trio.testing import MockClock, trio_test

@pytest.fixture
def mock_clock():
    return MockClock()


@pytest.fixture
def autojump_clock():
    return MockClock(autojump_threshold=0)


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        pyfuncitem.obj = trio_test(pyfuncitem.obj)
