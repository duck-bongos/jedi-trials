@Rem Run the harmonic map program

@pushd optimization\HarmonicMap\
@echo Current working directory is %CD%

@Rem enter the build directory
@pushd .\build\
@echo Current working directory is %CD%

cmake ..
cmake --build .

@Rem return to optimization/HarmonicMap
@popd
@echo Current working directory is %CD%

@Rem check the bin directory for the executable.
@Rem The executable name is the same as in line 22 of
@Rem optimization/HarmonicMap/harmonic_map/CMakeLists.txt

@if not exist bin\map.exe (
	@echo Executable doesn't exist. Please check the CMakeLists.txt and the build.
	goto :end
)

bin\map.exe ..\..\data\annotated\source\masked_source_object.obj ..\..\data\optimized\mapped_source.obj

bin\map.exe ..\..\data\annotated\target\masked_target_object.obj ..\data\optimized\mapped_target.obj

Rem return to the top level directory
popd
@echo Current working directory is %CD%

:end
@echo End of Harmonic Map