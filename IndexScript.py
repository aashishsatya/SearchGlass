# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 22:44:39 2014

@author: aashishsatya
"""

import urllib2  # to download source codes of web pages

""" 
Some explanation is in order!! For this search engine we use a crawler 
that crawls a web page and returns two items - a graph and an index. 
The index will be a dictionary of the form
<keyword>: <list of urls>
which will help us answer a search query. The graph will also be a dictionary
of the form
<url>: <list of urls pointed to by that particular page>
which will help the crawler "crawl".
All of the functions defined below are precursors to our final aim - 
the search engine.
"""


def get_page(url):
    
    """
    Gets the HTML source from the url of a page.
    Input: url, a VALID url string
    Output: Another string that is the source of the webpage with
    url 'url'.
    Note: We've used library functions for this.
    """
    
    try:
        source_link = urllib2.urlopen(url)
    except:
        # some error has occured
        # so stop processing
        return None
    html_source = source_link.read()
    return html_source


def lookup(index, keyword):
    
    """
    Returns a list of web pages that contain the keyword.
    Input: index, a dictionary and keyword, a string.
    Output: A list of webpages that contain the keyword.
    """
    
    if keyword in index:
        return index[keyword]
    return []

def remove_tags(inputStr):
    
    """
    Function to remove tags and tag items in an HTML source file.
    Input: A string (HTML file) from which tags must be removed.
    Output: A list of words in the string with tags removed.
    """
    
    while '<' in inputStr:
        start = inputStr.find('<')
        end = inputStr.find('>', start)
        inputStr = inputStr[:start] + ' ' + inputStr[end + 1:]
    listOfWords = inputStr.split()
    return listOfWords    
    
# The built-in <string>.split() procedure works
# okay, but fails to find all the words on a page
# because it only uses whitespace to split the
# string. To do better, we should also use punctuation
# marks to split the page into words.

# Here we define a procedure, split_string, that takes two
# inputs: the string to split and a string containing
# all of the characters considered separators. The
# procedure returns a list of strings that break
# the source string up by the characters in the
# splitlist.

def splitStringList(source, delimiters = ' \\~!@#$%^&*()_+=-{}[]:";<>?,./*-'):
   
    """
    Function that splits the source into a list of words based on the 
    delimiters given in splitlist.
    Input: 'source', a LIST of words and 'delimiters', a STRING of
    delimiters upon which the source is to be split.
    Output: A list of words in HTML separated by the delimiters given.
    Note: It is better to have use remove_tags() and refine this
    source before this function is called.
    """
    
    if len(delimiters) == 0:
        return source
        
    # split source based on first delimiter
    totalList = source
    
    for delimiter in delimiters:
        # list to store new elements obtained from
        # splitting each word in totalList by every
        # delimiter
        tempList = []
        for word in totalList:
            # split the word based on the current delimiter
            testWords = word.split(delimiter)
            tempList += testWords
        totalList = tempList[:]
        
    # checking for empty strings:
    while '' in totalList:
        totalList.remove('')
    
    # checking for duplicates
    tempList = totalList[:]
    totalList = []
    for word in tempList:
        if word not in totalList:
            totalList.append(word)
            
    return totalList
    
def addPageToIndex(index, url, content):
    
    """
    Updates the index to include all of the word occurences
    found in the page content by adding the url to the word's
    associated url list.
    Input: 'index', a DICTIONARY, 'url', a string and 'content',
    an HTML source file)
    Output: We'll see.
    Combines most of the functions defined earlier.
    """
    
    # clean the source file, i.e. remove tags, and split
    # contents based on delimiters
    listOfKeywords = splitStringList(remove_tags(content))    
    
    # add words to index
    for keyword in listOfKeywords:
        if keyword in index:
            if url not in index[keyword]:
                # to avoid duplicating the url
                index[keyword].append(url)
        else:
            index[keyword] = [url]


def get_next_target(source):

    """
    Gets the next occurrence of an HTML url from another
    HTML source file
    Input: A valid HTML source text
    Output: Next available url(string), 'None' if there
    isn't any
    """
    
    trial = source.find('<a href="http')
    if trial == -1:
        # no occurrence of <a href=..>, so no link
        return None, 0
    start = source.find('"', trial)
    end = source.find('"', start + 1)
    url = source[start + 1: end]
    return url, end

def get_all_links(source):

    """
    Returns all available links from an HTML file.
    Input: 'source', an HTML source text
    Output: A list of all urls available in that page.
    Uses get_next_target().
    """
    
    links = []
    while '<a href="http' in source:
        url, endPosition = get_next_target(source)
        links.append(url)
        source = source[endPosition: ]
    return links