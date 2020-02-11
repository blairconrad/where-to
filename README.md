![where-to logo](https://github.com/blairconrad/where-to/raw/master/assets/where-to-128.png "where-to logo")

where-to is a [Python](https://www.python.org/) command-line utility that
displays upcoming Outlook appointments on a Windows lock screen.

The package is [available on pypi](https://pypi.org/project/wehre-to/) and can
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

----
Logo: [Calendar](https://thenounproject.com/paisley.299/uploads/?i=1968675) by
[Paisley](https://thenounproject.com/paisley.299/) from
[the Noun Project](https://thenounproject.com/).
