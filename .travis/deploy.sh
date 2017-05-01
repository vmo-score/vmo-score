#!/usr/bin/env bash

if [[ "$TRAVIS_TAG" = "" ]];
then
  exit 0
fi

if [[ "$TRAVIS_OS_NAME" = "osx" ]]; then
  cd dist
  zip -r -9 "vmo-score-$TRAVIS_TAG-OSX.zip" VMO-Score.app
fi
