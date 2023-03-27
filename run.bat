@Rem clean all the directories
@call clean.bat

Rem detect the boundary
call scripts\detect_boundary.bat
echo worked?
Rem run the mapping
call scripts\run_harmonic_map.bat

call scripts\teardown.bat

echo -------------------------
echo Run complete
echo -------------------------