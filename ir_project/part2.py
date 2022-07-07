import copy
import math
from itertools import islice

from parsivar import *
import json

docs_content = []
docs_title = []
docs_url = []
positional_indexx = {}
doc_ranks = {}
phrase = []
champion = {}


def read_file():
    f = open('IR_data_news_12k.json', encoding='utf8')
    data = json.load(f)
    for i in data:
        docs_title.append(data[i]["title"])
        docs_content.append(data[i]["content"])
        docs_url.append(data[i]["url"])
    f.close()


def standard(data, i):
    normalizer = Normalizer()
    data = normalizer.normalize(data)
    tokenizer = Tokenizer()
    data_tokenized = tokenizer.tokenize_words(data)
    stemmer = FindStems()
    for j in range(len(data_tokenized)):
        data_tokenized[j] = stemmer.convert_to_stem(data_tokenized[j])
    data_tokenized = stopwords(data_tokenized)
    positional_index(data_tokenized, i)


def stopwords(data):
    stopword = ["با", "و", "در", "ولی", "اما", "نیز", "اگر", "که", "مگر", "از", "بر", "تا", "بی", "الا", "غیر", ".",
                ",", "،", ".", "/", "را", "مانند", "جزو", ":", "به", "؛"]
    for i in data:
        if i in stopword:
            data.remove(i)
    return data


def positional_index(tokenized, i):
    for j in range(len(tokenized)):
        data = tokenized[j]
        if data in positional_indexx:
            positional_indexx[data][0] = positional_indexx[data][0] + 1
            if i in positional_indexx[data][1]:
                positional_indexx[data][1][i].append(j)
            else:
                positional_indexx[data][1][i] = [j]
        else:
            positional_indexx[data] = []
            positional_indexx[data].append(1)
            positional_indexx[data].append({})
            positional_indexx[data][1][i] = [j]


def notIn(word):
    if word in positional_indexx.keys():
        for j in positional_indexx[word][1]:
            if j in doc_ranks.keys():
                doc_ranks.pop(j)


def phrasal(words):
    phrase = []
    for i in words:
        if i == '"':
            wordss = words[words.index(i) + 1:]
            phraseRank(phrase)
            return wordss
        else:
            phrase.append(i)


def positionCheck(phrases, docId, word, position):
    if len(phrases) == 2 and position not in positional_indexx[phrases[1]][1][docId]:
        return
    elif phrases.index(word) == len(phrases) - 1:
        doc_ranks[docId] += 1
        return
    elif position not in positional_indexx[word][1][docId]:
        return
    elif position in positional_indexx[word][1][docId]:
        positionCheck(phrases, docId, phrases[phrases.index(word) + 1], position + 1)


def phraseRank(phrase):
    docs_contentCopy = copy.deepcopy(docs_content)
    positional_indexCopy = copy.copy(positional_indexx)
    for i in phrase:
        if i not in positional_indexCopy.keys():
            return
    for i in list(positional_indexCopy.keys()):
        if i not in phrase:
            del positional_indexCopy[i]
    for i in range(len(docs_content)):
        for j in phrase:
            if i not in positional_indexCopy[j][1]:
                docs_contentCopy[i] = " "
    for i in positional_indexCopy:
        for j in list(positional_indexCopy[i][1]):
            if docs_contentCopy[j] == " ":
                del positional_indexCopy[i][1][j]
    for j in positional_indexCopy[phrase[0]][1]:
        if j not in doc_ranks:
            doc_ranks[j] = 0

        positionCheck(phrase, j, phrase[1], positional_indexCopy[phrase[0]][1][j][0] + 1)


def printDoc(docs):
    flag = 0
    print("\n\n\n\n\n\n")
    for i in docs.keys():
        if flag <= 5:
            print(docs_title[i] + ": " + docs_url[i])
            flag += 1
        else:
            break


def search(words):
    while len(words) != 0:
        if words[0] == '"':
            words = phrasal(words[1:])
        elif words[0] != '!' and words[0] != '"':
            normal = words.pop(0)
            normalWords(normal)
        else:
            words.pop(0)
            word = words.pop(0)
            notIn(word)
    for docs in list(doc_ranks.keys()):
        if doc_ranks[docs] == 0:
            del doc_ranks[docs]


def normalWords(normal):
    if normal in positional_indexx.keys():
        for j in positional_indexx[normal][1]:
            if j in doc_ranks.keys():
                doc_ranks[j] = doc_ranks[j] + len(positional_indexx[normal][1][j])
            else:
                doc_ranks[j] = len(positional_indexx[normal][1][j])


def tf_idf(positional_indexx):
    n = len(docs_content)
    for word in positional_indexx:
        temp = {}
        nt = len(positional_indexx[word][1])
        idf = math.log(n / nt, 10)
        for j in positional_indexx[word][1]:
            ftd = len(positional_indexx[word][1][j])
            tf = 1 + math.log(ftd, 10)
            positional_indexx[word][1][j].append(1 + math.log(ftd, 10))
            temp[j] = tf * idf
        sorted_temp = dict(sorted(temp.items(), key=lambda item: item[1], reverse=True))
        if word not in champion.keys():
            champion[word] = []
        if len(sorted_temp) <= 20:
            for i in sorted_temp.keys():
                champion[word].append(i)
        else:
            for i in islice(sorted_temp, 20):
                champion[word].append(i)

        positional_indexx[word].append(idf)


def tfidf_words(words):
    vec = {}
    scores = {}
    for word in words:
        if (word in positional_indexx.keys()):
            ftd = words.count(word)
            tf = 1 + math.log(ftd, 10)
            idf = positional_indexx[word][2]
            vec[word] = tf * idf
    for word in words:
        if word in positional_indexx.keys():
            for docId in champion[word]:
                if (docId not in scores.keys()):
                    scores[docId] = 0
                scores[docId] += positional_indexx[word][1][docId][1] * vec[word]
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    printDoc(sorted_scores)


read_file()

for i in range(len(docs_content)):
    standard(docs_content[i], i)

tf_idf(positional_indexx)
print(positional_indexx)

while (1):
    doc_ranks = {}
    query = input("write query: ")
    normalizer = Normalizer()
    tokenizer = Tokenizer()
    stemmer = FindStems()
    query = normalizer.normalize(query)
    words = tokenizer.tokenize_words(query)

    for j in range(len(words)):
        words[j] = stemmer.convert_to_stem(words[j])
    words = stopwords(words)
    tfidf_words(words)
