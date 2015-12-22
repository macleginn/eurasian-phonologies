import IPAParser
import re
import csv
import json
import pprint
from io import StringIO
from IPATabulator import CONS_ROW_NAMES, CONS_COL_NAMES
from IPATabulator import VOW_ROW_NAMES, VOW_COL_NAMES
from IPATabulator import processInventory, tabulateAllSegments

CONS_COL_NAMES.append('interdental')

class LangSearchEngine:
    def __init__(self, path, with_dialects):
        with open(path, 'r', encoding = 'utf-8') as inp:
            self.lang_dic = json.load(inp)
        if not with_dialects:
            entries_for_deletion = []
            for key in self.lang_dic:
                if self.lang_dic[key]["type"] == "Диалект":
                    entries_for_deletion.append(key)
            for key in entries_for_deletion:
                del self.lang_dic[key]
        self.all_langs    = set()
        self.all_phonemes = {} # Frozenset -> glyph map.
        self.phyla_dic    = {} # Family -> Sets of groups.
        self.family_dic   = {}
        self.group_dic    = {}
        self.inv_dic      = {}
        self.non_systematic   = {} # Phonemes which we cannot put in the table.
        self.coord_dic        = {} # For map.
        self.family_group_dic = {} # Idem.

        # Prepairing tables for lookup.
        self.cons_table = [[{} for i in CONS_COL_NAMES] for j in CONS_ROW_NAMES]
        self.cons_x_coords = {}
        for pair in enumerate(CONS_COL_NAMES):
            self.cons_x_coords[pair[1]] = pair[0]
        self.cons_y_coords = {}
        for pair in enumerate(CONS_ROW_NAMES):
            self.cons_y_coords[pair[1]] = pair[0]
        self.vow_table = [[{} for i in VOW_COL_NAMES] for j in VOW_ROW_NAMES]
        self.vow_x_coords = {}
        for pair in enumerate(VOW_COL_NAMES):
            self.vow_x_coords[pair[1]] = pair[0]
        self.vow_y_coords = {}
        for pair in enumerate(VOW_ROW_NAMES):
            self.vow_y_coords[pair[1]] = pair[0]
        self.cons_rows = set(CONS_ROW_NAMES)
        self.cons_cols = set(CONS_COL_NAMES)
        self.vow_rows = set(VOW_ROW_NAMES)
        self.vow_cols = set(VOW_COL_NAMES)
        
        # Adding languages.
        for key in self.lang_dic:
            self.add_language(key, self.lang_dic[key]["inv"])

            self.coord_dic[key] = self.lang_dic[key]["coords"]
            self.family_group_dic[key] = self.lang_dic[key]["gen"]

            family = self.lang_dic[key]["gen"][0]
            if self.lang_dic[key]["gen"][1]:
                group = self.lang_dic[key]["gen"][1]
            else:
                group = family + "_ungrouped"

            # Which families contain which groups.
            if family not in self.phyla_dic:
                self.phyla_dic[family] = set()
            if group:
                self.phyla_dic[family].add(group)
            
            # Which families and groups contain which langs.
            if not family in self.family_dic:
                self.family_dic[family] = []
            self.family_dic[family].append(key)
            if not group in self.group_dic:
                self.group_dic[group] = []
            self.group_dic[group].append(key)

    def generate_family_report(self, family):
        """This report, unlike the group one, will include data on group membership of languages in the family to show them on the map."""
        report = {}
        langs_to_report = self.family_dic[family]
        report["map_data"] = [] # List of lists of the type [lang_name, group, lat, lon]
        for lang in langs_to_report:
            report["map_data"].append(
                [id2name(lang),
                self.lang_dic[lang]["gen"][1],
                self.lang_dic[lang]["coords"][0],
                self.lang_dic[lang]["coords"][1]]
                )
        report["inv_sizes"] = self.get_inv_sizes(langs_to_report)
        report["table_of_common_phons"] = self.get_common_table(langs_to_report)
        return json.dumps(report, indent = 4, ensure_ascii = False)

    def generate_group_report(self, group):
        langs_to_report = self.group_dic[group]
        report = {} #To return as a JSON object.
        report["map_data"] = [] # List of lists of the type [lang_name, lat, lon]
        for lang in langs_to_report:
            report["map_data"].append(
                [id2name(lang),
                self.lang_dic[lang]["coords"][0],
                self.lang_dic[lang]["coords"][1]]
                )
        report["inv_sizes"] = self.get_inv_sizes(langs_to_report)
        report["table_of_common_phons"] = self.get_common_table(langs_to_report)
        return json.dumps(report, indent = 4, ensure_ascii = False)

    def get_common_table(self, langs_to_report):
        common_phonemes = set.intersection(*[self.inv_dic[lang] for lang in langs_to_report])
        phono_string = ', '.join(self.all_phonemes[phoneme] for phoneme in common_phonemes)
        if not phono_string:
            return ""
        else:
            return processInventory("Common phonemes", phono_string, True)

    def get_table(self, lang):
        phonemes = self.inv_dic[lang]
        phono_string = ', '.join(self.all_phonemes[phoneme] for phoneme in phonemes)
        out = StringIO()
        out.write('<div class="phono_tables"><h3>%s</h3>' % (lang.split('#')[0]))
        if self.lang_dic[lang]["code"] == '0':
            code = '-'
        else:
            code = self.lang_dic[lang]["code"]
        out.write('<p><b>Ethnologue code:</b> %s</p>' % code)
        out.write('<p><b>Family:</b> %s</p>' % self.lang_dic[lang]["gen"][0])
        if self.lang_dic[lang]["gen"][1]:
            out.write('<p><b>Group:</b> %s</p>' % self.lang_dic[lang]["gen"][1])
        else:
            out.write('<p><b>Group:</b> %s</p>' % "–")
        out.write(processInventory(lang, phono_string, False)) # Vowels and consonants.
        if self.lang_dic[lang]["tones"]:
            out.write("<h4>Tones</h2><p>%s</p>\n" % ', '.join(self.lang_dic[lang]["tones"]))
        if self.lang_dic[lang]["syllab"]:
            out.write("<h4>Syllable structure</h2><p>%s</p>\n" % self.lang_dic[lang]["syllab"])
        if self.lang_dic[lang]["cluster"]:
            out.write("<h4>Initial clusters</h2><p>%s</p>\n" % self.lang_dic[lang]["cluster"])
        if self.lang_dic[lang]["finals"]:
            out.write("<h4>Word-final clusters and segments</h2><p>%s</p>\n" % self.lang_dic[lang]["finals"])
        out.write("<h4>Source</h3><p>%s</p>\n" % self.lang_dic[lang]["source"])
        if self.lang_dic[lang]["comment"]:
            out.write("<h4>Commentary</h3><p>%s</p>\n" % self.lang_dic[lang]["comment"])
        out.write("<h4>Added by</h3><p>%s</p>\n" % self.lang_dic[lang]["contr"])
        out.write('</div>')
        return out.getvalue()

    def get_full_table(self):
        segments = ', '.join([self.all_phonemes[key] for key in self.all_phonemes])
        out = StringIO()
        out.write('<div class="phono_tables"><h1>All segments in the database</h1>\n')
        out.write('<p>(<em>Click on the phonemes to see their distribution.</em>)</p>\n')
        out.write(tabulateAllSegments(segments))
        out.write('</div>')
        return out.getvalue()

    def get_inv_sizes(self, langs_to_report):
        report = {
            "all": [],
            "cons": [],
            "vows": [],
            "tones": []
        }
        for lang in langs_to_report:
            all_segs = ncons = nvows = ntones = 0
            for phoneme in self.inv_dic[lang]:
                all_segs += 1
                if 'vowel' in phoneme:
                    nvows += 1
                elif 'consonant' in phoneme:
                    ncons += 1
                else:
                    raise ValueError("A segment is neither a consonant nor a vowel")
            ntones = len(self.lang_dic[lang]['tones'])
            report["all"].append(all_segs)
            report["cons"].append(ncons)
            report["vows"].append(nvows)
            report["tones"].append(ntones)
        return report

    def add_language(self, lang_name, phonemes):
        self.all_langs.add(lang_name)
        self.inv_dic[lang_name] = set()
        # We do not account for polyphthongs and apical vowels for now -- todo!
        for phoneme in phonemes:
            glyph = phoneme
            phoneme = set.union(*IPAParser.parsePhon(phoneme))
            phoneme_key = frozenset(phoneme)
            self.inv_dic[lang_name].add(phoneme_key)
            if phoneme_key not in self.all_phonemes:
                self.all_phonemes[phoneme_key] = glyph
            if 'vowel' in phoneme:
                if phoneme.intersection({'apical', 'diphthong', 'triphthong'}):
                    if phoneme_key not in self.non_systematic:
                        self.non_systematic[phoneme_key] = [glyph, []]
                    self.non_systematic[phoneme_key][1].append(lang_name)
                    continue
                height = phoneme.intersection(VOW_ROW_NAMES).pop()
                y_coord = self.vow_y_coords[height]
                row = phoneme.intersection(VOW_COL_NAMES).pop()
                x_coord = self.vow_x_coords[row]
                if phoneme_key not in self.vow_table[y_coord][x_coord]:
                    self.vow_table[y_coord][x_coord][phoneme_key] = (glyph, [])
                self.vow_table[y_coord][x_coord][phoneme_key][1].append(lang_name)
            else:
                try:
                    manner = phoneme.intersection(CONS_ROW_NAMES).pop()
                except KeyError:
                    raise Exception("A consonant does not have a manner:", phoneme)
                y_coord = self.cons_y_coords[manner]
                place = phoneme.intersection(CONS_COL_NAMES).pop()
                x_coord = self.cons_x_coords[place]
                if phoneme_key not in self.cons_table[y_coord][x_coord]:
                    self.cons_table[y_coord][x_coord][phoneme_key] = (glyph, [])
                self.cons_table[y_coord][x_coord][phoneme_key][1].append(lang_name)

    def IPA_exact_query(self, phoneme_string):
        """Returns a list of languages containing this phoneme."""

        phoneme = set.union(*IPAParser.parsePhon(phoneme_string))
        result = {}
        if 'vowel' in phoneme:
            if phoneme.intersection({'apical', 'diphthong', 'triphthong'}):
                phoneme_key = frozenset(phoneme)
                if phoneme_key in self.non_systematic:
                    return self.non_systematic[phoneme_key][1]
                else:
                    return []
            height = phoneme.intersection(self.vow_rows).pop()
            y_coord = self.vow_y_coords[height]
            row = phoneme.intersection(self.vow_cols).pop()
            x_coord = self.vow_x_coords[row]
            for key in self.vow_table[y_coord][x_coord]:
                if key == phoneme:
                    return self.vow_table[y_coord][x_coord][key][1]
            return []         
        else:
            manner = phoneme.intersection(self.cons_rows).pop()
            y_coord = self.cons_y_coords[manner]
            place = phoneme.intersection(self.cons_cols).pop()
            x_coord = self.cons_x_coords[place]
            for key in self.cons_table[y_coord][x_coord]:
                if key == phoneme:
                    return self.cons_table[y_coord][x_coord][key][1]
            return []
        raise Exception("Unreachable!")

    def IPA_query(self, phoneme_string):
        """Returns a dictionary with languages containing this phoneme and its derivatives."""

        phoneme = set.union(*IPAParser.parsePhon(phoneme_string))
        result = {}
        if 'vowel' in phoneme:
            if phoneme.intersection({'apical', 'diphthong', 'triphthong'}):
                for key in self.non_systematic:
                    if key.issuperset(phoneme):
                        glyph = self.non_systematic[key][0]
                        langs = self.non_systematic[key][1]
                        result[glyph] = langs
                return result
            height = phoneme.intersection(self.vow_rows).pop()
            y_coord = self.vow_y_coords[height]
            row = phoneme.intersection(self.vow_cols).pop()
            x_coord = self.vow_x_coords[row]
            for key in self.vow_table[y_coord][x_coord]:
                if key.issuperset(phoneme):
                    glyph = self.vow_table[y_coord][x_coord][key][0]
                    langs = self.vow_table[y_coord][x_coord][key][1]
                    result[glyph] = langs
            return result
        else:
            manner = phoneme.intersection(self.cons_rows).pop()
            y_coord = self.cons_y_coords[manner]
            place = phoneme.intersection(self.cons_cols).pop()
            x_coord = self.cons_x_coords[place]
            for key in self.cons_table[y_coord][x_coord]:
                if key.issuperset(phoneme):
                    glyph = self.cons_table[y_coord][x_coord][key][0]
                    langs = self.cons_table[y_coord][x_coord][key][1]
                    result[glyph] = langs
            return result
        raise Exception("Unreachable!")

    def IPA_query_multiple(self, *args):
        result = set()
        positive = []
        negative = []
        for phoneme in args:
            if phoneme[0] == '-':
                negative.append(phoneme[1:])
            else:
                positive.append(phoneme)
        if not negative and not positive:
            raise Exception("Nothing to search for")
        if not positive:
            result = self.all_langs
        else:
            result = self._dict2set(self.IPA_query(positive[0]))
            for phoneme in positive[1:]:
                result = result.intersection(self._dict2set(self.IPA_query(phoneme)))
        for phoneme in negative:
            result = result.difference(self._dict2set(self.IPA_query(phoneme)))
        return result

    def inject_laterals(self, arg):
        pass

    def features_query(self, *args):
        positive = set()
        negative = set()
        all_positives = []
        for arg in args:
            if 'lateral affricate' in arg:
                arg = arg.replace('lateral affricate', 'lateral_affricate')
            if 'lateral fricative' in arg:
                arg = arg.replace('lateral fricative', 'lateral_fricative')
            if 'lateral approximant' in arg:
                arg = arg.replace('lateral approximant', 'lateral_approximant')
        for arg in args:
            if arg[0] == '-':
                negative.add(arg[1:])
            else:
                positive.add(arg)
        if not positive:
            result = self.all_langs
        else:
            for feature in positive:
                feature = set(feature.split())
                temp = set()
                for key in self.all_phonemes:
                    if feature.issubset(key):
                        temp.update(self._dict2set(self.IPA_query(self.all_phonemes[key])))
                all_positives.append(temp)
            result = set.intersection(*all_positives)
        for feature in negative:
            feature = set(feature.split())
            for key in self.all_phonemes:
                if feature.issubset(key):
                    result = result.difference(self._dict2set(self.IPA_query(self.all_phonemes[key])))
        return result

    def feature_query_stat(self):
        pass

    def _dict2set(self, dic):
        result = set()
        for key in dic:
            for lang in dic[key]:
                result.add(lang)
        return result

    def feature_rating(self, feature):
        feature_havers = {}
        for lang in self.features_query(feature):
            counter = 0
            for phon in engine.lang_dic[lang]:
                if feature in set.union(*IPAParser.parsePhon(phon)):
                    counter += 1
            feature_havers[lang] = counter
        rating = []
        for key, value in feature_havers.items():
            rating.append((value, key))
        rating.sort(reverse = True)
        return rating

    def IPA_query_rating(self):
        pass # todo

def clear(s):
    return s.strip(' \n\t').replace('\u0361', '').replace('\u2009', '')

def id2name(lang):
    temp = []
    for char in lang:
        if char != '#':
            temp.append(char)
        else:
            break
    return ''.join(temp)

def escapeHTML4JSON(html):
    result = []
    for char in html:
        if char == '"':
            result.append(r'\"')
        elif char == '/':
            result.append(r'\/')
        else:
            result.append(char)
    return ''.join(result)

# Test code

if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent = 4)
    engine = LangSearchEngine('dbase/phono_dbase.json', with_dialects = True)
    pp.pprint(engine.IPA_query_multiple('-n'))
