# Parse the text of a PR to extract other repos and branches
# that may depend or be dependent of the current PR, so that
# they can be built together
import re
import sys
import requests

URL_PATTERN = r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'

def main():
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        exit()
    res = re.search(f'[dD]epends[\n ]+(?:on[\n ]+)?[\n ]*((?:{URL_PATTERN}[\n ]*,*(:?and)?[\n ]*)*)', text)
    if not res:
        print('No linked PRs could be found, the current branch will be compiled with the master branches of other packages', file=sys.stderr)
        return []
    urls = re.findall(URL_PATTERN, res.groups()[0])
    ret = []
    for url in urls:
        ls = url.split('/')
        owner = ls[3]
        repo = ls[4]
        number = ls[6]
        response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}')
        if response.status_code == 403:
            print('Status code 403 when querying the Github API, most likely the maximum number of requests has been exceeded', file=sys.stderr)
            return []
        js = response.json()
        branch_repo = js['head']['repo']['name']
        branch_owner = js['head']['repo']['owner']['login']
        branch = js['head']['ref']
        ret.append(f'{branch_owner} {branch_repo} {branch}')
    return ret

if __name__ == '__main__':
    print('\n'.join(main()))
