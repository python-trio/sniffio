#!/bin/bash

set -ex

MYPY_VERSION=0.782
YAPF_VERSION=0.22.0


pip install -U pip setuptools wheel

if [ "$CHECK_FORMATTING" = "1" ]; then
    pip install yapf==${YAPF_VERSION}
    if ! yapf -rpd sniffio; then
        cat <<EOF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Formatting problems were found (listed above). To fix them, run

   pip install yapf==${YAPF_VERSION}
   yapf -rpi setup.py sniffio

in your local checkout.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
EOF
        exit 1
    fi
    pip install mypy==${MYPY_VERSION}
    if ! mypy --pretty sniffio; then
      cat <<EOF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Type checking problems were found (listed above).

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
EOF
      exit 1
    fi
    exit 0
fi

pip install .

# Actual tests
pip install -Ur test-requirements.txt

mkdir empty
cd empty

pytest -W error -ra -v --pyargs sniffio --cov=sniffio --cov-config=../.coveragerc --verbose

bash <(curl -s https://codecov.io/bash)
