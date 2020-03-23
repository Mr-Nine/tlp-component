@echo off

del .\source\core.rst
del .\source\entity.rst
del .\source\error.rst
del .\source\modules.rst
del .\source\service.rst
del .\source\tools.rst

sphinx-apidoc -o .\source ..\TLPLibrary\

make html

pause