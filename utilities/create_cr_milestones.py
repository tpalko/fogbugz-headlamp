from fogbugz import FogBugz
import sys
import os
import click
from ConfigParser import ConfigParser
from pytz import timezone

TZ = timezone('America/New_York')

months = [
	( "January", "01-01", "01-31" ),
	( "February", "02-01", "02-28" ),
	( "March", "03-01", "03-31" ),
	( "April", "04-01", "04-30" ),
	( "May", "05-01", "05-31" ),
	( "June", "06-01", "06-30" ),
	( "July", "07-01", "07-31" ),
	( "August", "08-01", "08-31" ),
	( "September", "09-01", "09-30" ),
	( "October", "10-01", "10-31" ),
	( "November", "11-01", "11-30" ),
	( "December", "12-01", "12-31" )
]

def run(fb, year, project):
	for (month, start, end) in months:
		try:
			sFixFor = "Maintenance/CR - %s %s" % (month, year)
			dtRelease_date = TZ.localize(datetime.strptime("%s-%s" % (year, start), "%Y-%m-%d"))
			dtStart_date = TZ.localize(datetime.strptime("%s-%s" % (year, end), "%Y-%m-%d"))

			dtRelease = "%s-%sT04:00:00Z" % (year, start)
			dtStart = "%s-%sT04:00:00Z" % (year, end)
			fb.newFixFor(
				ixProject=project,
				sFixFor=sFixFor,
				dtRelease=dtRelease,
				dtStart=dtStart,
				fAssignable="true"
			)
			fixfors = fb.listFixFors(ixProject=project)
			print fixfors
		except:
			print sys.exc_info()[1]

@click.command()
@click.option('--year', '-y', required=True, help='Ingest new music on disk.')
@click.option('--project', '-p', required=True, default='3', help='Ingest new music on disk.')
@click.option('--credentials_file', '-c', required=True, default=os.path.join(os.path.expanduser("~"), '.headlmp'), help='Path to credentials file (default ~/.headlmp)')
def main(year, project, credentials_file):
	config = ConfigParser()
	config.read(credentials_file)
	site = config.get('default', 'site')
	username = config.get('default', 'username')
	password = config.get('default', 'password')
	fb = FogBugz(site)
	fb.logon(username, password)
	run(fb, year, project)

if __name__ == '__main__':
	main()
