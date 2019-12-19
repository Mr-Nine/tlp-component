@echo off

RD /s /q build
RD /s /q dist
RD /s /q TLPLibrary.egg-info

DEL .\TLPLibrary-1.0-py3-none-any.whl

python .\steup.py bdist_wheel

copy .\dist\TLPLibrary-1.0-py3-none-any.whl .\

pause