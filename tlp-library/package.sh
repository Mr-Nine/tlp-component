#! /bin/bash

rm -rf ./build ./dist ./TLPLibrary.egg-info TLPLibrary-1.0-py3-none-any.whl

python ./steup.py bdist_wheel

cp ./dist/TLPLibrary-1.0-py3-none-any.whl ./
