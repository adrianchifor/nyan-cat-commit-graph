import datetime
import math
import itertools
import json

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import urlopen, HTTPError, URLError

TITLE = '''
+      o     +              o
    +             o     +       +
o          +
    o  +           +        +
+        o     o       +        o
-_-_-_-_-_-_-_,------,      o
_-_-_-_-_-_-_-|   /\_/\\
-_-_-_-_-_-_-~|__( ^ .^)  +     +
_-_-_-_-_-_-_-""  ""
+      o         o   +       o
    +         +
o        o         o      o     +
    o           +
+      +     o        o      +
'''

NYANCAT = [
[1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,4,4,4,4,0,4,0,0,4,0,0,0,0,0,0,0,3,0,0],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,2,2,3,2,4,1,4,4,1,4,0,0,0,0,0,3,2,3,0],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,4,1,4,2,3,2,2,2,4,1,1,1,1,4,0,0,0,0,3,2,1,2,3],
[2,2,2,2,1,1,1,1,2,2,2,2,1,1,1,1,2,2,2,2,1,4,4,4,4,2,2,2,3,4,1,4,1,1,4,1,4,0,0,0,3,1,1,1,3],
[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,4,4,4,2,3,2,2,4,3,1,4,4,1,3,4,0,0,0,3,2,1,2,3],
[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,4,4,4,4,4,4,4,4,4,4,4,4,0,0,0,0,0,3,2,3,0],
[0,0,0,0,2,2,2,2,0,0,0,0,2,2,2,2,0,0,0,0,1,1,1,1,4,0,0,4,0,0,0,0,4,0,4,0,0,0,0,0,0,0,3,0,0]]

def get_calendar(username, base_url='https://github.com/'):
    base_url = base_url + 'users/' + username

    try:
        url = base_url + '/contributions'
        page = urlopen(url)
    except (HTTPError, URLError) as e:
        print ("There was a problem fetching data from {0}".format(url))
        print (e)
        raise SystemExit

    return page.readlines()

def get_start_date():
    d = datetime.datetime.today()
    date = datetime.datetime(d.year-1, d.month, d.day, 12)
    weekday = datetime.datetime.weekday(date)

    while weekday < 6:
        date = date + datetime.timedelta(1)
        weekday = datetime.datetime.weekday(date)

    return date

def date_gen(start_date, offset=0):
    start = offset * 7
    for i in itertools.count(start):
        yield start_date + datetime.timedelta(i)

def values_in_date_order(image, multiplier=1):
    height = 7
    width = len(image[0])
    for w in range(width):
        for h in range(height):
            yield image[h][w]*multiplier

def commit(content, commitdate):
    template = ("""echo {0} >> nananananana\n"""
    """GIT_AUTHOR_DATE={1} GIT_COMMITTER_DATE={2} """
    """git commit -a -m "nananananana" > /dev/null\n""")

    return template.format(content, commitdate.isoformat(),
           commitdate.isoformat())

def create_sh(image, start_date, username, repo, offset=0, multiplier=1,
        git_url='git@github.com'):

    script = ('#!/bin/bash\n'
        'REPO={0}\n'
        'touch README.md\n'
        'git add README.md\n'
        'touch nananananana\n'
        'git add nananananana\n'
        '{1}\n'
        'git pull\n'
        'git push -u origin master\n')

    strings = []
    for value, date in zip(values_in_date_order(image, multiplier),
            date_gen(start_date, offset)):
        for i in range(value):
            strings.append(commit(i, date))

    return script.format(repo, "".join(strings), git_url, username)

def save(output, filename):
    file = open(filename, "w")
    file.write(output)
    file.close()

def main():
    print (TITLE)
    print ('Enter your GitHub username:')
    username = input("> ")

    output = set()
    for line in get_calendar(username):
        for day in line.decode().split():
            if "data-count=" in day:
                commit = day.split('=')[1]
                commit = commit.strip('"')
                output.add(int(commit))

    output = list(output)
    output.sort()
    output.reverse()

    print ('Enter name of the repo to be used for nyan cat commit graph art:')
    repo = input("> ")

    print ('Enter the number of weeks to offset nyan cat from the left:')
    offset = input("> ")

    if not offset.strip():
        offset = 0
    else:
        offset = int(offset)

    multiplier = 6
    output = create_sh(NYANCAT, get_start_date(), username, repo, offset, multiplier)

    save(output, 'generate_nyan_cat_commit_graph.sh')
    print ('\ngenerate_nyan_cat_commit_graph.sh saved.\n\n'
           'Create the new repo, clone it if you have to,\n'
           'cd into it and run generate_nyan_cat_commit_graph.sh.\n\n'
           'Make sure you have an SSH key set up on GitHub\n'
           'and the current branch is master on remote origin.\n')

if __name__ == '__main__':
    main()
