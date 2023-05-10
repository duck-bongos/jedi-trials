@call scripts\boundary_clean.bat
@call scripts\map_clean.bat

@if exist tmp (
	deactivate
	rd /s /q tmp
)