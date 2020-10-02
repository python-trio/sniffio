from setuptools import setup, find_packages

exec(open("sniffio/_version.py", encoding="utf-8").read())

LONG_DESC = open("README.rst", encoding="utf-8").read()

setup(
    name="sniffio",
    version=__version__,
    description="Sniff out which async library your code is running under",
    url="https://github.com/python-trio/sniffio",
    long_description=LONG_DESC,
    author="Nathaniel J. Smith",
    author_email="njs@pobox.com",
    license="MIT -or- Apache License 2.0",
    packages=find_packages(),
    package_data={"sniffio": ["py.typed"]},
    install_requires=[],
    keywords=[
        "async",
        "trio",
        "asyncio",
    ],
    extras_require={":python_version < '3.7'": ["contextvars>=2.1"]},
    python_requires=">=3.5",
    tests_require=['curio'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Trio",
        "Framework :: AsyncIO",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
    ],
)
