# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# This notebook is available on github [http://github.com/jseabold/web-scraping/](http://github.com/jseabold/web-scraping/)

# <headingcell level=4>

# Forecasting the Papal Conclave

# <markdowncell>

# * Based off the great work of David Masad. [@badnetworker](http://twitter.com/badnetworker) [His notebook](http://nbviewer.ipython.org/urls/raw.github.com/dmasad/Pope_Forecasting/master/Conclave_Modeling_Tutorial.ipynb).
# * Forecast how the Cardinals will vote for the next Pope
# * Assumption being that they will vote for the candidate most like themselves
# * Determine similarity of Cardinals by the "distance" between their wikipedia page
#   - Determining [similarity of text](http://en.wikipedia.org/wiki/Category:String_similarity_measures) is a common task in computational science

# <headingcell level=4>

# Useful Links

# <markdowncell>

# * [Dive into Python](http://www.diveintopython.net/) is a fantastic resource.
# 
# Modules needed:
# 
# * urllib2
# * lxml
# * urlencode
# * json

# <codecell>

URL = "http://en.wikipedia.org/wiki/Cardinal_electors_in_Papal_conclave,_2005"

# <markdowncell>

# [http://en.wikipedia.org/wiki/Cardinal_electors_in_Papal_conclave,_2005](http://en.wikipedia.org/wiki/Cardinal_electors_in_Papal_conclave,_2005)

# <headingcell level=4>

# Requests

# <headingcell level=5>

# What not to do

# <codecell>

#import urllib
#url = "http://en.wikipedia.org/wiki/Cardinal_electors_in_Papal_conclave,_2005"
#page = urllib.urlopen(url).read()

# <markdowncell>

# * Don't do this. It's inefficient, and it's rude.
# * Instead you want to send HTTP `Requests`
# * To do this, we'll use `urllib2`

# <codecell>

import urllib2

# <markdowncell>

# * First create a `Request` object.
# * Nothing is retrieved here.

# <codecell>

request = urllib2.Request(URL)

# <markdowncell>

# * We will want to add `request headers`
# * We could pass these to `Request` as a `dictionary`, though we will do so afterward below

# <markdowncell>

# * First we will define a `User-Agent`
# * A `User-Agent` lets the server know who the client is that's requesting a page and how to get in touch if something is amiss

# <codecell>

request.add_header("User-Agent", 
                   "WikiApiDemo/0.0 +http://jseabold.net")

# <markdowncell>

# * There are other headers you could define, but this is enough for our purposes

# <headingcell level=4>

# Retrieve the URL

# <markdowncell>

# * The next step is to build an opener. 
#   - This is optional but will allow us to handle redirects and errors though we do not here

# <codecell>

opener = urllib2.build_opener()

# <codecell>

page = opener.open(request)

# <codecell>

page.headers.dict

# <markdowncell>

# **Aside:** If you are building a client that may request the same page many times, you should look into `httplib2` which supports caching out of the box. It is also really easy to implement whatever custom backend for caching that you want.

# <headingcell level=4>

# Parsing HTML

# <markdowncell>

# * There are a few popular choices for parsing HTML, depending on what you need
# * There are a few [built-in options](http://docs.python.org/2/library/markup.html) like `HTMLParser` and `xml` modules
# * There is the third-party [`lxml`](http://lxml.de/) library
# * There is also the third-party [`Beautiful Soup`](http://www.crummy.com/software/BeautifulSoup/) library
#   - One of the big features of Beautiful Soup is that it handles malformed HTML intelligently.
#   - It also handles encodings explicitly. If you've ever worked with Unicode, you will appreciate this.
#   - It leverages `lxml` and `html5lib`
# * That said, we are going to use `lxml`

# <markdowncell>

# * We have our page, but how to get the links we want?
# * Pop over to [the page](http://en.wikipedia.org/wiki/Cardinal_electors_in_Papal_conclave,_2005) in your browser.
# * In Chrome, you can hit F12 to bring up the developer tools.
# * In Firefox, you will probably want to install [Firebug](http://getfirebug.com/) first. F12 will open Firebug.
# * In Chrome, click on Elements and hover over the HTML until you find the part that contains the source you want.
# * Right-click and `Copy XPath`
#   - The result wil be something like `"//*[@id="mw-content-text"]/ol[1]"`
# * In Firefox, click on HTML and do the same though you will select `Copy XPath`
#   - The result will be something like `"/html/body/div[3]/div[3]/div[4]/ol"`

