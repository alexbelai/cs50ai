import nltk
import sys
import os
import string
from collections import Counter
from numpy import log

FILE_MATCHES = 1
SENTENCE_MATCHES = 1
nltk.download('stopwords')

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)
    
    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)
    

def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    data = dict()

    # Change into directory folder
    path = os.path.join(os.getcwd(), directory)
    os.chdir(path)

    # Read each file and add data into dictionary
    for filename in os.listdir(path):
        with open(filename, encoding="utf8") as f:
            content = f.read()
            data[filename] = content
    
    return data


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    data = nltk.word_tokenize(document.lower())
    remove = list(string.punctuation) + nltk.corpus.stopwords.words("english") 
    processed = [word for word in data if word not in remove]

    return processed


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = dict()
    for filename in documents:
        for word in documents[filename]:
            if word not in idfs:
                value = calculate_idf(word, documents)
                idfs[word] = value

    return idfs
                


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    fileValues = []

    for filename in files:
        # Get count of every word in file text
        count = Counter(files[filename])
        value = 0

        # Calculate tf-idf of each query word for given file
        for word in query:
            tf = 0
            idf = idfs[word] if word in idfs else 0
            if word in count:
                tf += count[word]

            tfidf = tf * idf
            value += tfidf

        # Add file and corresponding sum to array
        fileValues.append([filename, value])   

    # Sort files according to sum of tf-idfs of query words
    fileValues.sort(key= lambda x: x[1])         

    # Return top 'n' elements of sorted list
    returnList = []
    for i in range(n):
        returnList.append(fileValues[i][0])

    return returnList



def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentenceValues = []
    for sentence in sentences:

        # Get words in sentence
        words = sentences[sentence]

        # Calculate sum of idfs of words from query and query term frequency for given sentence
        idfsum = 0
        qtf = 0
        for word in query:
            if word in words:
                idfsum += idfs[word] if word in idfs else 0
                qtf += 1

        # Calculate query term density
        qtd = qtf / len(words)

        # Add each sentence to array with corresponding data
        sentenceValues.append([sentence, idfsum, qtd])

    # Sort list according to idf sums, then query term density
    sentenceValues.sort(key=lambda x: (x[1], -x[2]))

    # Return top 'n' elements of sorted list
    returnList = []
    for i in range(n):
        returnList.append(sentenceValues[i][0])

    return returnList

def calculate_idf(word, documents):
    """
    Calculate idf of given word and return its value.
    """

    # Count the number of documents that contain given word
    appearances = 0
    for filename in documents:
        if word in documents[filename]:
            appearances += 1

    # Use idf formula to calculate
    idf = log(appearances / len(documents))
    return idf

if __name__ == "__main__":
    main()
