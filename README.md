GAE-PyDownloadCounter
=====================

Example file upload script in Python for Google App Engine with added download counter using the Datastore.


In order to run it you must first install the Goolge App Engine dev scripts.


1) run: dev_appserver.py ./gae-pydownloadcounter

2) Navigate with your browser to: http://localhost:8080

3) Upload a file (might have to click 'Refresh Form' after to have it appear in the list)

4) Click on the file link to download it.

5) Click 'Refresh Form' to have the download counter updated on the screen.

NOTE: For testing on your localhost the 'last IP' reported value will always be '::1'.  
  To see net-routable IPs listed you must deploy the app to GAE and try it there.
  
-EOF-
