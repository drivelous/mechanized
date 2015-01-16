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

def get_base_url(url):
	pieces = urlparse(url)
	return pieces.scheme + '://' + pieces.netloc

def get_filename(img_url):
	"""Takes image URL, parses, and eliminates excess filepath"""
	parsed = urlparse(img_url)
	return parsed.path.rstrip('/').split('/')[-1]

def download(dir_link, filename):
	"""Downloads image from dir_link giving it name filename"""
	f = open(filename, 'wb')
	f.write(urllib.urlopen(dir_link).read())
	f.close()

class Parse(object):

	def __init__(self, url):
		self.base_url = get_base_url(url)
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
		self.base_url = get_base_url(url)
		self.q = deque([self.base_url])
		self.visited = set([])
		self.images = set([])
		self.sources = ['src', 'data-src']

		try:
			self.directory = self.base_url.split('//')[1]
			os.makedirs(self.directory)
		except OSError:
			print "Directory %s exists. Setting as directory..." % self.directory

	def add_or_discard_links(self, links):
		for counter, link in enumerate(links, start=1):
			print "Link #" + str(counter)
			if not link.startswith('http'):
				print "Appending base URL to link ", link
				link = urljoin(self.base_url, link.replace(" ", ""))
			if get_base_url(link) != self.base_url:
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
		"""Downloads list of BeautifulSoup images"""
		
		for img_idx, img in enumerate(images):
			print "Image #" + str(img_idx + 1) + " of " + str(len(images))
			for src_idx, src in enumerate(self.sources):
				try:
					dir_link = img[src]
					if not dir_link.startswith('http'):
						dir_link = urljoin(self.base_url, dir_link.replace(" ", ""))
					if dir_link in self.images:
						print "This image has already been downloaded. Skipping...\n"
						break
					filename = get_filename(dir_link)
					filepath = os.path.join(self.directory, filename)
					download(dir_link, filepath)
					self.images.add(dir_link)
					print "Downloaded %s from %s\n" % (filename, dir_link)
					# Does not attempt next source - goes to next image
					break
				except KeyError as e:
					print "Does not have '%s' attribute" % src
					if src_idx + 1 < len(self.sources):
						print "Attempting '%s' attribute" % self.sources[src_idx + 1]
					else:
						print "Sources exhausted. Skipping download.\n"


	def process(self, url):
		page = Parse(url)
		images = page.return_images()
		links = page.return_hrefs()
		self.add_or_discard_links(links)
		self.download_or_discard_images(images)
		# print "self.q: ", self.q
		# self.add_or_discard_links(links)

	def go(self):
		while self.q:
			url = self.q.popleft()
			print "Currently on %s. Processing...\n\n" % url
			self.process(url)
			self.visited.add(url)

			# page = Parse(self.q.popleft())
			# images = page.return_images()
			# self.download_or_discard_images(images)
			# links = page.return_hrefs()
			# self.add_or_discard_links(links)
			# self.visited.add(page)

		print "Crawling finished! Wrapping up..."

def main():
	if len(sys.argv) > 1:
		url = sys.argv[1]
	else:
		try:
			url = raw_input('Enter starting URL: ')
		except (KeyboardInterrupt, EOFError):
			print "You didn't enter a URL to crawl. Aborting..."
			return
	if not url.startswith('http://') and \
		not url.startswith('ftp://'):
		url = 'http://%s/' % url

	mechanized = Crawler(url)
	mechanized.go()

if __name__ == '__main__':
	main()

