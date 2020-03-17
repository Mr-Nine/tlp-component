@echo off

RD .\build /S/Q
RD .\dist /S/Q
RD .\TLPLibrary.egg-info /S/Q

DEL .\TLPLibrary-1.0-py3-none-any.whl

python .\steup.py bdist_wheel

copy .\dist\TLPLibrary-1.0-py3-none-any.whl .\

pause