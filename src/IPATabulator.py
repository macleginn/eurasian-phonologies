#! /usr/bin/env python3

import sys
import re
from io import StringIO
from IPAParser import parsePhon

SERIES_FORMING_FEATURES = {'pre-glottalised', 'pre-aspirated', 'pre-aspirated', 'pre-nasalised', 'pre-labialised', 'pharyngealised', 'nasalised', 'labialised', 'velarised', 'faucalised', 'palatalised', 'half-long', 'long', 'creaky-voiced', 'breathy-voiced', 'lateral-released', 'rhotic', 'advanced-tongue-root', 'retracted-tongue-root'}

CONS_ROW_NAMES = ['plosive', 'implosive', 'nasal', 'trill', 'tap', 'lateral_tap', 'fricative', 'affricate', 'lateral_fricative', 'lateral_affricate', 'approximant', 'lateral_approximant']
CONS_COL_NAMES = ['bilabial', 'labial-velar', 'labial-palatal', 'labiodental', 'dental', 'alveolar', 'postalveolar', 'hissing-hushing', 'retroflex', 'alveolo-palatal', 'palatal', 'palatal-velar', 'velar', 'uvular', 'pharyngeal', 'glottal', 'epiglottal']

VOW_ROW_NAMES = ['close', 'near-close', 'close-mid', 'mid', 'open-mid', 'near-open', 'open']
VOW_COL_NAMES = ['front', 'near-front', 'central', 'near-back', 'back']

class Phoneme:
    """A phoneme unit consisting of a string representation and two frozensets of features.
    coreSet is used to draw a table; seriesSet is used to choose the appopriate table
    to put the phoneme in."""
    def __init__(self, phon, preSet, coreSet, postSet):
        self.phon      = phon
        self.coreSet   = coreSet
        self.seriesSet = frozenset(
            SERIES_FORMING_FEATURES.intersection(set.union(preSet, postSet))
            )
        self.coreSet.update(set.difference(set.union(preSet, postSet), self.seriesSet))
        self.coreSet = frozenset(self.coreSet)

    def __str__(self):
        return self.phon

    def summary(self):
        return self.phon + "\n" + ", ".join(set.union(set(self.coreSet), set(self.seriesSet)))

def makeTableCons(consList):
    """Transforms a list of consonant Phonemes into a 2-D array for subsequent formatting."""
    checkList = set(consList)
    pooledFeatures = set()
    for phon in consList:
        pooledFeatures.update(phon.coreSet)
    columns = [item for item in CONS_COL_NAMES if item in pooledFeatures]
    rows    = [item for item in CONS_ROW_NAMES if item in pooledFeatures]
    table   = [['' for i in range(len(columns) + 1)] for j in range(len(rows) + 1)]
    table[0][1:] = columns
    for i in range(1, len(table)):
        table[i][0] = rows[i - 1]
    for i in range(1, len(table)):
        for j in range(1, len(table[0])):
            temp = []
            for phon in consList:
                trimmed_set = set(phon.coreSet)
                if 'lateral_affricate' in trimmed_set:
                    trimmed_set.discard('affricate')
                if 'lateral_fricative' in trimmed_set:
                    trimmed_set.discard('fricative')
                if 'lateral_approximant' in trimmed_set:
                    trimmed_set.discard('approximant')
                if rows[i - 1] in trimmed_set and columns[j - 1] in trimmed_set:
                    checkList.discard(phon)
                    temp.append(str(phon))
            if temp:
                table[i][j] = ", ".join(sorted(temp))
    if checkList:
        raise Exception("Not all consonants made their way into the table: " + ", ".join([str(item) for item in checkList]))
    return table

def makeTableVow(vowList):
    checkList = set(vowList)
    pooledFeatures = set()
    for phon in vowList:
        pooledFeatures.update(phon.coreSet)
    columns = [item for item in VOW_COL_NAMES if item in pooledFeatures]
    rows    = [item for item in VOW_ROW_NAMES if item in pooledFeatures]
    table   = [['' for i in range(len(columns) + 1)] for j in range(len(rows) + 1)]
    table[0][1:] = columns
    for i in range(1, len(table)):
        table[i][0] = rows[i - 1]
    for i in range(1, len(table)):
        for j in range(1, len(table[0])):
            temp = []
            for phon in vowList:
                if rows[i - 1] in phon.coreSet and columns[j - 1] in phon.coreSet:
                    checkList.discard(phon)
                    temp.append(str(phon))
            if temp:
                table[i][j] = ", ".join(sorted(temp))
    if checkList:
        raise Exception("Not all vowels made their way into the table: " + ", ".join(checkList))
    return table

