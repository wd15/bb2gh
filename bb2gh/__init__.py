import json, yaml
import urllib2
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

def yield_bb_issues(user=None, repo=None):
    count = jsonify(bb_url.format(user=user, repo=repo, issue_id=''))['count']
    for issue_id in range(count + 1):
        try:
            raw_issue = jsonify(bb_url.format(user=user, repo=repo, issue_id=issue_id))
        except urllib2.HTTPError:
            pass
        else:
            yield BBissue(**raw_issue)

def migrate(config_yaml, verbose=False):
    with open(config_yaml, 'r') as f:
        config_data = yaml.load(f)
    for bitbucket_issue in yield_bb_issues(**config_data['bitbucket']):
        github_issue = GHissue(bitbucket_issue)
        github_issue.create(**config_data['github'])
        if verbose:
            print github_issue
        
__version__ = get_version()