# <markdowncell>

# * What in the world is this?
# * [XML](http://en.wikipedia.org/wiki/XML), or extensible markup language, defines a set of rules for making documents both machine and human readable.
#   - Many, many XML-based languages exist. This includes XHTML/HTML5.
# * [XPath](http://www.w3schools.com/xpath/xpath_syntax.asp) provides a way to select nodes in an XML document.
# * Unpacking `"//*[@id="mw-content-text"]/ol[1]"`
#   - `//` means select nodes that are either self or a descedant anywhere from self.
#   - `*` is the wildcard and matches any element node
#   - [@] selects attributes of nodes
#   - [1] denotes selecting the first element
#   - So this says get any node with id="mw-content-text" and grab it's first `<ol>` node.
# * Unpacking `"/html/body/div[3]/div[3]/div[4]/ol"`
#   - This is a bit clearer if you're familiar with html.
#   - These are just HTML tags in order of descendancy
#   - Note that this will grab every ol element at that level
# 
# Example:
#     
#     <html>
#     <body>
#       <div>...</div>
#       <div>...</div>
#       <div>
#         <div>...</div>
#         ...
#           ...
#           <div>
#             <ol>GRAB THIS</ol>

# <codecell>

from lxml import html

# <codecell>

xml_tree = html.parse(page)

# <codecell>

tables = xml_tree.xpath("/html/body/div[3]/div[3]/div[4]/ol")

# <markdowncell>

# At this point, I usually use trial and error, go back to the browser and look at the HTML source, or use the additional information in the developer tools to identify what I need.

# <codecell>

tables

# <codecell>

table = tables[0]

# <codecell>

row = table.xpath("li")[0]

# <codecell>

link = row.xpath("a[1]")[0]

# <codecell>

link.text, link.get("href")

# <codecell>

electors = []

for table in tables:
    for row in table.xpath('li'):
        # use star because of <b><a>
        link = row.xpath("a[1]|*/a[1]")[0]
        link.make_links_absolute()
        name = link.text
        href = link.get("href")
        electors.append(dict(name=name, url=href))

# <codecell>

assert len(electors) == 115

# <headingcell level=4>

# Wikipedia API and JSON

# <markdowncell>

# * We now have the name and links
# * We can get the information we really need using the [Wikipedia JSON API](http://en.wikipedia.org/w/api.php)
# * JSON is a text-based open standard for data exchange based on Javascript data structures
#   - It's an alternative to xml that's a bit easier on the eyes in my opinon

# <codecell>

from urllib import urlencode
import json

# <codecell>

WIKI_API_URL = "http://en.wikipedia.org/w/api.php"

# <codecell>

request = urllib2.Request(WIKI_API_URL)
request.add_header("User-Agent", 
                   "WikiApiDemo/0.0 +http://jseabold.net")

# <codecell>

request_params = {
        "action" : "parse",
        "format" : "json",
        "redirects" : "true",
         }

# <codecell>

print urlencode(request_params)

# <markdowncell>

# Let's take one example to be clear

# <codecell>

name, url = electors[0]["name"], electors[0]["url"]

# <codecell>

print url

# <markdowncell>

# We need the end of the URL.

# <codecell>

url = url.rsplit("/")[-1]

# <codecell>

print url

# <markdowncell>

# Update the `request_params` dict with the target `page`.

# <codecell>

request_params.update({"page" : url})

# <codecell>

data = urlencode(request_params)

# <codecell>

print data

# <codecell>

request = urllib2.Request(WIKI_API_URL, data)
page = opener.open(request)
json_page = page.read()

# <codecell>

print json_page[:200]

# <codecell>

json_obj = json.loads(json_page)

# <codecell>

type(json_obj)

# <codecell>

json_obj.keys()

# <codecell>

json_obj["parse"].keys()

# <codecell>

text = json_obj["parse"]["text"]
text = text["*"]

# <markdowncell>

# * Before we were able to parse the returned file-like object from `opener.open`.
# * Now we need to parse a string. 
# * These strings contain non-ascii characters (utf-8 in this case)
# * So we make a parser

# <codecell>

from lxml import etree

# <codecell>

parser = html.HTMLParser(encoding="utf-8")

# <codecell>

html_tree = etree.HTML(text, parser=parser)

# <codecell>

text = html_tree.text_content()

# <codecell>

print text[:480]

# <markdowncell>

