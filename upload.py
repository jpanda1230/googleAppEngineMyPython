#!/usr/bin/env python
# coding: utf-8

import os
import urllib
import logging

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import ndb

class DownloadCounter(ndb.Model):
    """Data model for the download counter"""
    blobkey = ndb.StringProperty(indexed=True)
    count_downloaded = ndb.IntegerProperty(indexed=False)
    last_ip = ndb.StringProperty(indexed=False)


class MainHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('<input type="button" value="Refresh Form" onClick="history.go(0)"><br /><br />')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit" name="submit" value="Submit"> </form></body></html>""")

        for b in blobstore.BlobInfo.all():
            last_ip = 'n/a'
            counter = 0
            entry = DownloadCounter.query( DownloadCounter.blobkey==str(b.key()) ).get()
            #logging.info("Got ENTRY: %s" % (entry))
            if (entry != None):
                counter = entry.count_downloaded
                last_ip = entry.last_ip
            self.response.out.write('<li><a href="/serve/%s' % str(b.key()) + '">' + str(b.filename) + '</a> Downloaded: '+ str(counter) +' times. Last from IP: '+ last_ip)


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        counter = DownloadCounter(blobkey=str(blob_info.key()), count_downloaded=0, last_ip='n/a')
        ckey = counter.put()
        logging.info("Uploaded: fname[%s] size[%s] user[%s] client_IP[%s] keys[%s] counter_key[%s]" % 
          (blob_info.filename, blob_info.size, users.get_current_user().email(), self.request.remote_addr, blob_info.properties(), ckey))
        self.redirect('/')


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key = str(urllib.unquote(blob_key))
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            blob = blobstore.get(blob_key)
            entry = DownloadCounter.query( DownloadCounter.blobkey==str(blob_key) ).get()
            if (entry != None):
                entry.count_downloaded += 1
                entry.last_ip = self.request.remote_addr
                key = entry.put() # resave it
            else:  # no entry for this file, create it
                counter = DownloadCounter(blobkey=str(blob_key), count_downloaded=1, last_ip=self.request.remote_addr)
                ckey = counter.put()
            logging.info("Downloaded: fname[%s] size[%s] client_IP[%s]" % (blob.filename, blob.size, self.request.remote_addr))
            self.send_blob(blobstore.BlobInfo.get(blob_key), save_as=True)



application = webapp.WSGIApplication(
          [('/', MainHandler),
           ('/upload', UploadHandler),
           ('/serve/([^/]+)?', ServeHandler),
          ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
  main()
