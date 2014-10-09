import json
import urllib2
from .BBissue import BBissue

bb_url = 'https://bitbucket.org/api/1.0/repositories/{accountname}/{repo_slug}/issues/{issue_id}'

    
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

def yield_bb_issues(accountname, repo_slug):
    count = jsonify(bb_url.format(accountname=accountname, repo_slug=repo_slug, issue_id=''))['count']
    for issue_id in range(count + 1):
        try:
            raw_issue = jsonify(bb_url.format(accountname=accountname, repo_slug=repo_slug, issue_id=issue_id))
        except urllib2.HTTPError:
            pass
        else:
            yield BBissue(**raw_issue)

__version__ = get_version()


