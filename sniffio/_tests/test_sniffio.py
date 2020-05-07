import sys
import warnings

import pytest

from .. import (
    current_async_library, AsyncLibraryNotFoundError,
    current_async_library_cvar
)


def test_basics():
    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    token = current_async_library_cvar.set("generic-lib")
    try:
        assert current_async_library() == "generic-lib"
    finally:
        current_async_library_cvar.reset(token)

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()


def test_asyncio():
    import asyncio

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    ran = []

    async def this_is_asyncio():
        assert current_async_library() == "asyncio"
        # Call it a second time to exercise the caching logic
        assert current_async_library() == "asyncio"
        ran.append(True)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(this_is_asyncio())
    assert ran == [True]
    loop.close()

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()


def test_curio():
    import curio

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    ran = []

    async def this_is_curio():
        assert current_async_library() == "curio"
        # Call it a second time to exercise the caching logic
        assert current_async_library() == "curio"
        ran.append(True)

    curio.run(this_is_curio)
    assert ran == [True]

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()


@pytest.fixture(params=['select', 'asyncio'])
def reactor(request):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        from twisted.internet import asyncioreactor, selectreactor

    if request.param == 'asyncio':
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncioreactor.install(loop)
        yield
        loop.close()
    else:
        selectreactor.install()
        yield

    del sys.modules['twisted.internet.reactor']


def test_twisted(reactor):
    from twisted.internet import reactor

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    ran = []

    async def this_is_twisted():
        try:
            assert current_async_library() == "twisted"
            ran.append(True)
        finally:
            reactor.stop()

    import twisted.internet.defer
    reactor.callWhenRunning(
        lambda: twisted.internet.defer.ensureDeferred(this_is_twisted()),
    )
    reactor.run()
    assert ran == [True]

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()
