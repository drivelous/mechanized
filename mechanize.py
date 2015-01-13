import cStringIO
import formatter
from htmllib import HTMLParser
import httplib
import os
import sys
import urllib
from collections import deque
from urlparse import urlparse, urljoin

from BeautifulSoup import BeautifulSoup as bs

# TODO:
# Parse:
# -Parse all a tags, return all a tags to crawler, and check if each is in a set
# -Parse all images on a soupified page, check if those filenames have been downloaded
# -Visit next page

def get_filename(img_url):
	"""Takes image URL, parses, and eliminates excess filepath"""
	parsed = urlparse(img_url)
	return parsed.path.split('/')[-1]

def download(dir_link, filename):
	"""Downloads image from dir_link giving it name filename"""
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


class Parse(object):

	def __init__(self, url):
		self.soup = self.soupify(url)

	def soupify(self, url):
		html_content = urllib.urlopen(url).read()
		return bs(html_content)

	def return_hrefs(self):
		all_a_tags = self.soup.findAll('a')
		return [a_tag['href'] for a_tag in all_a_tags \
			if a_tag.has_key('href')]

	def return_images(self):
		return self.soup.findAll('img')

class Crawler(object):

	def __init__(self, url):
		self.base_url = self.get_base_url(url)
		self.q = deque([])
		self.visited = set([])
		self.images = set([])

	def get_base_url(self, url):
		pieces = urlparse(url)
		return pieces.scheme + '://' + pieces.netloc

	def add_or_discard_links(self, links):
		for counter, link in enumerate(links, start=1):
			print "Link #" + str(counter)
			if not link.startswith('http'):
				print "Appending base URL to link ", link
				link = urljoin(self.base_url, link)
			if self.get_base_url(link) != self.base_url:
				print "DISCARDED: ", link
				print "Not in same domain\n"
				continue
			if link.startswith('mailto:'):
				print "DISCARDED: ", link
				print "mailto link\n"
				continue
			if link in self.visited:
				print "DISCARDED: ", link
				print "Already visited\n"
				continue
			if link in self.q:
				print "DISCARDED: ", link
				print "Already in queue\n"
				continue

			self.q.append(link)
			print "ADDED: ", link
			print "New link! Adding to queue...\n"

	def download_or_discard_images(self, images):
		
		sources = ['src', 'data-src']

		for img_idx, img in enumerate(images):
			print "Image #" + str(img_idx + 1) + " of " + str(len(images))
			for src_idx, src in enumerate(sources):
				try:
					dir_link = img[src]
					filename = get_filename(dir_link)
					download(dir_link, filename)
					self.images.add(dir_link)
					print "Downloaded %s from %s\n" % (filename, dir_link)
					# Does not attempt next source - goes to next image
					break
				except KeyError as e:
					print "Does not have '%s' attribute" % src
					if src_idx + 1 < len(sources):
						print "Attempting '%s' attribute" % sources[src_idx + 1]
					else:
						print "Sources exhausted. Skipping download.\n"


	def process(self):
		#TODO: process starts on base_url -- should  be called by
		#unwritten method go() on every page processed in self.q
		page = Parse(self.base_url)
		images = page.return_images()
		links = page.return_hrefs()
		self.download_or_discard_images(images)
		#self.add_or_discard_links(links)



