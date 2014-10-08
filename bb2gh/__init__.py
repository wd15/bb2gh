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

def bb_issues(accountname, repo_slug):
    issue_id = 1
    while True:
        url = bb_url.format(accountname=accountname, repo_slug=repo_slug, issue_id=issue_id)
        response = urllib2.urlopen(url)
        raw_issue = json.loads(response.read())
        yield BBissue(**raw_issue)
        issue_id += 1
    #     response = urllib2.urlopen(url)
    # except urllib2.HTTPError as ex:
    #     raise ValueError("Problem connecting to Bitbucket URL, {url}: {ex}".format(url=url, ex=ex))
    # raw_issues = json.loads(response.read())['issues']
    # for raw_issue in raw_issues:
    #     yield BBissue(**raw_issue)

__version__ = get_version()