# Let's go ahead and get them all, if we haven't already.

# <markdowncell>

# * We need to be aware of one thing. 
# * URLs like `Julián_Herranz_Casado` will be replaced with the URL encoded `Juli%C3%A1n_Herranz_Casado`.
# * We need to first `unquote` these before passing them to `urlencode`.

# <codecell>

from urllib2 import unquote

# <codecell>

print unquote('Juli%C3%A1n_Herranz_Casado')

# <codecell>

import os

# <codecell>

if not os.path.exists("./ElectorData05.json"):
    for elector in electors:
        name, url = elector["name"], elector["url"]
        url = url.rsplit("/")[-1]
        request_params.update({"page" : unquote(url)})
        data = urlencode(request_params)
        request = urllib2.Request(WIKI_API_URL, data)
        page = opener.open(request)
        json_obj = json.loads(page.read())
        text = json_obj["parse"]["text"]["*"]
        html_tree = etree.HTML(text, parser=parser)
        text = html_tree.text_content()
        elector["text"] = text
else:
    electors = json.load(open("./ElectorData05.json", "r"))

# <markdowncell>

# Save the data to disk using json. You could use the `pickle` module if you wanted to use a binary format.

# <codecell>

with open("ElectorData05.json", "wb") as json_out:
    json.dump(electors, json_out)

# <headingcell level=3>

# What Now?

# <markdowncell>

# * Clean the text and compute n-grams
# * Calculate TF-IDF
# * Decide on a vocabularly
# * Quantify text vectors
# * Compute distance metrics between the cardinals based on wiki page bios
# * Formulate a model for prediction for 2005 Conclave given we know the outcome
# * Forecast 2013 voting
# * We may explore this model in more detail in CSC-432, if there's sufficient interest.

# <headingcell level=3>

# Cleaning Text

# <headingcell level=4>

# Regular Expressions

# <markdowncell>

# * A regular expression, or regex, is a text string that describes a search pattern
# * Python has the [re](http://docs.python.org/2/library/re.html) module.
# * There is also the third-party [regex](https://pypi.python.org/pypi/regex) module
#   - This library has advantages if you need to work with Unicode character categories
#   - If we were properly to clean the Wikipedia pages, we would need to remove Unicode punctuation
#   - Apparently this is supposed to become part of the standard library, but I don't know the status of this
# * Let's look at some examples to get the idea of regex

# <codecell>

import re

# <headingcell level=5>

# A Simple Example

# <markdowncell>

# The simplest regular expressions are plain characters

# <codecell>

text1 = "Moby Dick by Herman Melville"
text2 = "Vaudeville"

# <markdowncell>

# Matches return a match object.

# <codecell>

re.search("ville", text1)

# <codecell>

search = re.search("ville", text1)

# <markdowncell>

# Match objects have a group method.

# <codecell>

search.group()

# <codecell>

re.search("ville", text2)

# <markdowncell>

# Non-matches return `None`.

# <codecell>

re.search("Maude", "Vaudeville")

# <headingcell level=5>

# A little more complicated

# <markdowncell>

# Regular expressions may also contain special characters.

# <codecell>

text3 = "manners"

# <codecell>

text4 = "mandolin"

# <markdowncell>

# The character `\w` is a special character that matches any alphanumeric character and the underscore.

# <codecell>

re.search("man\w", text1)

# <codecell>

re.search("man\w", text3).group()

# <codecell>

re.search("man\w", text4).group()

# <markdowncell>

# Another special character is `.` which matches any character except a newline character.

# <codecell>

re.search("man.", text1).group()

# <codecell>

re.search("man.", text3).group()

# <markdowncell>

# You can escape the special characters with a `\`, so that `\.` would match a period.

# <codecell>

re.search("street\.", "Main street.").group()

# <markdowncell>

# `[]` is used to indicate a set of characters. For instances `[amk]` will match a, m, or k.

# <codecell>

re.search("Mar[atk]", "Mart").group()

# <codecell>

re.search("Mar[atk]", "Mark").group()

# <codecell>

re.search("Mar[atk]", "Mara").group()

# <codecell>

re.search("Mar[atk]", "Mars")

# <markdowncell>

# We can use what we know so far to strip out punctuation using the `re.sub` function.

# <codecell>

pattern = "[%s]" % re.escape(".,'")

# <codecell>

print pattern

# <codecell>

re.sub(pattern, "", "Hello, ma'am.")

