ECHO OFF
REM A Windows 'build' script. Run this after editing the addon's files. Then restart Anki. 
REM Don't make edits over there in addons directly, as VCS won't see them, and an Anki or addon upgrade
REM might destroy them.
ECHO ON

REM copy all modified (D) files and folders (even E, empty ones), and overwrite (Y) without prompting
REM (Like Anki's own deployment, this does NOT remove any files. The simplest way to do so manually here is to delete the addons folder, then re-run.)

xcopy /D /Y flashgr.py %USERPROFILE%\documents\Anki\addons\
xcopy /D /E /Y .\flashgrid\*.* %USERPROFILE%\documents\Anki\addons\flashgrid\

PAUSE

