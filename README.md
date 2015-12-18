# Quik Strt

1. Fill out instance/config.py with appropriate information for your Fogbugz account
2. Install pip requirements:

		$ sudo pip install -r requirements.txt

3. Run the app

		$ python run.py

# Notes

* This application was originally written for Fogbugz API version 7, however my account has since been upgraded to API version 8, and everything seems to work fine.

# References

### Fogbugz 

http://help.fogcreek.com/8202/xml-api

http://help.fogcreek.com/8447/how-to-get-a-fogbugz-xml-api-token

* Note: manually obtaining a token is not necessary for this application - the 'fogbugz' Python module will manage your token, given a username and password. 

### Flask

http://flask.pocoo.org/docs/0.10/

### Jinja 

http://jinja.pocoo.org/