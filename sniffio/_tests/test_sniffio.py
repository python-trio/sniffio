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