# <markdowncell>

# We can also make sure we strip out unicode by using the `flags` argument. For example, our first text has unicode spaces (`\xa0`) in it. The special character for whitespace is `\s` this matches any whitespace character including `[ \t\n\r\f\v]`. With the `UNICODE` flag set it also matches any character designated as whitespace in the Unicode character properties database.

# <codecell>

electors[0]["text"][:64]

# <codecell>

re.sub("\s", " ", electors[0]["text"][:64], flags=re.UNICODE)

# <markdowncell>

# The last special character we will want to know about is `+`. `+` matches 1 or more of the preceding characters.

# <codecell>

re.sub(" +", " ", "This   has      a lot of    repeated spaces")

# <markdowncell>

# * Now we're going to use this to make a function to strip out all of the punctation from our text. 
# * We can get all of the ASCII punctuations from the `string` module.

# <codecell>

import string

# <codecell>

print string.punctuation

# <codecell>

punc_pattern = "[%s]" % re.escape(string.punctuation)

# <codecell>

space_pattern = "\s+"

# <codecell>

def clean_text(text, punc_pattern, space_pattern):
    text = re.sub(punc_pattern, "", text)
    text = re.sub(space_pattern, " ", text, flags=re.UNICODE)
    text = re.sub("\d+", "", text)
    # some cruft I saw ex post
    # could use regex to get unicode across the board
    text = re.sub(u"\u2014", "", text)
    return text

# <codecell>

for elector in electors:
    text = clean_text(elector["text"], punc_pattern, space_pattern)
    elector.update({"text" : text})

# <headingcell level=4>

# Remove Stop Words

# <codecell>

dates = ["january", "february", "march", "april", "may", "june", "july", "august",
         "september", "october", "november", "december", "monday", "tuesday", 
         "wednesday", "thursday", "friday", "saturday", "sunday"]

try:
    from nltk.corpus import stopwords
    all_stopwords = stopwords.words("english") 
except:
    all_stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 
        'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 
         'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 
         'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 
         'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 
         'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 
         'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
         'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 
         'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
         'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 
         'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 
         'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 
         'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'edit',
         'disambiguation']
all_stopwords += ["edit", "disambiguation"] 
all_stopwords += dates

# <codecell>

def remove_stop_words(x, stop_words):
    """
    Creates a regex for all the stop words and then removes them from the text.

    \b matches the empty string but only at the beginning and end of words.
    """
    stop_words_regex = r'\b%s\b' % r'\b|\b'.join(stop_words)
    x = re.sub(stop_words_regex, "", x, flags=re.UNICODE)
    return x

# <codecell>

def count(text):
    """
    Generator that yields the unigrams, bigrams, and trigrams in a single
    space separated string from a given text.
    """
    words = text.split()
    for i in range(len(words)-2):
        yield words[i], 1
        yield ' '.join(words[i:i+2]), 1 
        yield ' '.join(words[i:i+3]), 1
    # yield that last bi-gram and last 2 uni-grams
    if len(words) > 1:
        yield ' '.join(words[-2:]), 1
        yield words[-2], 1
        yield words[-1], 1

# <codecell>

from itertools import groupby
import operator

def key(k_v):
    return k_v[0]

def kvgroup(kviter):
    """
    Copy of the function from disco.utils

    Group the values of consecutive keys which compare equal.

    Takes an iterator over ``k, v`` pairs,
    and returns an iterator over ``k, vs``.
    Does not sort the input first.
    """
    for k, kvs in groupby(kviter, key):
        yield k, (v for _k, v in kvs)
        
def combine(counts):
    for word, count in kvgroup(sorted(counts)):
        yield word, sum(count)

# <codecell>

for elector in electors:
    text = elector["text"]
    text = text.lower()
    cleaned_text = remove_stop_words(text, all_stopwords)
    elector["text_vector"] = dict(i for i in combine(count(cleaned_text)))

# <codecell>

elector["text_vector"]

# <codecell>

def jaccard_similarity(vector1, vector2):
    '''
    Compute Jaccard Similarity between two sparse vectors,
    represented as dicts.
    '''
    # checking for set membership is fast
    keys1 = set(vector1.keys())
    keys2 = set(vector2.keys())
    all_keys = keys1.union(keys)
    union = len(all_keys)
    intersection = 0.
    for key in all_keys:
        if key in vector1 and key in vector2:
            intersection += 1.
    return intersection / union

