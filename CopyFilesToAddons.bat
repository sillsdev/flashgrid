ECHO OFF
REM Windows script. Run this after editing the addon's files. Then restart Anki. 
REM Don't make edits over there in addons directly, as VCS won't see them, and an Anki or addon upgrade
REM might destroy them.
ECHO ON

xcopy /D /Y flashgrid.py %USERPROFILE%\documents\Anki\addons\

PAUSE
