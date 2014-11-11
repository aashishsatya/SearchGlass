"""
Script for SearchGlass' crawler.

Author: Aashish Satyajith
Developed during June 2014
"""

from IndexScript import *

def crawl_web(seed): # returns index, graph of inlinks
    tocrawl = [seed]
    crawled = []
    graph = {}  # <url>: [list of pages it links to]
    index = {}
    while tocrawl:
        page = tocrawl.pop()
        if page not in crawled:
            print 'Crawling', page, '...'
            content = get_page(page)
            if content == None:
                continue
            addPageToIndex(index, page, content)
            outlinks = get_all_links(content)
            graph[page] = outlinks
            for url in outlinks:
                # avoiding duplicates
                if url not in tocrawl and url not in crawled:
                    tocrawl.append(url)
            crawled.append(page)
    return index, graph


# Explanation of reciprocal links
# Thanks Udacity    
# One of the problems with our page ranking system is that pages can 
# collude with each other to improve their page ranks.  We consider 
# A->B a reciprocal link if there is a link path from B to A of length 
# equal to or below the collusion level, k.  The length of a link path 
# is the number of links which are taken to travel from one page to the 
# other.

# If k = 0, then a link from A to A is a reciprocal link for node A, 
# since no links needs to be taken to get from A to A.

# If k=1, B->A would count as a reciprocal link  if there is a link 
# A->B, which includes one link and so is of length 1 (it requires 
# two parties, A and B, to collude to increase each others page rank).

# If k=2, B->A would count as a reciprocal link for node A if there is
# a path A->C->B, for some page C, (link path of length 2),
# or a direct link A-> B (link path of length 1).

def checkLink(graph, start, destination, k):
    
    # I created this as a separate funtion because I thought it would
    # be useful in the future.
    # isReciprocal() can be directly implemented in itself.
    
    """
    Checks if there is a link from start to destination
    within a depth of k    
    Target: A link from start -> destination
    Input: A dictionary of the form <url>: [<urls linked to by page>],
    urls start and destination (strings) and k, the depth (an integer).
    Output: True or False as per whether there is a link from start to
    destination within a depth of k.
    """
    
   
    if k == 0:
        if start == destination:
            return True
        return False
            
    # takes care of the k = 1 case
    if destination in graph[start]:
        return True
        
    # check using checkLinks for all urls in the graph of start
    
    # variable reciprocal answers the question "Is the link reciprocal?"    
    reciprocal = False
    
    for url in graph[start]:
        reciprocal = checkLink(graph, url, destination, k - 1)
        if reciprocal:
            return True
    
    return False
    
def isReciprocal(graph, link1, link2, k):
    
    """
    Checks whether link1 is reciprocal to link2.
    start(link1) -> destination(link2) is reciprocal if there is a link
    destination(link2) -> start(link1) within a depth of k pages
    Input: A dictionary of the form <url>: [<urls linked to by page>],
    urls start and destination (strings) and k, an integer.
    Output: True or False as per whether there is a RECIPROCAL link from 
    start to destination within a depth of k.
    """
    
    return checkLink(graph, link2, link1, k)
    

def compute_ranks(graph, k = 0):
    
    """
    Computes the rank for pages in the graph using an algorithm
    similar to Google's PageRank
    Input: A dictionary of the form <url>: [<urls linked to by page>],
    and k, the allowed collusion level for checking reciprocal links.
    Output: A dictionary of the form <url>: rank of that page (float)
    """
    
    d = 0.8 # damping factor
    numloops = 10
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node] and not isReciprocal(graph, node, page, k):
                    newrank = newrank + d * (ranks[node]/len(graph[node]))
            newranks[page] = newrank
        ranks = newranks
    return ranks
    

def quickSort(allUrls, ranks):
    
    """
    Sorts allUrls by each url's ranks using Quick sort algorithm.
    Input: allUrls, the list of all pages and ranks, a dictionary
    containing elements of the form <url>: <rank of that url>
    Output: A list containing all the URLs in allUrls sorted by their
    rank.
    """
    
    if len(allUrls) <= 1:
        return allUrls
        
    # big, so start working
    # get pivot element
        
    pivotElement = allUrls.pop()
    smallerElements = []
    greaterElements = []
    for url in allUrls:
        if ranks[url] < ranks[pivotElement]:
            smallerElements.append(url)
        else:
            greaterElements.append(url)
    return quickSort(smallerElements, ranks) + [pivotElement] + quickSort(greaterElements, ranks) 
    

def ordered_search(index, ranks, keyword):
    
    """
    Performs a search for keyword 'keyword' in index 'index' and returns
    results sorted such that the page with the greatest rank comes first
    based on the ranks provided by 'ranks'.
    Input: Dicts index, ranks (see above) and a keyword
    Output: A list of URLs sorted descending based on their ranks.
    """
    
    allUrls = lookup(index, keyword)
    if not allUrls:
        return None
    # we now have a list of urls
    # sort it and return
    return quickSort(allUrls, ranks)
    


def searchQuery(index, graph, keyword):

    """
    Wrapper function (kind of) for ordered search
    Input: Dicts 'index', 'graph' and string 'keyword'
    Output: A list of URLs sorted descending based on their ranks.
    """

    ranks = compute_ranks(graph)
    return ordered_search(index, ranks, keyword)

index, graph = crawl_web('http://udacity.com/cs101x/urank/index.html')
print searchQuery(index, graph, 'hummus')

# useful url for testing: http://www.udacity.com/cs101x/index.html