def convert2HTML(twoDArr):
    out = ["<table>\n"]
    for item in twoDArr:
        out.append("<tr>\n")
        for cell in item:
            out.append("    <td>" + cell + "</td>\n")
        out.append("</tr>\n")
    out.append("</table>\n\n")
    return "".join(out)

def convert2HTMLAndSpanify(twoDArr):
    out = ["<table>\n"]
    count = 0
    for item in twoDArr:
        out.append("<tr>\n")
        if count == 0:
            for cell in item:
                out.append("    <td>" + cell + "</td>\n")
            count += 1
        else:    
            for cell in item:
                new_cell = ', '.join(spanify(el) for el in cell.split(', '))
                out.append("    <td>" + new_cell + "</td>\n")
        out.append("</tr>\n")
    out.append("</table>\n\n")
    return "".join(out)

def processInventory(idiomName, phonoString, with_title):
    """A function that takes a string of comma separated phonemes and returns a <div>."""

    # Classifying phonemes: 
    # 0. Vowels vs. consonants
    # 1. Vowels:
    # 1.1. Monophthongs — with any combinations of secondary features.
    # Every combination of series-forming secondary features serves as a key in the dictionary.
    # All entries for this key are put into a separate table. The same procedure is applied to vowels.
    # 1.2. Diphthongs
    # 1.3. Triphthongs
    # 2. Consonants — with any combinations of secondary features.

    # print(idiomName) # For finding bugs in descriptions.

    # if idiomName.startswith("Santali"):
    #     print(phonoString)

    conClassDict  = {}
    vowClassDict  = {}
    diphthongs    = []
    triphthongs   = []
    consonants    = []
    vowels        = []
    apical_vowels = []

    inputPhons = re.split(r'\s*,\s*', phonoString)

    for phon in inputPhons:
        phoneme = Phoneme(phon, *parsePhon(phon))
        if 'consonant' in phoneme.coreSet:
            consonants.append(phoneme)
            if phoneme.seriesSet:
                classMarker = " & ".join(sorted(phoneme.seriesSet))
            else:
                classMarker = "plain"
            if classMarker in conClassDict:
                conClassDict[classMarker].append(phoneme)
            else:
                conClassDict[classMarker] = []
                conClassDict[classMarker].append(phoneme)
        elif 'vowel' in phoneme.coreSet:
            if 'diphthong' in phoneme.coreSet:
                diphthongs.append(phon)
            elif 'triphthong' in phoneme.coreSet:
                triphthongs.append(phon)
            elif 'apical' in phoneme.coreSet:
                apical_vowels.append(phon)
            else:
                vowels.append(phoneme)
                if phoneme.seriesSet:
                    classMarker = " & ".join(sorted(phoneme.seriesSet))
                else:
                    classMarker = "plain"
                if classMarker in vowClassDict:
                    vowClassDict[classMarker].append(phoneme)
                else:
                    vowClassDict[classMarker] = []
                    vowClassDict[classMarker].append(phoneme)
        else:
            raise ValueError("Neither a vowel nor a consonant: %s" % phon)

    out = StringIO()
    if with_title:
        out.write('<div class="phono_tables"><h1>%s</h1>' % (idiomName.split('#')[0]))
    if conClassDict:
        out.write("<h2>Consonants</h2>")
        keys = sorted(conClassDict.keys(), key = lambda x: len(x))
        for key in keys:
            out.write("<h3>" + key[0].upper() + key[1:] + " series:</h3>")
            out.write(convert2HTML(makeTableCons(conClassDict[key])))
    if vowClassDict:
        out.write("<h2>Vowels</h2>")
        keys = sorted(vowClassDict.keys(), key = lambda x: len(x))
        for key in keys:
            out.write("<h3>" + key[0].upper() + key[1:] + " series:</h3>")
            out.write(convert2HTML(makeTableVow(vowClassDict[key])))
    if apical_vowels:
        out.write("<h3>Apical vowels:</h3>")
        out.write("<p>" + ", ".join(str(el) for el in apical_vowels))
    if diphthongs:
        out.write("<h3>Diphthongs:</h3>")
        out.write("<p>" + ", ".join(str(el) for el in diphthongs))
    if triphthongs:
        out.write("<h3>Triphthongs:</h3>")
        out.write("<p>" + ", ".join(str(el) for el in triphthongs))
    if with_title:
        out.write('</div>')

    return out.getvalue()

