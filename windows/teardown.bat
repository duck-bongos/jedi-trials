@echo ----------------
@echo Begin Teardown
@echo ----------------


Rem remove the virtual environment
deactivate
@rd /s /q tmp
@echo Teardown complete.