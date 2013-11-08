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

has_run = False


def get_header(repo_name):
    '''Get the beginning of our HTML document (with inlined styles)'''
    css = open(os.path.join(os.getcwd(), os.pardir) + '/table.css', 'r').read()
    header = """<!DOCTYPE html>
<html lang=en>
<title>commitgrep.py results for {0}</title>
<meta name="viewport" content="width=device-width">
<style>{1}</style>"""

    return header.format(repo_name, css)


def get_thead(caption):
    '''Return the beginning of a <table> with a <caption>'''
    thead = """<table class="table table-responsive">
<caption>Commits related to the token: {0}, as of {1}</caption>
<thead><tr><th>SHA</th><th>date</th><th>commit</th></tr></thead>"""

    return thead.format(caption, date)


def get_repo_name(repo_url):
    '''Takes a github repo URL and returns the repo name.'''
    return repo_url.split('/')[-1].replace('.git', '')


def get_row(repo_url):
    '''Creates a format string that is passed to git log (in the form of a
       table <tr> with the following format options:
        %H:  commit hash (long one)
        %h:  commit hash (abbreviated)
        %ar: author date, relative
        %s:  subject'''
    tr = '''<tr><td><a href="https://{0}/commit/%H">%h</a></td>
  <td>%ar</td>
  <td>%s</td></tr>'''

    if repo_url.find('git@') == 0:  # e.g. git@github.com:foo/bar.git
        path = repo_url.split('@')[1]
    elif repo_url.find('https:') == 0:  # e.g., https://github.com/foo/bar.git
        path = repo_url.split('://')[1]
    else:
        raise Exception("Is this a git clone URL from github?")
    return tr.format(path.replace(':', '/').replace('.git', ''))


def get_from_sha():
    '''
    If we've passed in the --relative flag, this will return the SHA of the HEAD
    of the last time we've grepped the logs. Otherwise, it returns None.'''
    if args.relative:
        global has_run
        if has_run is True:
            try:
                head_file = open(os.path.join(os.getcwd(), os.pardir)
                                 + '/lasthead.txt', 'r')
                last_known_head = head_file.readline()
            except IOError:
                print('Something went wrong with lasthead.txt!')
                return None
        else:
            head_file = open(os.path.join(os.getcwd(), os.pardir)
                             + '/lasthead.txt', 'w')
            head_file.seek(0)
            last_known_head = subprocess.check_output(["git", "rev-parse",
                                                       "HEAD"]).rstrip()
            print(last_known_head, file=head_file)
            has_run = True
        print(last_known_head)
        return last_known_head
    else:
        return None


def grep_logs(token, repo_url, from_sha=None):
    '''Make git do the actual work.'''
    command = ["git", "log", "-S{0}".format(token),
               "--format=" + get_row(repo_url)]
    if from_sha:
        commit_range = from_sha + "...HEAD"
        command.append(commit_range)
    return subprocess.check_output(command)


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
    to_addr = args.email
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
    for token in args.tokens:
        print(get_thead(token), file=out_file)
        print(grep_logs(token, args.repo, get_from_sha())
              + "</table>", file=out_file)
    if args.email:
        if re.match(r'[^@]+@[^@]+\.[^@]+', args.email):
            send_email()
        else:  # TODO: raise this earlier
            raise Exception("Is your email address correct?")
    clean_up()


def clean_up():
    os.chdir(os.pardir)
    shutil.rmtree(os.path.join(os.getcwd(), repo_name))
    if not args.email:
        print("All cleaned up. See {0} for results.".format(out_file.name))
    else:
        print("An email was sent to {0}".format(args.email))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help='Github git repo URL')
    parser.add_argument('tokens', nargs='+',
                        help=('token [, token , ...]. A space separated list'
                              ' of tokens to search the repo for'))
    parser.add_argument('--email',
                        help='Email the results to the given email address.')
    parser.add_argument('--relative', action='store_true',
                        help=('This option will grep the repo relative to the '
                              ' last time it was run, creating a lasthead.txt '
                              ' file to keep track of this. This may be '
                              ' useful to run every 24 hours via CRON, etc.'))
    args = parser.parse_args()
    repo_name = get_repo_name(args.repo)
    date = datetime.datetime.now().strftime("%m-%d-%Y")
    out_file = open(repo_name + '.html', 'w+')
    clone_repo(args.repo)
    write_to_disk()
