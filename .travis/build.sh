#!/usr/bin/env bash

pip install numpy
pip install scipy==0.18
pip install matplotlib
pip install future
pip install Pillow
pip install PyYAML
pip install scikits.samplerate==0.3.3
pip install librosa==0.4.2
pip install vmo==0.23.3

# custom packages
pip install -q git+https://github.com/himito/snakes.git

if [[ "$TRAVIS_OS_NAME" = "osx" ]]; then
  python setup_osx.py --quiet py2app
fi
