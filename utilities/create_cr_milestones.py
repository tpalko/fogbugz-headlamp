from fogbugz import FogBugz
import sys

fb = FogBugz("https://palkosoftware.fogbugz.com")
fb.logon("tim@palkosoftware.com", "Ilmgitmn8")

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

for m in months:
	try:
		fb.newFixFor(ixProject=3, sFixFor="Maintenance/CR - %s 2017" % m[0], dtRelease="2017-%sT04:00:00Z" % m[2], dtStart="2017-%sT04:00:00Z" % m[1], fAssignable="true")
	except:
		print sys.exc_info()[1]
