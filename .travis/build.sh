pip install -r requirements/ci.txt
pip install scikits.samplerate==0.3.3
pip install librosa==0.4.2

# custom packages
pip install -q git+https://github.com/himito/snakes.git
pip install -q git+https://github.com/himito/vmo.git

if [[ "$TRAVIS_OS_NAME" = "osx" ]]; then
  python setup_osx.py --quiet py2app
fi
