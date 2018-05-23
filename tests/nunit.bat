@echo off
csc /target:library /out:PrimeService.dll PrimeService.cs
IF %ERRORLEVEL% == 0 csc /target:library /out:TestPrime.dll /reference:nunit.framework.dll /reference:PrimeService.dll TestPrime.cs
IF %ERRORLEVEL% == 0 nunit3-console TestPrime.dll