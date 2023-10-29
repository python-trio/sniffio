from functools import partial
from contextvars import ContextVar
from typing import Optional
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


def _guessed_mode() -> str:
    # special support for trio-asyncio
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
            current_task = asyncio.current_task  # type: ignore[attr-defined]
        except AttributeError:
            current_task = asyncio.Task.current_task  # type: ignore[attr-defined]
        try:
            if current_task() is not None:
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


def _noop_hook(v: str) -> str:
    return v


_NO_HOOK = object()

# this is publicly mutable, if an async framework wants to implement complex
# async gen hook behaviour it can set
# sniffio.hooks[__package__] = detect_me. As long as it does so before
# defining its async gen finalizer function it is free from race conditions
hooks = {
    # could be trio-asyncio or trio-guest mode
    # once trio and trio-asyncio and sniffio align trio should set
    # sniffio.hooks['trio'] = detect_trio
    "trio": _guessed_mode,
    # pre-cache some well-known well behaved asyncgen_finalizer modules
    # and so it saves a trip around _is_asyncio(finalizer) when we
    # know asyncio is asyncio and curio is curio
    "asyncio.base_events": partial(_noop_hook, "asyncio"),
    "curio.meta": partial(_noop_hook, "curio"),
    _NO_HOOK: _guessed_mode,  # no hooks installed, fallback
}


def current_async_library() -> str:
    """Detect which async library is currently running.

    The following libraries are currently special-cased:

    ================   ===========  ============================
    Library             Requires     Magic string
    ================   ===========  ============================
    **Trio**            Trio v0.6+   ``"trio"``
    **Curio**           -            ``"curio"``
    **asyncio**                      ``"asyncio"``
    **Trio-asyncio**    v0.8.2+     ``"trio"`` or ``"asyncio"``,
                                    depending on current mode
    ================   ===========  ============================

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
    finalizer = sys.get_asyncgen_hooks().finalizer
    finalizer_module = getattr(finalizer, "__module__", _NO_HOOK)
    if finalizer_module is None:  # finalizer is old cython function
        if "uvloop" in sys.modules and _is_asyncio(finalizer):
            return "asyncio"

    try:
        hook = hooks[finalizer_module]
    except KeyError:
        pass
    else:
        return hook()

    # special case asyncio - when implementing an asyncio event loop
    # you have to implement _asyncgen_finalizer_hook in your own module
    if _is_asyncio(finalizer):  # eg qasync _SelectorEventLoop
        hooks[finalizer_module] = partial(_noop_hook, "asyncio")
        return "asyncio"

    # when implementing a twisted reactor you'd need to rely on hooks defined in
    # twisted.internet.defer
    assert type(finalizer_module) is str
    sniffio_name = finalizer_module.rpartition(".")[0]
    hooks[finalizer_module] = partial(_noop_hook, sniffio_name)
    return sniffio_name


def _is_asyncio(finalizer):
    if "asyncio" in sys.modules:
        import asyncio
        try:
            return finalizer == asyncio.get_running_loop()._asyncgen_finalizer_hook
        except RuntimeError:
            return False
    return False
