import os

with open('.env', 'rb') as envfile:
	lines = envfile.readlines()
	for l in lines:
		envvar, value = l.split('=')
		os.environ[envvar] = value
		print "loaded %s=%s" %(envvar, value)

from webapp import app
from flask.ext.script import Manager, Server
from flask.ext.migrate import MigrateCommand

print "Starting server at one-twenty-seven-oh-oh-one:eighty-eighty.."
server = Server(host='127.0.0.1', port=8080)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', server)

manager.run()