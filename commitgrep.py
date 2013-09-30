#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import shutil
import argparse
import datetime
import subprocess


def get_header(repo_name):
    return """<!DOCTYPE html>
<html lang=en>
<title>commitgrep.py results for {0}</title>
<meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="table.css">
""".format(repo_name)


def get_thead(caption):
    return """<table class="table table-responsive">
<caption>Commits related to the token: {0}, as of {1}</caption>
<thead><tr><th>SHA</th><th>date</th><th>commit</th></tr></thead>
""".format(caption, datetime.datetime.now().strftime("%m-%d-%Y"))


def get_repo_name(repo_url):
    '''Takes a github repo URL and returns the repo name.'''
    return repo_url.split('/')[-1].replace('.git', '')


def get_row(repo_url):
    '''Creates a format string that is passed to git log (in the form of a
       table <tr> with the following format options:
        %H: commit hash (long one)
        %h: commit hash (abbreviated)
        %ar author date, relative
        %s: subject'''
    if repo_url.find('git@') == 0:  # e.g. git@github.com:foo/bar.git
        path = repo_url.split('@')[1]
    elif repo_url.find('https:') == 0:  # e.g., https://github.com/foo/bar.git
        path = repo_url.split('://')[1]
    else:
        raise Exception("Is this a git clone URL from github?")
    return '''<tr>
      <td><a href="https://{0}/commit/%H">%h</a></td>
      <td>%ar</td>
      <td>%s</td>
    </tr>'''.format(path.replace(':', '/').replace('.git', ''))


def grep_logs(token, repo_url):
    return subprocess.check_output(["git", "log", "-S{0}".format(token),
                                    "--format=" + get_row(repo_url)])


def clone_repo(repo_url):
    '''Clones a repo and enters its directory.'''
    clone_output = subprocess.check_output(["git", "clone", repo_url])
    print(clone_output, file=sys.stdout)
    os.chdir(os.getcwd() + '/' + get_repo_name(repo_url))


def write_to_disk():
    print(get_header(get_repo_name(repo_url)), file=out_file)
    for token in tokens:
        print(get_thead(token), file=out_file)
        print(grep_logs(token, repo_url), file=out_file)
        print("</table>", file=out_file)
    clean_up()


def clean_up():
    os.chdir(os.pardir)
    shutil.rmtree(os.path.join(os.getcwd(), get_repo_name(repo_url)))
    print("All cleaned up. See {0} for results.".format(out_file.name),
          file=sys.stdout)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help='Github git repo URL')
    parser.add_argument('tokens', nargs='+',
                        help=('token [, token , ...]. A space separated list'
                              ' of tokens to search the repo for'))
    args = parser.parse_args()
    repo_url = args.repo
    tokens = args.tokens
    out_file = open(get_repo_name(repo_url) + '.html', 'w')
    clone_repo(repo_url)
    write_to_disk()
