import os

with open(os.path.join(os.getcwd(), 'private', 'headlmp', '.env'), 'rb') as envfile:
        lines = envfile.readlines()
        for l in lines:
                envvar, value = l.split('=')
                os.environ[envvar] = value.replace('\n', '')
                print "loaded %s=%s" %(envvar, value)

from webapp import app as application
