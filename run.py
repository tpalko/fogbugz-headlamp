from webapp import app
from flask.ext.script import Manager, Server
from flask.ext.migrate import MigrateCommand

server = Server(host='127.0.0.1', port=8080)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', server)

manager.run()