import bb2gh
import time

config_yaml = 'config.yaml'

for issue_id in range(190, 500):
    while True:
        try:
            bb2gh.migrate(config_yaml, verbose=True, issue_ids=[issue_id])
        except Exception as inst:
            print 'issue_id',issue_id
            print type(inst)
            print inst
            print 'waiting for 60 seconds'
            print
            time.sleep(60)
        else:
            break
        

