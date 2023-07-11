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

    def test_from_callback():
        assert current_async_library() == "asyncio"
        ran.append(2)

    async def this_is_asyncio():
        asyncio.get_running_loop().call_soon(test_from_callback)
        assert current_async_library() == "asyncio"
        ran.append(1)

    asyncio.run(this_is_asyncio())
    assert ran == [1, 2]

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()


# https://github.com/dabeaz/curio/pull/354 has the Windows/3.9 fix.
# 3.12 error is from importing a private name that no longer exists in the
# multiprocessing module; unclear if it's going to be fixed or not.
@pytest.mark.skipif(
    (os.name == "nt" and sys.version_info >= (3, 9)) or sys.version_info >= (3, 12),
    reason="Curio breaks on Python 3.9+ on Windows and 3.12+ everywhere",
)
def test_curio():
    import curio

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    ran = []

    async def this_is_curio():
        assert current_async_library() == "curio"
        ran.append(True)

    curio.run(this_is_curio)
    assert ran == [True]

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()
