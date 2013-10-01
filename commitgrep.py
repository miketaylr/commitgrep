#!/usr/bin/env python

from __future__ import print_function
import argparse
import datetime
import os
import re
import shutil
import smtplib
import subprocess
import sys


def get_header(repo_name):
    '''Get the beginning of our HTML document (with inlined styles)'''
    css = open(os.path.join(os.getcwd(), os.pardir) + '/table.css', 'r').read()
    return """<!DOCTYPE html>
<html lang=en>
<title>commitgrep.py results for {0}</title>
<meta name="viewport" content="width=device-width">
<style>{1}</style>""".format(repo_name, css)


def get_thead(caption):
    '''Return the beginning of a <table> with a <caption>'''
    return """<table class="table table-responsive">
<caption>Commits related to the token: {0}, as of {1}</caption>
<thead><tr><th>SHA</th><th>date</th><th>commit</th></tr></thead>
""".format(caption, date)


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
    '''Make git do the actual work.'''
    return subprocess.check_output(["git", "log", "-S{0}".format(token),
                                    "--format=" + get_row(repo_url)])


def clone_repo(repo_url):
    '''Clones a repo and enters its directory.'''
    clone_output = subprocess.check_output(["git", "clone", repo_url])
    print(clone_output, file=sys.stdout)
    os.chdir(os.getcwd() + '/' + repo_name)


def send_email():
    '''Send an email from commitgrep@gmail.com with the results. You'll want
    to change this if you don't have the password. This isn't very flexible
    but it serves my needs. Pull requests welcome, etc.'''
    from_addr = 'commitgrep@gmail.com'
    to_addr = email
    passwd = open(os.path.join(os.getcwd(), os.pardir) + '/password.txt', 'r')
    # seek back to the beginning of the file
    out_file.seek(0)
    body = out_file.read()
    headers = "\r\n".join(
        ["From: " + from_addr,
         "Subject: [commitgrep] results for {0} ({1})".format(repo_name, date),
         "To: " + to_addr,
         "MIME-Version: 1.0",
         "Content-Type: text/html"]
    )
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login('commitgrep@gmail.com', passwd.readline())
    server.sendmail(from_addr, to_addr, headers + "\r\n\r\n" + body)


def write_to_disk():
    '''Dump all the strings in a file, optionally emailing it.'''
    print(get_header(repo_name), file=out_file)
    for token in tokens:
        print(get_thead(token), file=out_file)
        print(grep_logs(token, repo_url) + "</table>", file=out_file)
    if email:
        if re.match(r'[^@]+@[^@]+\.[^@]+', email):
            send_email()
        else:  # TODO: raise this earlier
            raise Exception("Is your email address correct?")
    clean_up()


def clean_up():
    os.chdir(os.pardir)
    shutil.rmtree(os.path.join(os.getcwd(), repo_name))
    if not email:
        print("All cleaned up. See {0} for results.".format(out_file.name),
              file=sys.stdout)
    else:
        print("An email was sent to {0}".format(email), file=sys.stdout)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help='Github git repo URL')
    parser.add_argument('tokens', nargs='+',
                        help=('token [, token , ...]. A space separated list'
                              ' of tokens to search the repo for'))
    parser.add_argument('-e', '--email',
                        help='Email the results to the given email address.')
    args = parser.parse_args()
    repo_url = args.repo
    repo_name = get_repo_name(repo_url)
    tokens = args.tokens
    email = args.email
    date = datetime.datetime.now().strftime("%m-%d-%Y")
    out_file = open(repo_name + '.html', 'w+')
    clone_repo(repo_url)
    write_to_disk()
