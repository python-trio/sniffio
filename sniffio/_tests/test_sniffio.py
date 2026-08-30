import os
import sys

import pytest

from .. import (
    current_async_library, AsyncLibraryNotFoundError,
    current_async_library_cvar, thread_local
)


def test_basics_cvar():
    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    token = current_async_library_cvar.set("generic-lib")
    try:
        assert current_async_library() == "generic-lib"
    finally:
        current_async_library_cvar.reset(token)

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()


def test_basics_tlocal():
    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    old_name, thread_local.name = thread_local.name, "generic-lib"
    try:
        assert current_async_library() == "generic-lib"
    finally:
        thread_local.name = old_name

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

    asyncio.run(this_is_asyncio())
    assert ran == [True]

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()


def test_asyncio_running_loop_without_task():
    import asyncio

    result = []

    def sync_cb():
        result.append(current_async_library())
        loop.stop()

    loop = asyncio.new_event_loop()
    try:
        loop.call_soon(sync_cb)
        loop.run_forever()
    finally:
        loop.close()

    assert result == ["asyncio"]


@pytest.mark.skipif(
    sys.version_info >= (3, 12),
    reason=
    "curio broken on 3.12 (https://github.com/python-trio/sniffio/pull/42)",
)
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
