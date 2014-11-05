import github
import random
import textwrap
import dateutil.parser

def parse_date(date):
    dateformat = "%m-%d-%Y at %H:%M"
    return dateutil.parser.parse(date).strftime(dateformat)

class GHissue(object):
    def __init__(self, bbissue, tokens, repo, user):
        self.title = bbissue.title
        self.body = bbissue.content
        if hasattr(bbissue, 'responsible'):
            self.assignee = bbissue.responsible['username']
        else:
            self.assignee = None
        self.milestone = bbissue.metadata['milestone']
        if bbissue.status == 'new':
            self.state = 'open'
        else:
            self.state = 'closed'
        self.labels = self.get_labels(bbissue)
        self.comments = bbissue.comments
        self.reporter = bbissue.reported_by['username']
        self.tokens = tokens
        self.url = '{0}/{1}'.format(user, repo)
        self.reporter_repo = self.get_repo(self.reporter)
        self.default_repo = self.get_repo()
        self.legacy_info = self.get_legacy_info(bbissue)

    def get_repo(self, user=None):
        token = self.tokens.get(user, self.tokens['default'])
        hub = github.Github(token)
        return hub.get_repo(self.url)
        
    def get_labels(self, bbissue):
        labels = [l for l in (bbissue.metadata['kind'], bbissue.metadata['component']) if l is not None]
        if bbissue.status in ['wontfix', 'duplicate', 'invalid']:
            labels.append(bbissue.status)
        return labels
        
    def create(self):
        for label in self.labels:
            self.create_label(label)
        gh_milestone = self.create_milestone(self.milestone)
        # gh_assignee = hub.get_user(self.assignee)
        extra_args = dict()
        if gh_milestone:
            extra_args['milestone'] = gh_milestone
        issue = self.reporter_repo.create_issue(self.title,
                                                body=self.body + self.legacy_info,
                                                **extra_args)
        issue.edit(state=self.state, labels=self.labels)
        for comment in self.comments[::-1]:
            self.create_comment(issue, comment)

    def create_comment(self, issue, comment):
        user = comment['author_info']['username']
        repo = self.get_repo(user)
        _issue = repo.get_issue(issue.number)
        _issue.create_comment(comment['content'] + self.get_comment_info(comment))

    def create_label(self, label):
        r = lambda: random.randint(0, 255)
        labels = [l.name for l in self.default_repo.get_labels()]
        if label not in labels:
            color = '%02X%02X%02X' % (r(),r(),r())
            print 'label',label
            print 'color',color
            self.default_repo.create_label(label, color)

    def create_milestone(self, milestone):
        gh_milestone = None
        for m in self.default_repo.get_milestones():
            if milestone == m._title.value:
                gh_milestone = m
        if not gh_milestone and milestone:
            gh_milestone = self.default_repo.create_milestone(milestone)
        return gh_milestone
    

    def __repr__(self):
        indent = 15
        width = 87
        ks = ['title', 'body', 'assignee', 'milestone', 'state', 'labels']
        d = self.__dict__
        linelist = []
        for k in ks:
            v = d[k]
            if k == 'labels':
                v = ', '.join(v)
            s_ = "{{k:<{indent}}}: {{v:<{width_}}}\n".format(indent=indent, width_=width - indent)
            if v:
                v = v.encode('utf-8')
            s_ = s_.format(k=k, v=v)
            s = textwrap.fill(s_,
                              subsequent_indent = ' ' * (indent + 2),
                              initial_indent='')
            linelist.append(s)
        return '\n'.join(linelist)


    
    def get_legacy_info(self, bbissue):
        fargs = bbissue.resource_uri.split('/')[-4:-2] + [bbissue.local_id]
        url = "https://bitbucket.org/{0}/{1}/issue/{2}".format(*fargs)
        issue_string = '[{0}]({1})'.format(bbissue.local_id, url)

        created = parse_date(bbissue.utc_created_on)
        modified = parse_date(bbissue.utc_last_updated)
        
        legacy_info = u"""
        \n\n _Imported from Bitbucket issue {issue_string},  created by {reporter} on {created}, last modified: {modified}_\n
        """.format(issue_string=issue_string,
                   reporter=bbissue.reported_by['username'],
                   created=created,
                   modified=modified)
        
        return legacy_info
        
    def get_comment_info(self, comment):
        created = parse_date(comment['utc_created_on'])
        reporter = comment['author_info']['username']
        
        legacy_info = u"""
        \n\n_Trac comment by {reporter} on {created}_\n
        """.format(reporter=reporter,
                   created=created)
        
        return legacy_info
