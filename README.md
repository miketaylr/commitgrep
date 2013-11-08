# commitgrep.py*

### What?

This utility clones a github hosted repository, runs `git log -S<token>`, and creates a table with hyperlinks to commits from the returned logs.

You'll get an .html file that looks something like this: http://miketaylr.github.io/commitgrep/. Or exactly like that.

### Usage
`python commitgrep.py repourl token [, token, ...]`

To create a file named jquery.html which greps for commits that have something to do with the tokens `firefox` and `gecko`:

`python commitgrep.py git@github.com:jquery/jquery.git firefox gecko`

To email the results grepping over jquery's repo for "event":

`python commitgrep.py --email=foo@bar.com --relative https://github.com/jquery/jquery.git event`

### Email

If you pass in the optional `--email` argument, the script will send you an email from `commitgrep@gmail.com` with the commits containing the tokens rather than create an html file.

*TODO*: If it's the first time it is run, you'll get the output for the entire history of the repo. Subsequent repos will compare only the commits made since the last run, and if there's no match no email will be sent.

### License

Licensed under the [Mozilla Public License Version 2.0](http://www.mozilla.org/MPL/2.0/)

*coming up with good names is hard. This doesn't even use --grep, because that's limited to log messages. :|
