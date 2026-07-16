import sys
import types

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


def test_curio_detection_without_installing_curio():
    """Exercise the curio branch without the deprecated PyPI package.

    Curio no longer ships releases on PyPI (see issue #34). Runtime support
    remains for environments that still vendor curio; this test stubs the
    tiny public surface sniffio actually imports.
    """
    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()

    meta = types.ModuleType("curio.meta")
    meta.curio_running = lambda: True
    curio = types.ModuleType("curio")
    curio.meta = meta

    sys.modules["curio"] = curio
    sys.modules["curio.meta"] = meta
    try:
        assert current_async_library() == "curio"
        # Call it a second time to exercise the caching logic
        assert current_async_library() == "curio"
    finally:
        sys.modules.pop("curio.meta", None)
        sys.modules.pop("curio", None)

    with pytest.raises(AsyncLibraryNotFoundError):
        current_async_library()
