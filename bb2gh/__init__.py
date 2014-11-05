import json, yaml
import urllib2
import os


from .BBissue import BBissue
from .ghissue import GHissue


bb_url = 'https://bitbucket.org/api/1.0/repositories/{user}/{repo}/issues/{issue_id}'

def get_version():
    from pkg_resources import get_distribution, DistributionNotFound

    try:
        version = get_distribution(__name__).version
    except DistributionNotFound:
        version = "unknown, try running `python setup.py egg_info`"

    return version

def jsonify(url):
    response = urllib2.urlopen(url)
    return json.loads(response.read())

def yield_bb_issues(user=None, repo=None, issue_ids=None):
    if not issue_ids:
        count = jsonify(bb_url.format(user=user, repo=repo, issue_id=''))['count']
        issue_ids = range(count + 1)
        
    for issue_id in issue_ids:
        try:
            format_url = bb_url.format(user=user, repo=repo, issue_id=issue_id)
            raw_issue = jsonify(format_url)
            comments = jsonify(os.path.join(format_url, 'comments'))
        except urllib2.HTTPError:
            pass
        else:
            issue = BBissue(**raw_issue)
            issue.comments = comments
            yield issue

def migrate(config_yaml, verbose=False, issue_ids=None):
    with open(config_yaml, 'r') as f:
        config_data = yaml.load(f)
    for bitbucket_issue in yield_bb_issues(issue_ids=issue_ids, **config_data['bitbucket']):
        github_issue = GHissue(bitbucket_issue)
        github_issue.create(**config_data['github'])
        if verbose:
            print github_issue
        
__version__ = get_version()


