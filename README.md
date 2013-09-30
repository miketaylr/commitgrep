# commitgrep.py*

### What?

This utility clones a github hosted repository, runs `git log -S<token>`, and creates a table with hyperlinks to commits from the returned logs.

You'll get an .html file that looks something like this: http://miketaylr.github.io/commitgrep/. Or exactly like that.

### Usage
`python commitgrep.py repourl token [, token, ...]`

To create a file named jquery.html which greps for commits that have something to do with the tokens `firefox` and `gecko`:

`python commitgrep.py git@github.com:jquery/jquery.git firefox gecko`

### License

Licensed under the [Mozilla Public License Version 2.0](http://www.mozilla.org/MPL/2.0/)

*coming up with good names is hard. This doesn't even use --grep, because that's limited to log messages. :|