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


def test_uvloop():
    import uvloop

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    ran = []

    async def this_is_asyncio():
        assert current_async_library() == "asyncio"
        # Call it a second time to exercise the caching logic
        assert current_async_library() == "asyncio"
        ran.append(True)

    loop = uvloop.new_event_loop()
    loop.run_until_complete(this_is_asyncio())
    assert ran == [True]

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()


# https://github.com/dabeaz/curio/pull/354
@pytest.mark.skipif(
    os.name == "nt" and sys.version_info >= (3, 9),
    reason="Curio breaks on Python 3.9+ on Windows. Fix was not released yet",
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


def test_asyncio_in_curio():
    import curio
    import asyncio

    async def this_is_asyncio():
        return current_async_library()

    async def this_is_curio():
        return current_async_library(), asyncio.run(this_is_asyncio())

    assert curio.run(this_is_curio) == ("curio", "asyncio")


def test_curio_in_asyncio():
    import asyncio
    import curio

    async def this_is_curio():
        return current_async_library()

    async def this_is_asyncio():
        return current_async_library(), curio.run(this_is_curio)

    assert asyncio.run(this_is_asyncio()) == ("asyncio", "curio")



@pytest.mark.skipif(sys.version_info < (3, 9), reason='to_thread requires 3.9')
def test_curio_in_asyncio_to_thread():
    import curio
    import sniffio
    import asyncio

    async def current_framework():
        return sniffio.current_async_library()


    async def amain():
        sniffio.current_async_library()
        return await asyncio.to_thread(curio.run, current_framework)


    assert asyncio.run(amain()) == "curio"
