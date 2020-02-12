![where-to logo](https://github.com/blairconrad/where-to/raw/master/assets/where-to-128.png "where-to logo")

where-to is a [Python](https://www.python.org/) command-line utility that
displays upcoming Outlook appointments on a Windows lock screen.

The package is [available on pypi](https://pypi.org/project/where-to/) and can
be installed from the command line by typing

```
pip install where-to
```

Once installed, a `where-to` command will be added to your Python scripts
directory. You can run it to show the next appointment, all appointments for the
rest of the day only appointments due to start at this time.

Examples:

```shell
where-to upcoming # shows all appointments for the rest of the day
where-to next
where-to now      # appointments starting between 10 minutes ago and 15  minutes hence
```

Get more help via `where-to --help`.

Note that `where-to` is built to be console-less, so that when invoked from a Windows scheduled
task it will not pop up an annoying console window. The help message (and indeed all output)
should be presented in an instance of the notepad editor. If this isn't working, or if for some
reason you want to see a display in a terminal window, the alternative executable `where-to-console`
is also available. This can be combined with the `--display-mode list` option to print appointments
rather than splash them on the lock screen.


----
Logo: [Calendar](https://thenounproject.com/paisley.299/uploads/?i=1968675) by
[Paisley](https://thenounproject.com/paisley.299/) from
[the Noun Project](https://thenounproject.com/).
