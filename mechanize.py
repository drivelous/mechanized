import cStringIO
import formatter
from htmllib import HTMLParser
import httplib
import os
import sys
import urllib
import urlparse

from BeautifulSoup import BeautifulSoup as bs

def get_filename(img_url):
	"""Takes image URL, parses, and eliminates excess filepath"""
	parsed = urlparse.urlparse(img_url)
	return parsed.path.split('/')[-1]

def download(dir_link, filename):
	f = open(filename, 'wb')
	f.write(urllib.urlopen(dir_link).read())
	f.close()

def download_all_images(url):
	# open URL - check to see if http and www are in it - if not, append manually
	html_content = urllib.urlopen(url).read()
	html_soup = bs(html_content)
	all_imgs = html_soup.findAll('img')

	for img in all_imgs:
		try:
			dir_link = img['src']
		except KeyError as e:
			try:
				dir_link = img['data-src']
			except KeyError as e:
				print "Located image. Unable to localize src. Passing..."
		filename = get_filename(dir_link)
		download(dir_link, filename)
