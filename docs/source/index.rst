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
avoid collisions, this should match your library's name on PyPI.

**Step 2:** There's a special :class:`contextvars.ContextVar` object:

.. data:: current_async_library_cvar

Make sure that whenever your library is running, this is set to your
identifier string. In most cases, this will be as simple as:

.. code-block:: python3

   from sniffio import current_async_library_cvar

   # Your library's run function
   def run(...):
        token = current_async_library_cvar.set("my-library's-PyPI-name")
        try:
            # The actual body of your run() function:
            ...
        finally:
            current_async_library_cvar.reset(token)

**Step 3:** Send us a PR to add your library to the list of supported
libraries above.

That's it!

Notes:

On older Pythons without native contextvars support, sniffio
transparently uses `the official contextvars backport
<https://pypi.org/project/contextvars/>`__, so you don't need to worry
about that.

There are libraries that can switch back and forth between different
async modes within a single call-task – like ``trio_asyncio`` or
Twisted's asyncio operability. These libraries should make sure to set
the value back and forth at appropriate points.

The general rule of thumb: :data:`current_async_library_cvar` should
be set to X exactly at those moments when ``await X.sleep(...)`` will
work.

.. warning:: You shouldn't attempt to read the value of
   ``current_async_library_cvar`` directly –
   :func:`current_async_library` has a little bit more cleverness than
   that.

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
