@Rem starting from top level directory
@echo Removing data\optimized contents...
@del /f /q data\optimized\*
@echo Removed data\optimized contents.


@Rem clean the data/optimized directory
@pushd optimization\HarmonicMap
@echo Changed working directory to %CD%

@Rem clean the build and bin
@echo Removing .\bin contents...
@del /f /q bin\*
@echo Removed .\bin contents

@echo Removing .\build contents...
@del /f /q build\*
@rd /s /q build
mkdir build
@echo Removed .\build contents

@popd
@echo Returned to %CD%