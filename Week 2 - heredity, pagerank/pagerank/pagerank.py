import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    linkCount = len(corpus.get(page))
    probs = dict.fromkeys(list(corpus.get(page)), 0)

    # If page has no links, assign equal probability to all pages
    if linkCount == 0:
        corpCount = len(corpus.keys())
        probs = dict.fromkeys(list(corpus))
        for key in probs:
            probs[key] = 1 / corpCount
        
        return probs

    # Distributing probability values
    distrib1 = damping_factor / linkCount
    distrib2 = (1 - damping_factor) / (linkCount + 1)

    # For each page, assign a distributed probability
    for key in probs:
        probs[key] += distrib1
    
    # Append the page itself into dictionary and distribute the random page probability
    probs[page] = 0
    for key in probs:
        probs[key] += distrib2

    return probs

    
def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize dictionary of page titles with values all at 0
    sampleDict = dict.fromkeys(list(corpus.keys()), 0)

    # Initialize function by picking random page first
    global nextPage
    nextPage = random.choice(list(corpus.keys()))

    # Reset counter
    N = 0

    # Go through loop n times
    while N < n:

        # Increase counter value for page in dictionary
        sampleDict[nextPage] += 1

        # Convert transition model dict to two lists
        pageArray = []
        probArray = []
        model = transition_model(corpus,nextPage,damping_factor)
        for page in model:
            pageArray.append(page)
            probArray.append(model.get(page))

        # Pick a page using weighted probabilities
        choices = random.choices(population=pageArray, weights=probArray)
        nextPage = choices[0]

        # Increase counter
        N += 1

    for key in sampleDict:
        sampleDict[key] = sampleDict.get(key) / n
    
    return sampleDict



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Assign equal probability to all pages initially
    pageDict = dict.fromkeys(list(corpus.keys()), 0)
    corpCount = len(corpus)
    for page in pageDict:
            pageDict[page] = 1 / corpCount

    # Flag used to exit loop
    flagA = 1
    while flagA:

        # Reset flagB for given loop
        flagB = 1

        # If all values are changing by less then 0.001, flagB stays put and loop ends
        for page in pageDict.keys():
            newValue = calculate_pagerank(corpus, pageDict, page, damping_factor)
            if abs(newValue - pageDict.get(page)) > 0.001:
                flagB = 0
            pageDict[page] = newValue
        
        # If flagB still standing, exit while loop
        if flagB == 1:
            flagA = 0

    return pageDict
    
def calculate_pagerank(corpus, pageRanks, page, damping_factor):
    """
    Return PageRank value for a single page.
    """

    # Collects all pages linking to "page" into a list
    linkTo = []
    for pages in corpus:
        if page in corpus.get(pages):
            linkTo.append(pages)
    
    # For each page linking to list, sum up pagerank value / link number
    pageSum = 0
    for pages in linkTo:
        linkNum = len(corpus.get(pages))
        pageSum += pageRanks.get(pages) / linkNum

    # Formula specified in project details
    pageRank = ((1 - damping_factor) / len(pageRanks)) + (damping_factor * pageSum)
    return pageRank


if __name__ == "__main__":
    main()
