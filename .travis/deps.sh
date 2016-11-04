curl -L http://www.mega-nerd.com/SRC/libsamplerate-0.1.8.tar.gz | tar xz
(cd libsamplerate-0.1.8; ./configure; make; make install)

if [[ "$TRAVIS_OS_NAME" = "osx" ]]; then
  # update package
  brew update

  # install dot command and copy to resources
  brew install graphviz
  cp $(which dot) resources

  # install python via brew
  brew install python

  # make brew python the system default
  brew link --overwrite python

  pip install git+https://github.com/himito/macholib.git
  pip install setuptools==19.2
  pip install py2app
fi
