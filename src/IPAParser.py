#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time

# All base glyphs.

MAIN_GLYPHS = {'ɿ', 'ʅ', 'ʮ', 'ʯ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'ɡ', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'æ', 'ç', 'ð', 'ø', 'ħ', 'ŋ', 'œ', 'ɐ', 'ɑ', 'ɒ', 'ɓ', 'ɔ', 'ɕ', 'ᶑ', 'ɖ', 'ɗ', 'ɘ', 'ə', 'ɛ', 'ɜ', 'ɞ', 'ɟ', 'ɠ', 'ɢ', 'ɣ', 'ɤ', 'ɥ', 'ɦ', 'ɨ', 'ɪ', 'ɬ', 'ɭ', 'ɮ', 'ɯ', 'ɰ', 'ɱ', 'ɲ', 'ɳ', 'ɴ', 'ɵ', 'ɶ', 'ɸ', 'ɹ', 'ɺ', 'ɻ', 'ɽ', 'ɾ', 'ʀ', 'ʁ', 'ʂ', 'ʃ', 'ʄ', 'ʈ', 'ʉ', 'ʊ', 'ʋ', 'ʌ', 'ʍ', 'ʎ', 'ʏ', 'ʐ', 'ʑ', 'ʒ', 'ʔ', 'ʕ', 'ʙ', 'ʛ', 'ʜ', 'ʝ', 'ʟ', 'ʡ', 'ʢ', 'β', 'θ', 'χ', 'ɚ', 'ɫ', '\u026a\u0308', '\u028a\u0308', '\xe4', '\xf8\u031e', 'e\u031e', '\u0264\u031e', 'o\u031e', 'ƺ', 'ʓ', 'ɧ'}

# Consonants by manner.

PLOSIVES = {'b', 'c', 'd', 'g', 'ɡ', 'k', 'p', 'q', 't', 'ɖ', 'ɟ', 'ɢ', 'ʈ', 'ʔ', 'ʡ'}
IMPLOSIVES = {'ɓ', 'ɗ', 'ɠ', 'ʄ', 'ʛ', 'ᶑ'}
NASALS = {'m', 'n', 'ŋ', 'ɱ', 'ɲ', 'ɳ', 'ɴ'}
TRILLS = {'r', 'ʀ', 'ʙ'}
TAPS = {'ɽ', 'ɾ'}
LATERAL_TAPS = {'ɺ'}
FRICATIVES = {'f', 'h', 's', 'v', 'x', 'z', 'ç', 'ð', 'ħ', 'ɕ', 'ɣ', 'ɦ', 'ɸ', 'ʁ', 'ʂ', 'ʃ', 'ʐ', 'ʑ', 'ʒ', 'ʕ', 'ʜ', 'ʝ', 'ʢ', 'β', 'θ', 'χ', 'ƺ', 'ʓ', 'ɧ'}
LATERAL_FRICATIVES = {'ɬ', 'ɮ'}
APPROXIMANTS = {'j', 'w', 'ɥ', 'ɰ', 'ɹ', 'ɻ', 'ʋ', 'ʍ'}
LATERAL_APPROXIMANTS = {'l', 'ɫ', 'ɭ', 'ʎ', 'ʟ'}

MANNERS = [PLOSIVES, IMPLOSIVES, NASALS, TRILLS, TAPS, LATERAL_TAPS, FRICATIVES, LATERAL_FRICATIVES, APPROXIMANTS, LATERAL_APPROXIMANTS]
MANNERS_NAMES = ['plosive', 'implosive', 'nasal', 'trill', 'tap', 'lateral_tap', 'fricative', 'lateral_fricative', 'approximant', 'lateral_approximant']
ALL_CONSONANTS = set.union(*MANNERS)

# Voiced consonants.

VOICED = {'b', 'd', 'g', 'ɡ', 'j', 'l', 'm', 'n', 'r', 'v', 'w', 'z', 'ð', 'ŋ', 'ɓ', 'ᶑ', 'ɖ', 'ɗ', 'ɟ', 'ɠ', 'ɢ', 'ɣ', 'ɥ', 'ɦ', 'ɭ', 'ɮ', 'ɰ', 'ɱ', 'ɲ', 'ɳ', 'ɴ', 'ɹ', 'ɺ', 'ɻ', 'ɽ', 'ɾ', 'ʀ', 'ʁ', 'ʄ', 'ʎ', 'ʐ', 'ʑ', 'ʒ', 'ʙ', 'ʛ', 'ʝ', 'ʟ', 'ʢ', 'β', 'ɫ', 'ʓ', 'ʕ'}

# Consonants by place.

BILABIAL = {'b', 'm', 'p', 'ɸ', 'ʙ', 'β', 'ɓ'}
LABIAL_VELAR = {'w', 'ʍ'}
LABIAL_PALATAL = {'ɥ'}
LABIODENTAL = {'f', 'v', 'ɱ', 'ʋ'}
INTERDENTAL = {'ð', 'θ'}
ALVEOLAR = {'ɗ', 'ɹ', 'ɾ', 'ɮ', 'ɬ', 'r', 't', 'n', 'ɫ', 'l', 'd', 's', 'z', 'ɺ'}
POSTALVEOLAR = {'ʃ', 'ʒ'}
HISSING_HUSHING = {'ƺ', 'ʓ'} # ŝ and ẑ are automatically converted to these symbols.
RETROFLEX = {'ɖ', 'ɭ', 'ɳ', 'ɻ', 'ɽ', 'ʂ', 'ʈ', 'ʐ', 'ᶑ'}
ALVEOLO_PALATAL = {'ɕ', 'ʑ'}
PALATAL = {'c', 'j', 'ç', 'ɟ', 'ɲ', 'ʎ', 'ʝ', 'ʄ'}
PALATAL_VELAR = {'ɧ'}
VELAR = {'g', 'ɡ', 'k', 'x', 'ŋ', 'ɣ', 'ɰ', 'ʟ', 'ɠ'}
UVULAR = {'q', 'ɢ', 'ɴ', 'ʀ', 'ʁ', 'χ', 'ʛ'}
PHARYNGEAL = {'ħ', 'ʕ'}
GLOTTAL = {'ʔ', 'h', 'ɦ'}
EPIGLOTTAL = {'ʜ', 'ʢ', 'ʡ'}

PLACES = [BILABIAL, LABIAL_VELAR, LABIAL_PALATAL, LABIODENTAL, INTERDENTAL, ALVEOLAR, POSTALVEOLAR, HISSING_HUSHING, RETROFLEX, ALVEOLO_PALATAL, PALATAL, PALATAL_VELAR, VELAR, UVULAR, PHARYNGEAL, GLOTTAL, EPIGLOTTAL]
PLACES_NAMES = ['bilabial', 'labial-velar', 'labial-palatal', 'labiodental', 'interdental', 'alveolar', 'postalveolar', 'hissing-hushing', 'retroflex', 'alveolo-palatal', 'palatal', 'palatal-velar', 'velar', 'uvular', 'pharyngeal', 'glottal', 'epiglottal']

# Vowels by openness.

CLOSE = {'i', 'u', 'y', 'ɨ', 'ɯ', 'ʉ'}
NEAR_CLOSE = {'ɪ', 'ɪ\u0308', 'ʊ', 'ʊ\u0308', 'ʏ'}
CLOSE_MID = {'e', 'o', 'ø', 'ɘ', 'ɤ', 'ɵ'}
MID = {'e\u031e', 'o\u031e', 'ø\u031e', 'ə', 'ɚ', 'ɤ\u031e'}
OPEN_MID = {'œ', 'ɔ', 'ɛ', 'ɜ', 'ɞ', 'ʌ'}
NEAR_OPEN = {'æ', 'ɐ'}
OPEN = {'a', 'ä', 'ɑ', 'ɒ', 'ɶ'}

OPENNESS = [CLOSE, NEAR_CLOSE, CLOSE_MID, MID, OPEN_MID, NEAR_OPEN, OPEN]
OPENNESS_NAMES = ['close', 'near-close', 'close-mid', 'mid', 'open-mid', 'near-open', 'open']
ALL_VOWELS = set.union(*OPENNESS)
ALL_VOWELS.update({'ɿ', 'ʅ', 'ʮ', 'ʯ'})

# Vowels by position.

FRONT = {'i', 'y', 'e', 'ø', 'e\u031e', 'ø\u031e', 'ɛ', 'œ', 'æ', 'ɶ'}
NEAR_FRONT = {'ɪ', 'ʏ'}
CENTRAL = {'ɪ\u0308', 'ʊ\u0308', 'a', 'ä', 'ɐ', 'ɘ', 'ɚ', 'ə', 'ɜ', 'ɞ', 'ɨ', 'ɵ', 'ʉ'}
NEAR_BACK = {'ʊ'}
BACK = {'o', 'u', 'ɑ', 'ɒ', 'ɔ', 'ɤ', 'ɯ', 'ʌ', 'o\u031e', 'ɤ\u031e'}

POSITIONS = [FRONT, NEAR_FRONT, CENTRAL, NEAR_BACK, BACK]
POSITIONS_NAMES = ['front', 'near-front', 'central', 'near-back', 'back']

# Vowels by roundedness.

ROUNDED = {'y', 'ʉ', 'u', 'ʏ', 'ʊ\u0308', 'ʊ', 'ø', 'ɵ', 'o', 'ø\u031e', 'o\u031e', 'œ', 'ɞ', 'ɔ', 'ɶ', 'ɒ'}

# Additional articulations.

PRE_FEATURES = {
    '\u02c0': 'pre-glottalised',
    '\u02bc': 'pre-glottalised',
    '\u2019': 'pre-glottalised',
    '\u02b0': 'pre-aspirated',
    '\u02b1': 'pre-aspirated',
    '\u207f': 'pre-nasalised',
    '\u02b7': 'pre-labialised'
}

POST_FEATURES = {
    '\u02b0': 'aspirated',
    '\u02b1': 'aspirated',
    '\u02e4': 'pharyngealised',
    '\u02c0': 'glottalised',
    '\u02bc': 'glottalised',
    '\u2019': 'glottalised',
    '\u0303': 'nasalised',
    '\u02b7': 'labialised',
    '\u0306': 'ultra-short',
    '\u02e0': 'velarised',
    '\u0334': 'velarised',
    '\u0348': 'faucalised',
    '\u02b2': 'palatalised',
    '\u02d1': 'half-long',
    '\u02d0': 'long',
    '\u0330': 'creaky-voiced',
    '\u0324': 'breathy-voiced',
    '\u02e1': 'lateral-released',
    '\u02de': 'rhotic',
    '\u032f': 'non-syllabic',
    '\u031e': 'lowered',
    '\u031d': 'raised',
    '\u0349': 'weakly-articulated',
    '\u0347': 'alveolar',
    '\u030a': 'voiceless',
    '\u0325': 'voiceless',
    '\u032a': 'dental',
    '\u0353': '?',
    '\u0320': 'retracted',
    '\u033b': 'laminal',
    '\u0329': 'syllabic',
    '\u1e47': 'syllabic',
    '\u0308': 'centralised',
    '\u033d': 'mid-centralised',
    '\u0339': 'more-rounded',
    '\u031c': 'less-rounded',
    '\u031f': 'advanced',
    '\u0318': 'advanced-tongue-root',
    '\u0319': 'retracted-tongue-root',
    '\u031a': 'unreleased',
    '\u033a': 'apical',
    '\u02e2': 'affricated',
    '\u1dbb': 'affricated'
}

def parseCons(phon):
    # print("".join(phon)) # For finding bugs in descriptions.
    attributes = set()
    if len(phon) > 2:
        raise Exception("Too long a sequence: " + "".join(phon))
    if len(phon) == 1:
        phon = phon[0]
        if phon == '\u026b':
            attributes.add('velarised')   
        for i in range(len(MANNERS)):
            if phon in MANNERS[i]:
                attributes.add(MANNERS_NAMES[i])
                break
    else:
        phon = phon[1]
        attributes.add('affricate')
        if phon in LATERAL_FRICATIVES:
            attributes.add('lateral')
    for i in range(len(PLACES)):
        if phon in PLACES[i]:
            attributes.add(PLACES_NAMES[i])
            break
    if phon in VOICED:
        attributes.add('voiced')
    else:
        attributes.add('voiceless')
    return attributes

def parseVow(phon):
    attributes = set()
    if len(phon) > 3:
        raise Exception("Too long a sequence: " + "".join(phon))
    if len(phon) == 3:
        attributes.add('triphthong')
        return attributes
    elif len(phon) == 2:
        attributes.add('diphthong')
        return attributes
    elif phon[0] in {'ɿ', 'ʅ', 'ʮ', 'ʯ'}:
        attributes.add('apical')
        if phon[0] == 'ʅ' or phon[0] == 'ʯ':
            attributes.add('retroflex')
        if phon[0] == 'ʮ' or phon[0] == 'ʯ':
            attributes.add('labialised')
        return attributes
    else:
        phon = phon[0]
        for i in range(len(POSITIONS)):
            if phon in POSITIONS[i]:
                attributes.add(POSITIONS_NAMES[i])
                break
        for i in range(len(OPENNESS)):
            if phon in OPENNESS[i]:
                attributes.add(OPENNESS_NAMES[i])
        if len(attributes) < 2:
            raise Exception("Vowel attributes under-parsed: " + phon)
        if phon in ROUNDED:
            attributes.add('rounded')
        else:
            attributes.add('unrounded')
        return attributes

def parsePhon(phon):
    if ' ' in phon.strip():
        raise Exception('Blank space inside the phoneme! Check your commas: ' + phon)
    # Catch non-standard symbols and ignore brackets.
    replaceDict = {
        'ŝ': 'ƺ', # Internal convention — exchange for a singe non-IPA symbol.
        'ẑ': 'ʓ', # Idem.
        'z̩': 'ɿ',  # To parse as a vowel.
        'ʐ̩': 'ʅ',  # Idem.
        'z̩ʷ': 'ʮ', # Idem.
        'ʐ̩ʷ': 'ʯ', # Idem.
        '(': '',    # For marginal phonemes. Don't use this unless you really have to.
        ')': ''
    } 
    for key in replaceDict:
        phon = phon.replace(key, replaceDict[key])
    if len(phon) > 1:
        phonoset = set(phon)
        if 'w' in phonoset and phonoset.intersection(ALL_VOWELS):
            phon = phon.replace('w', 'u\u032f')
        elif 'ɰ' in phonoset and phonoset.intersection(ALL_VOWELS):
            phon = phon.replace('ɰ', 'ɨ')
        elif 'j' in phonoset and phonoset.intersection(ALL_VOWELS):
            phon = phon.replace('j', 'i\u032f')
    pre_attributes  = set()
    core_attributes = set()
    core_glyphs_vow = []
    core_glyphs_con = []
    post_attributes = set()
    j = 0
    # print(phon)
    for i in range(len(phon)):
        if phon[i] in MAIN_GLYPHS:
            j = i
            break
        else:
            if phon[i] in PRE_FEATURES:
                pre_attributes.add(PRE_FEATURES[phon[i]])
            else:
                if phon[i] == ' ':
                    continue
                else:
                    raise Exception("Failed to parse a feature %s of phoneme %s" % (str(phon[i].encode("unicode_escape")).strip('b'), phon))
    else:
        raise Exception("No core features found in %s" % phon)
    i = j
    while i < len(phon):
        if phon[i] in MAIN_GLYPHS:
            if phon[i] in ALL_CONSONANTS:
                core_glyphs_con.append(phon[i])
            else:
                if i < len(phon) - 1 and phon[ i : i + 2 ] in {'e\u031e', 'ø\u031e', 'ɪ\u0308', 'ʊ\u0308', 'o\u031e', 'ɤ\u031e'}:
                    core_glyphs_vow.append(phon[ i : i + 2 ])
                    i += 2
                    continue
                core_glyphs_vow.append(phon[i])
        else:
            if phon[i] not in POST_FEATURES and phon[i] != ' ':
                raise Exception("Failed to parse a feature %s of phoneme %s" % (str(phon[i].encode("unicode_escape")).strip('b'), phon))
            else:
                if phon[i] in POST_FEATURES and phon[i] != ' ':    
                    post_attributes.add(POST_FEATURES[phon[i]])
        i += 1
    if core_glyphs_con and core_glyphs_vow:
        raise Exception("Conflicting features error: " + "".join(phon))
    elif core_glyphs_vow:
        core_attributes.add('vowel')
        core_attributes.update(parseVow(core_glyphs_vow))
    elif core_glyphs_con:
        core_attributes.add('consonant')
        if core_glyphs_con[0] in {'n', 'ɲ', 'ɳ', 'ɴ'} and len(core_glyphs_con) > 1:
            pre_attributes.add(PRE_FEATURES['\u207f'])
            core_glyphs_con = core_glyphs_con[1:]
        core_attributes.update(parseCons(core_glyphs_con))
    # Check for diacritic-induced voiced-voiceless conflict.
    if 'voiceless' in post_attributes:
        if set.intersection(core_attributes, {'nasal', 'lateral', 'trill', 'approximant', 'tap', 'lateral_tap', 'lateral_approximant'}) or set(['palatal', 'affricate']).issubset(core_attributes):
            post_attributes.remove('voiceless')
            core_attributes.discard('voiced')
            core_attributes.add('voiceless')
        else:
            # print('%s must have zero VOT' % phon)
            core_attributes.add('lenis')
    # Check for redundant non-syllabicity and make proviso for diphthongs and triphthongs.
    if 'diphthong' in core_attributes:
        post_attributes.discard('non-syllabic')
        core_attributes.add(phon)
    if 'triphthong' in core_attributes:
        post_attributes.discard('non-syllabic')
        core_attributes.add(phon)
    # Check for laterals.
    if 'lateral' in core_attributes and 'affricate' in core_attributes:
        core_attributes.add('lateral_affricate')
    if 'lateral_fricative' in core_attributes:
        core_attributes.add('lateral')
        core_attributes.add('fricative')
    if 'lateral_approximant' in core_attributes:
        core_attributes.add('lateral')
        core_attributes.add('approximant')
    if 'lateral_tap' in core_attributes:
        core_attributes.add('lateral')
        core_attributes.add('tap')
    # Make non-laterals a class.
    if not 'lateral' in core_attributes:
        core_attributes.add('non_lateral')
    # Check for dental-alveolar conflict.
    if 'dental' in post_attributes:
        post_attributes.remove('dental')
        core_attributes.discard('alveolar')
        core_attributes.add('dental')
    # Check for the same the other way round.
    if 'alveolar' in post_attributes:
        post_attributes.remove('alveolar')
        core_attributes.discard('dental')
        core_attributes.add('alveolar')
    return pre_attributes, core_attributes, post_attributes

# Testing code.

def main():
#     # test_set = ['ɿ', 'ʅ', 'ʮ', 'ʯ', 'a', 'b', 'c', 'd', 'e', 'f', 'ɡ', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'æ', 'ç', 'ð', 'ø', 'ħ', 'ŋ', 'œ', 'ɐ', 'ɑ', 'ɒ', 'ɓ', 'ɔ', 'ɕ', 'ᶑ', 'ɖ', 'ɗ', 'ɘ', 'ə', 'ɛ', 'ɜ', 'ɞ', 'ɟ', 'ɠ', 'ɢ', 'ɣ', 'ɤ', 'ɥ', 'ɦ', 'ɨ', 'ɪ', 'ɬ', 'ɭ', 'ɮ', 'ɯ', 'ɰ', 'ɱ', 'ɲ', 'ɳ', 'ɴ', 'ɵ', 'ɶ', 'ɸ', 'ɹ', 'ɺ', 'ɻ', 'ɽ', 'ɾ', 'ʀ', 'ʁ', 'ʂ', 'ʃ', 'ʄ', 'ʈ', 'ʉ', 'ʊ', 'ʋ', 'ʌ', 'ʍ', 'ʎ', 'ʏ', 'ʐ', 'ʑ', 'ʒ', 'ʔ', 'ʕ', 'ʙ', 'ʛ', 'ʜ', 'ʝ', 'ʟ', 'ʡ', 'ʢ', 'β', 'θ', 'χ', 'ɚ', 'ɫ', '\u026a\u0308', '\u028a\u0308', '\xe4', '\xf8\u031e', 'e\u031e', '\u0264\u031e', 'o\u031e', 'ƺ', 'ʓ']
#     # i = 10000
#     # print(i * len(test_set), 'parses')
#     # time1 = time.time()
#     # for _ in range(i):
#     #     for phon in test_set:
#     #         parsePhon(phon)
#     # all_time = time.time() - time1
#     # time_per_parse = all_time / (i * len(test_set))
#     # print('All time:', all_time)
#     # print('Time per parse: %.10f' % time_per_parse)
#     while True:
#         phon = input()
#         print(set.union(*parsePhon(phon)))
#         print('More? ', end='')
#         reply = input()
#         if reply in {'n', 'N', 'no'}:
#             break
    for phon in ['ð', 'θ']:
        print(phon, parsePhon(phon))

if __name__ == '__main__':
    main()
    sys.exit(0)