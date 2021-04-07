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

Make sure that whenever your library is calling a coroutine ``throw()``, ``send()``, or ``close()``
that this is set to your identifier string. In most cases, this will be as simple as:

.. code-block:: python3

   from sniffio import thread_local

   # Your library's step function
   def step(...):
        old_name, thread_local.name = thread_local.name, "my-library's-PyPI-name"
        try:
            result = coro.send(None)
        finally:
            thread_local.name = old_name

**Step 3:** Send us a PR to add your library to the list of supported
libraries above.

That's it!

There are libraries that directly drive a sniffio-naive coroutine from another,
outer sniffio-aware coroutine such as `trio_asyncio`.
These libraries should make sure to set the correct value
while calling a synchronous function that will go on to drive the
sniffio-naive coroutine.


.. code-block:: python3

   from sniffio import thread_local

   # Your library's compatibility loop
   async def main_loop(self, ...) -> None:
        ...
        handle: asyncio.Handle = await self.get_next_handle()
        old_name, thread_local.name = thread_local.name, "asyncio"
        try:
            result = handle._callback(obj._args)
        finally:
            thread_local.name = old_name


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
