.. documentation master file, created by
   sphinx-quickstart on Sat Jan 21 19:11:14 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


=================================================================
sniffio: Sniff out which async library your code is running under
=================================================================

You're writing a library. You've decided to be ambitious, and support
multiple async I/O packages, like `Trio
<https://trio.readthedocs.io>`__, and `asyncio
<https://docs.python.org/3/library/asyncio.html>`__, and ... You've
written a bunch of clever code to handle all the differences. But...
how do you know *which* piece of clever code to run?

This is a tiny package whose only purpose is to let you detect which
async library your code is running under.

* Documentation: https://sniffio.readthedocs.io

* Bug tracker and source code: https://github.com/python-trio/sniffio

* License: MIT or Apache License 2.0, your choice

* Contributor guide: https://trio.readthedocs.io/en/latest/contributing.html

* Code of conduct: Contributors are requested to follow our `code of
  conduct
  <https://trio.readthedocs.io/en/latest/code-of-conduct.html>`_
  in all project spaces.

This library is maintained by the Trio project, as a service to the
async Python community as a whole.


.. module:: sniffio

Usage
=====

.. autofunction:: current_async_library

.. autoexception:: AsyncLibraryNotFoundError


Adding support to a new async library
=====================================

If you'd like your library to be detected by ``sniffio``, it's pretty
easy.

**Step 1:** Pick the magic string that will identify your library. To
avoid collisions, this should match your library's PEP 503 normalized name on PyPI.

**Step 2:** There's a special :class:`threading.local` object:

.. data:: thread_local.name

Make sure that whenever your library is potentially executing user-provided code,
this is set to your identifier string. In many cases, you can set it once when
your library starts up and restore it on shutdown:

.. code-block:: python3

   from sniffio import thread_local as sniffio_loop

   # Your library's run function (like trio.run() or asyncio.run())
   def run(...):
       old_name, sniffio_loop.name = sniffio_loop.name, "my-library's-PyPI-name"
       try:
           # actual event loop implementation left as an exercise to the reader
       finally:
           sniffio_loop.name = old_name

In unusual situations you may need to be more fine-grained about it:

* If you're using something akin to Trio `guest mode
  <https://trio.readthedocs.io/en/stable/reference-lowlevel.html#using-guest-mode-to-run-trio-on-top-of-other-event-loops>`__
  to permit running your library on top of another event loop, then
  you'll want to make sure that :func:`current_async_library` can
  correctly identify which library (host or guest) is running at any
  given moment.  To achieve this, you should set and restore
  :data:`thread_local.name` around each "tick" of your library's logic
  (the part that is invoked as a callback from the host loop), rather
  than around an entire ``run()`` function.

* If you're using something akin to `trio-asyncio
  <https://trio-asyncio.readthedocs.io/en/latest/>`__ to implement one async
  library on top of another, then you can set and restore :data:`thread_local.name`
  around each task step (call to a coroutine object ``send()``, ``throw()``, or
  ``close()`` method) into the 'inner' library. For example, trio-asyncio does
  something like:

  .. code-block:: python3

     from sniffio import thread_local as sniffio_loop

     # Your library's compatibility loop
     async def main_loop(self, ...) -> None:
         ...
         handle: asyncio.Handle = await self.get_next_handle()
         old_name, sniffio_loop.name = sniffio_loop.name, "asyncio"
         try:
             result = handle._callback(obj._args)
         finally:
             sniffio_loop.name = old_name

**Step 3:** Send us a PR to add your library to the list of supported
libraries above.

That's it!

.. toctree::
   :maxdepth: 1

   history.rst

====================
 Indices and tables
====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`
