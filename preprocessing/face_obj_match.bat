
@echo off
setlocal enabledelayedexpansion

set input_file=%1
set output_file=%2

for /f "tokens=*" %%i in ('type "%input_file%" ^| findstr /v /b "vn" ^| findstr /r /c:"^f [0-9]*\/[0-9]*\/[0-9]* [0-9]*\/[0-9]*\/[0-9]* [0-9]*\/[0-9]*\/[0-9]*$"') do (
    set line=%%i
    call set line=%%line:f =f %%
    echo !line! >> %output_file%
)
