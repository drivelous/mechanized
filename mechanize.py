import os
import sys
import urllib
import time
from collections import deque
from urlparse import urlparse, urljoin

from BeautifulSoup import BeautifulSoup as bs

def get_base_url(url):
	"""Takes any URL and gets its base URL. Used to join
	paths that lack absolute paths"""

	pieces = urlparse(url)
	return pieces.scheme + "://" + pieces.netloc

def get_filename(img_url):
	"""Takes image URL, parses, and eliminates excess filepath"""

	parsed = urlparse(img_url)
	return parsed.path.rstrip("/").split("/")[-1]

def download(dir_link, filename):
	"""Downloads image from dir_link giving it name filename"""

	f = open(filename, 'wb')
	f.write(urllib.urlopen(dir_link).read())
	f.close()

class Parse(object):
	"""Takes URL's HTML content, turns it into BeautifulSoup
	object, and then returns all images and links"""

	def __init__(self, url):
		self.base_url = get_base_url(url)
		self.soup = self.soupify(url)

	def soupify(self, url):
		"""Turns an HTML page into a BeautifulSoup object"""

		html_content = urllib.urlopen(url).read()
		return bs(html_content)

	def return_hrefs(self):
		all_a_tags = self.soup.findAll('a')
		return [a_tag['href'] for a_tag in all_a_tags \
			if a_tag.has_key('href')]

	def return_images(self):
		return self.soup.findAll('img')

class Crawler(object):
	"""Keeps track of all links and files it comes across"""

	def __init__(self, url):
		self.base_url = get_base_url(url)
		self.q = deque([self.base_url])
		self.visited = set([])
		self.images = set([])
		self.sources = ['src', 'data-src', 'ng-src']
		self.ext = set(['.jpg', '.jpeg', '.gif', '.png', '.docx', '.doc',
						'.pdf', '.bmp'])

		try:
			self.directory = self.base_url.split('//')[1]
			os.makedirs(self.directory)
		except OSError:
			print "Directory %s exists. Setting as directory..." % self.directory

	def add_or_discard_links(self, links):
		"""Sanitizes, downloads, or discards each link
		from a BeautifulSoup object"""

		for counter, link in enumerate(links, start=1):
			print "Link #" + str(counter)
			link = link.replace(" ", "").lstrip("..").split("#")[0]
			if not link.startswith('http'):
				print "Appending base URL to link ", link
				link = urljoin(self.base_url, link)
			if get_base_url(link) != self.base_url:
				print "DISCARDED: ", link
				print "Not in same domain\n"
				continue
			if os.path.splitext(link)[1] in self.ext:
				print "Link to file. Processing..."
				self.process_file(link)
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
			print "New link! ", link
			print "Adding to queue...\n"

	def process_file(self, dir_link):
		"""Extracts filename from dir_link, derives filepath,
		downloads, and then saves link"""

		filename = get_filename(dir_link)
		filepath = os.path.join(self.directory, filename)
		download(dir_link, filepath)
		self.images.add(dir_link)
		print "Downloaded %s from %s\n" % (filename, dir_link)

	def download_or_discard_images(self, images):
		"""Downloads list of BeautifulSoup images"""
		
		for img_idx, img in enumerate(images, start=1):
			print "Image #" + str(img_idx) + " of " + str(len(images))
			for src_idx, src in enumerate(self.sources, start=1):
				try:
					dir_link = img[src]
					if not dir_link.startswith('http'):
						dir_link = urljoin(self.base_url, dir_link.replace(" ", ""))
					if dir_link in self.images:
						print "This image has already been downloaded. Skipping...\n"
						break
					else:
						self.process_file(dir_link)
						break # Does not attempt next source - goes to next image

				except KeyError as e:
					print "Does not have '%s' attribute" % src
					if src_idx < len(self.sources):
						print "Attempting '%s' attribute" % self.sources[src_idx]
					else:
						print "Sources exhausted. Skipping download.\n"


	def process(self, url):
		"""Extracts all content from one URL"""

		page = Parse(url)
		images = page.return_images()
		links = page.return_hrefs()
		self.add_or_discard_links(links)
		self.download_or_discard_images(images)

	def go(self):
		"""Processes all uncrawled links until empty"""
		
		retries = 0
		max_retries = 5
		while self.q:
			url = self.q[0]
			print "Visiting URL: ", url
			try:
				self.process(url)
				self.visited.add(self.q.popleft())
			except IOError as errMsg:
				retries += 1
				if retries == max_retries:
					print "Error threshold met. Quitting...\n"
					return

				print "(%d) There's an IOError. Check below." % retries
				print errMsg
				print "Let's wait this out a few seconds.\n"
				time.sleep(5)

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
	if not url.startswith('http') and \
		not url.startswith('ftp://'):
		url = 'http://%s/' % url

	mechanized = Crawler(url)
	mechanized.go()


if __name__ == '__main__':
	main()

