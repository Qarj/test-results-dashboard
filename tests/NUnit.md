# NUnit integration

## Installation

### NUnit Framework
* Download NUnit framework: https://github.com/nunit/nunit/releases/tag/v3.10.1
* Place in folder `C:\cs` (should not matter)
* Copy `C:\cs\NUnit.Framework-3.10.1\bin\net40\nunit.framework.dll` to folder with UnitTests.cs
* Add csc to system path `C:\Windows\Microsoft.NET\Framework64\v4.0.30319`
* `csc /target:library /out:PrimeService.dll PrimeService.cs`
* `csc /target:library /out:TestPrime.dll /reference:nunit.framework.dll /reference:PrimeService.dll TestPrime.cs`

### Install NUnit Console
* Download msi from https://github.com/nunit/nunit-console/releases
* Add to System path `C:\Program Files (x86)\NUnit.org\nunit-console`
* Run as `nunit3-console TestPrime.dll`

## Architecture

https://github.com/nunit/docs/wiki/TestContext

### In global test setup (run only once per run):
- [x] Generate & store run_name
- [x] Find & store run_server name

### Log in individual test setup
* test_name (NUnit.Framework.TestContext.CurrentContext.Test.FullName or NUnit.Framework.TestContext.CurrentContext.Test.Name)
* app_name
* run_name
* run_server

### Log in Teardown
- [ ] test_name
- [ ] app_name
- [ ] run_name
- [ ] run_server
* test_passed - Outcome.Status - Inconclusive (map to fail), Passed, Failed
* small message (not stack trace) Outcome.Site
* test_passed - Skipped

Post additional info (optional):
* Stack Trace
* Screenshot
(keyed by run_name, app_name, test_name)

