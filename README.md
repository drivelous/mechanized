<h1>Mechanized</h1>

<p>Requires Python 2.5+ and uses BeautifulSoup 3.2.1</p>

<p>Mechanized is a web crawler that downloads all images it comes across from a given URL.</p>

<p>The Parse class takes a URL, turns the page into a BeautifulSoup object, and returns a list of all anchors and images.</p>

<p>The Crawler class queues up unique URLs within the same base domain, instantiates a Parse object with these URLs, and manages the logic of adding or discarding all links and images.</p>

<h3>Usage</h3>

<p>Simply call the script with a URL</p>

<pre><code>python mechanize.py <url here></code></pre>

<p>Mechanized downoads all images into a directory matching the name of the URL</p>

<h3>Future of Development</p>

<p>I probably won't be making any major improvements on this (EX: using a headless browser) but I am still curious about bugs that people come across as well as improvementst hat anyone makes. Send them to me at sean@drivelous.com.</p>
