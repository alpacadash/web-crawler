import logging
import re
from urllib.parse import urlparse,urljoin
import lxml
from bs4 import BeautifulSoup
import collections
from collections import Counter

logger = logging.getLogger(__name__)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier, corpus):
        self.frontier = frontier
        self.corpus = corpus
        self.countStatic = collections.defaultdict(int)
        self.subdomainDict = collections.defaultdict(int)
        self.Maxlink = ('', 0)
        self.validURLs = []
        self.invalidURLs = []


    def writeTxt(self, filename, header, contents):
        f = open(filename, mode='w', encoding='utf8')
        f.write(header)
        if type(contents) is list:
            for item in contents:
                f.write(str(item) + "\n")
        elif type(contents) is tuple:
            f.write(str(contents[0]) + " " + str(contents[1]) + "\n")
        else:
            for key,value in contents.items():
                f.write(str(key) + ": " + str(value) + "\n")
        f.close()

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            self.validURLs.append(url)
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            url_data = self.corpus.fetch_url(url)

            for next_link in self.extract_next_links(url_data):
                if self.is_valid(next_link):
                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)

        self.writeTxt("subdomains.txt", "Subdomains:\n\n", self.subdomainDict)
        self.writeTxt("mostVisited.txt", "Most visited URLs:\n\n", self.Maxlink)
        self.writeTxt("downloadedURLs.txt", "", self.validURLs)
        self.writeTxt("traps.txt", "", self.invalidURLs)


    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """
        outputLinks = []

        soup = BeautifulSoup(url_data["content"], "lxml") # parsing
        tags = soup.find_all('a') # extracting
        for tag in tags:
            link = tag.get('href')
            if type(link) != type(None):
                link = urljoin(url_data["url"], link) #converting links to absolute links
                outputLinks.append(link)

        count = len(outputLinks) # statistics to check page with maximum links
        if self.Maxlink[1] < count:
            self.Maxlink = (url_data["url"], count)

        return outputLinks

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        parsed = urlparse(url)
        if parsed.hostname == None:
            return False

        if ".ics.uci.edu" in parsed.hostname:

            self.subdomainDict[parsed.netloc] += 1
            if parsed.scheme not in set(["http", "https"]):
                return False

            static_portion = url.split('?')[0]

            self.countStatic[static_portion] += 1
            if self.countStatic[static_portion] > 1000:
                self.invalidURLs.append(url)
                return False

            paths_split = parsed.path.split("/")
            word, freq = Counter(paths_split).most_common(1)[0]
            if freq > 12:
                self.invalidURLs.append(url)
                return False

        try:
            return ".ics.uci.edu" in parsed.hostname \
                   and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

        except TypeError:
            print("TypeError for ", parsed)
            return False