def spanify(el):
    return '<span onclick="searchForThis(this)" class="hoverRed">' + str(el) + '</span>'

def tabulateAllSegments(phonoString):
    conClassDict  = {}
    vowClassDict  = {}
    diphthongs    = []
    triphthongs   = []
    consonants    = []
    vowels        = []
    apical_vowels = []

    inputPhons = re.split(r'\s*,\s*', phonoString)

    for phon in inputPhons:
        phoneme = Phoneme(phon, *parsePhon(phon))
        if 'consonant' in phoneme.coreSet:
            consonants.append(phoneme)
            if phoneme.seriesSet:
                classMarker = " & ".join(sorted(phoneme.seriesSet))
            else:
                classMarker = "plain"
            if classMarker in conClassDict:
                conClassDict[classMarker].append(phoneme)
            else:
                conClassDict[classMarker] = []
                conClassDict[classMarker].append(phoneme)
        elif 'vowel' in phoneme.coreSet:
            if 'diphthong' in phoneme.coreSet:
                diphthongs.append(phon)
            elif 'triphthong' in phoneme.coreSet:
                triphthongs.append(phon)
            elif 'apical' in phoneme.coreSet:
                apical_vowels.append(phon)
            else:
                vowels.append(phoneme)
                if phoneme.seriesSet:
                    classMarker = " & ".join(sorted(phoneme.seriesSet))
                else:
                    classMarker = "plain"
                if classMarker in vowClassDict:
                    vowClassDict[classMarker].append(phoneme)
                else:
                    vowClassDict[classMarker] = []
                    vowClassDict[classMarker].append(phoneme)
        else:
            raise ValueError("Neither a vowel nor a consonant: %s" % phon)
    out = StringIO()
    if conClassDict:
        out.write("<h2>Consonants</h2>")
        keys = sorted(conClassDict.keys(), key = lambda x: len(x))
        for key in keys:
            out.write("<h3>" + key[0].upper() + key[1:] + " series:</h3>")
            out.write(convert2HTMLAndSpanify(makeTableCons(conClassDict[key])))
    if vowClassDict:
        out.write("<h2>Vowels</h2>")
        keys = sorted(vowClassDict.keys(), key = lambda x: len(x))
        for key in keys:
            out.write("<h3>" + key[0].upper() + key[1:] + " series:</h3>")
            out.write(convert2HTMLAndSpanify(makeTableVow(vowClassDict[key])))
    if apical_vowels:
        out.write("<h3>Apical vowels:</h3>")
        out.write("<p>" + ", ".join(spanify(el) for el in apical_vowels))
    if diphthongs:
        out.write("<h3>Diphthongs:</h3>")
        out.write("<p>" + ", ".join(spanify(el) for el in diphthongs))
    if triphthongs:
        out.write("<h3>Triphthongs:</h3>")
        out.write("<p>" + ", ".join(spanify(el) for el in triphthongs))
    return out.getvalue()



# Test client
if __name__ == '__main__':
    phons = ','.join(['d', 'dz', 'kʰ', 'pʰ', 'ts', 'tsʰ', 'tʃʰ', 'tʰ', 'x', 'z', 'ʂ', 'ʃ', 'ʈʂʰ', 'ʒ'])
    div = processInventory("Diagnostic phonemes for cluster 1", phons, True)
    with open('test.html', 'w', encoding = 'utf-8') as out:
        out.write("""<html>
            <head>
            <title>%s</title>
            <meta charset="utf-8"/>
            <style>
            div.phono_tables table {
                border-collapse: collapse;
            }
            div.phono_tables td {
                border: 1px solid black;
                padding: 3px;
            }
            </style>
            </head>
            <body>
            %s
            </body>
            </html>""" % ("English alphabet", div))