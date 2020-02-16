# How to build

At the time of writing the build is only confirmed to work on Windows.

## Prerequisites

Ensure that the following is installed:

* [poetry](https://python-poetry.org/) - version 1.0.3 is confirmed to work, but others may as well

## Running automated tests

From a command prompt in the root of the repo, run

```powershell
poetry run task test
```

This will run the tests in all supported environments, replicating the testing
done on the continuous integration server, and is the best way to ensure that
any changes you make will work on the server.

## Manual testing

You can execute manual tests by running where-to through poetry:

```powershell
poetry run where-to [additional arguments]
```
