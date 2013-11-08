# commitgrep.py*

### What?

This utility clones a github hosted repository, runs `git log -S<token>`, and creates a table with hyperlinks to commits from the returned logs.

You'll get an .html file that looks something like this: http://miketaylr.github.io/commitgrep/. Or exactly like that.

### Usage
```
usage: commitgrep.py [-h] [-e EMAIL] [--relative] repo tokens [tokens ...]

positional arguments:
  repo           Github git repo URL
  tokens         token [, token , ...]. A space separated list of tokens to
                 search the repo for

optional arguments:
  -h, --help     show this help message and exit
  --email EMAIL  Email the results to the given email address.
  --relative     This option will grep the repo relative to the last    time it
                 was run, creating a lasthead.txt file to keep track of this.
                 This may be useful to run every 24 hours via CRON, etc.
```

### Examples

To create a file named jquery.html which greps for commits that have something to do with the tokens `firefox` and `gecko`:

`python commitgrep.py git@github.com:jquery/jquery.git firefox gecko`

To email the results grepping over jquery's repo for "event":

`python commitgrep.py --email=foo@bar.com --relative https://github.com/jquery/jquery.git event`

### License

Licensed under the [Mozilla Public License Version 2.0](http://www.mozilla.org/MPL/2.0/)

*coming up with good names is hard. This doesn't even use --grep, because that's limited to log messages. :|
