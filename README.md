# key4hep-dev-utils
Utilities for development of the key4hep stack

# Default files
In `/defaults` there is a set of files that are used across the key4hep
repositories like, for example, a `.gitignore` file. Changes to those files
should not be made individually in each repository but here instead and then the
changes pushed to all of them.

# Utilities

## Syncing to many repos

There is a script to commit and push files to many repositories. The script is
called `sync-files.sh` and will pick up all the repositories in
`get_packages.sh` (currently all the ones with `CMakeLists.txt` that are not
archived).

## Github rulesets

To update the github rulesets for many repositories go to `scripts` and run
`./update-all update-ruleset.sh`. To update the default ruleset used the easiest
way is to create one in Github, export it and then overwrite the json file
`defaults/github/default-branch-ruleset.json`.

## Github repository settings

Similarly to the rulesets, run `./update-all update-github-settings.sh`

# Running the tests

## Troubleshooting

### Code 403 on requests
The Github REST API limits the number of requests that can be made. For an
unauthenticated user it's 60 per hour so it's likely this is the case if you
have run the tests a few times.
Run `curl -i https://api.github.com/users/octocat`. If the limit is hit something like this will be shown:
```
...
x-ratelimit-limit: 60
x-ratelimit-remaining: 0
x-ratelimit-reset: 1676361860
x-ratelimit-resource: core
x-ratelimit-used: 60
content-length: 280
x-github-request-id: 9506:1A1C:F7D0CD:FCC1BE:63EB3C83

{"message":"API rate limit exceeded for XXX.XXX.XXX.XX. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"}
```

The best way to solve this is to [create a github token][https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token]. And then adding an `auth` field to the request:
``` python
    response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}', auth=(user, token))
```
