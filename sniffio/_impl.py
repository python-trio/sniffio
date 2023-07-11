from contextvars import ContextVar
from typing import Callable, Optional
import sys
import threading

current_async_library_cvar = ContextVar(
    "current_async_library_cvar", default=None
)  # type: ContextVar[Optional[str]]


class _ThreadLocal(threading.local):
    # Since threading.local provides no explicit mechanism is for setting
    # a default for a value, a custom class with a class attribute is used
    # instead.
    name = None  # type: Optional[str]


thread_local = _ThreadLocal()


class AsyncLibraryNotFoundError(RuntimeError):
    pass


def current_async_library() -> str:
    """Detect which async library is currently running.

    The following libraries are currently supported:

    ================   ===========  ============================
    Library             Requires     Magic string
    ================   ===========  ============================
    **Trio**            Trio v0.6+   ``"trio"``
    **Curio**           -            ``"curio"``
    **asyncio**                      ``"asyncio"``
    **Trio-asyncio**    v0.8.2+     ``"trio"`` or ``"asyncio"``,
                                    depending on current mode
    ================   ===========  ============================

    If :func:`current_async_library` returns ``"someio"``, then that
    generally means you can ``await someio.sleep(0)`` if you're in an
    async function, and you can access ``someio``\\'s global state (to
    start background tasks, determine the current time, etc) even if you're
    not in an async function.

    .. note:: Situations such as `guest mode
       <https://trio.readthedocs.io/en/stable/reference-lowlevel.html#using-guest-mode-to-run-trio-on-top-of-other-event-loops>`__
       and `trio-asyncio <https://trio-asyncio.readthedocs.io/en/latest/>`__
       can result in more than one async library being "running" in the same
       thread at the same time. In such ambiguous cases, `sniffio`
       returns the name of the library that has most directly invoked its
       caller. Within an async task, if :func:`current_async_library`
       returns ``"someio"`` then that means you can ``await someio.sleep(0)``.
       Outside of a task, you will get ``"asyncio"`` in asyncio callbacks,
       ``"trio"`` in trio instruments and abort handlers, etc.

    Returns:
      A string like ``"trio"``.

    Raises:
      AsyncLibraryNotFoundError: if called from synchronous context,
        or if the current async library was not recognized.

    Examples:

        .. code-block:: python3

           from sniffio import current_async_library

           async def generic_sleep(seconds):
               library = current_async_library()
               if library == "trio":
                   import trio
                   await trio.sleep(seconds)
               elif library == "asyncio":
                   import asyncio
                   await asyncio.sleep(seconds)
               # ... and so on ...
               else:
                   raise RuntimeError(f"Unsupported library {library!r}")

    """
    value = thread_local.name
    if value is not None:
        return value

    value = current_async_library_cvar.get()
    if value is not None:
        return value

    # Need to sniff for asyncio
    if "asyncio" in sys.modules:
        import asyncio
        try:
            test: Callable[
                [], object
            ] = asyncio._get_running_loop  # type: ignore[attr-defined]
        except AttributeError:
            # 3.6 doesn't have _get_running_loop, so we can only detect
            # asyncio if we're inside a task (as opposed to a callback)
            test = asyncio.Task.current_task  # type: ignore[attr-defined]
        try:
            if test() is not None:
                return "asyncio"
        except RuntimeError:
            pass

    # Sniff for curio (for now)
    if 'curio' in sys.modules:
        from curio.meta import curio_running
        if curio_running():
            return 'curio'

    raise AsyncLibraryNotFoundError(
        "unknown async library, or not in async context"
    )
