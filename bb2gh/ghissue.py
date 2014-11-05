import github
import random
import textwrap


class GHissue(object):
    def __init__(self, bbissue):
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

    def get_labels(self, bbissue):
        labels = [bbissue.metadata['kind'],
                  bbissue.metadata['component']]
        if bbissue.status in ['wontfix', 'duplicate', 'invalid']:
            labels.append(bbissue.status)
        return labels
        
    def create(self, token=None, user=None, repo=None):
        hub = github.Github(token)
        self.repo = hub.get_repo('{0}/{1}'.format(user, repo))
        for label in self.labels:
            self.create_label(label)
        gh_milestone = self.create_milestone(self.milestone)
        # gh_assignee = hub.get_user(self.assignee)
        extra_args = dict()
        if gh_milestone:
            extra_args['milestone'] = gh_milestone
        issue = self.repo.create_issue(self.title,
                                       body=self.body,
                                       **extra_args)
        issue.edit(state=self.state, labels=self.labels)
        for comment in self.comments[::-1]:
            issue.create_comment(comment['content'])

    def create_label(self, label):
        r = lambda: random.randint(0, 255)
        labels = [l.name for l in self.repo.get_labels()]
        if label not in labels:
            color = '%02X%02X%02X' % (r(),r(),r())
            self.repo.create_label(label, color)

    def create_milestone(self, milestone):
        gh_milestone = None
        for m in self.repo.get_milestones():
            if milestone == m._title.value:
                gh_milestone = m
        if not gh_milestone and milestone:
            gh_milestone = self.repo.create_milestone(milestone)
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
        
