from cgi import parse_qs, escape
from PhonoSearchLib import LangSearchEngine
from io import BytesIO
import re
import json
import os
import csv
import sys
import re

def app(environ, start_response):
    d = parse_qs(environ['QUERY_STRING'])
    print(d)
    if 'search_type' in d:
        if d['search_type'][0] == 'exact':
            if 'dialects' in d:
                try:
                    result = sorted(engine_w_dialects.IPA_exact_query(d['query'][0]))
                except:
                    result = []
            else:
                try:
                    result = sorted(engine.IPA_exact_query(d['query'][0]))
                except:
                    result = []
            callback = d['myCallback'][0]
            table = []
            for lang in result:
                table.append([
                        lang_dic[lang]["name"], lang_dic[lang]["code"], lang_dic[lang]["coords"][0], lang_dic[lang]["coords"][1], lang_dic[lang]["gen"][0], lang_dic[lang]["gen"][1]
                    ])
            responseJSON = json.dumps(['exact', d['query'][0], table])
            response_body = callback + "(" + responseJSON + ");"
            response_body = response_body.encode()
            status = '200 OK'
            response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))]
            start_response(status, response_headers)
            return [response_body]
        elif d['search_type'][0] == 'exact_multiple':
            phono_list = re.split(r'\s*,\s*', d['query'][0])
            phono_string = ', '.join(phono_list)
            if 'dialects' in d:
                result = sorted(engine_w_dialects.IPA_query_multiple(*phono_list))
            else:
                result = sorted(engine.IPA_query_multiple(*phono_list))
            callback = d['myCallback'][0]
            table = []
            for lang in result:
                table.append([
                        lang_dic[lang]["name"], lang_dic[lang]["code"], lang_dic[lang]["coords"][0], lang_dic[lang]["coords"][1], lang_dic[lang]["gen"][0], lang_dic[lang]["gen"][1]
                    ])
            responseJSON = json.dumps(['exact_multiple', d['query'][0], table])
            response_body = callback + "(" + responseJSON + ");"
            response_body = response_body.encode()
            status = '200 OK'
            response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))]
            start_response(status, response_headers)
            return [response_body]
        elif d['search_type'][0] == 'superset':
            if 'dialects' in d:
                try:
                    result = engine_w_dialects.IPA_query(d['query'][0]) # Result is a dictionary now!
                except:
                    result = {}
            else:
                try:
                    result = engine.IPA_query(d['query'][0])
                except:
                    result = {}
            result_dic = {}
            for key in result:
                result_dic[key] = []
                for lang in result[key]:
                    result_dic[key].append([
                        lang_dic[lang]["name"], lang_dic[lang]["code"], lang_dic[lang]["coords"][0], lang_dic[lang]["coords"][1], lang_dic[lang]["gen"][0], lang_dic[lang]["gen"][1]
                    ])
            responseJSON = json.dumps([d['query'][0], result_dic])
            response_body = d['myCallback'][0] + "(" + responseJSON + ");"
            response_body = response_body.encode()
            status = '200 OK'
            response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))]
            start_response(status, response_headers)
            return [response_body]
        elif d['search_type'][0] == 'feature':
            feature_list = re.split(r'\s*,\s*', d['query'][0])
            feature_string = ', '.join(feature_list)
            if 'dialects' in d:
                result = sorted(engine_w_dialects.features_query(*feature_list))
            else:
                result = sorted(engine.features_query(*feature_list))
            callback = d['myCallback'][0]
            table = []
            for lang in result:
                table.append([
                        lang_dic[lang]["name"], lang_dic[lang]["code"], lang_dic[lang]["coords"][0], lang_dic[lang]["coords"][1], lang_dic[lang]["gen"][0], lang_dic[lang]["gen"][1]
                    ])
            responseJSON = json.dumps(['feature', d['query'][0], table])
            response_body = callback + "(" + responseJSON + ");"
            response_body = response_body.encode()
            status = '200 OK'
            response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))]
            start_response(status, response_headers)
            return [response_body]
        else:
            response_body = ('Nothing here yet').encode()
            status = '200 OK'
            response_headers = [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(response_body)))
            ]
            start_response(status, response_headers)
            return [response_body]
    elif 'report_type' in d:
        if d['report_type'][0] == 'family':
            response_body = "showFamilyReport("
            if 'dialects' in d:
                response_body += engine_w_dialects.generate_family_report(d['family'][0])
            else:
                response_body += engine.generate_family_report(d['family'][0])
        elif d['report_type'][0] == 'group':
            response_body = "showGroupReport("
            if 'dialects' in d:
                response_body += engine_w_dialects.generate_group_report(d['group'][0])
            else:
                response_body += engine.generate_group_report(d['group'][0])
        response_body += ");"
        response_body = response_body.encode()
        status = '200 OK'
        response_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]
    elif 'stats' in d:
        response_body = d['myCallback'][0] + "("
        respDic = {
            "nlangs": len(engine.lang_dic),
            "ndials": len(engine_w_dialects.lang_dic) - len(engine.lang_dic),
            "nvars":  len(engine_w_dialects.lang_dic)
        }
        response_body += json.dumps(respDic) + ");"
        response_body = response_body.encode()
        status = '200 OK'
        response_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]
    elif 'langlist' in d:
        response_body = d['myCallback'][0] + "("
        response_dic = {}
        group_dic    = {}
        if 'dialects' in d:
            for key in engine_w_dialects.phyla_dic:
                response_dic[key] = sorted(engine_w_dialects.phyla_dic[key])
            group_dic = engine_w_dialects.group_dic
            isolates  = engine_w_dialects.family_dic['Isolate']
        else:
            for key in engine.phyla_dic:
                response_dic[key] = sorted(engine.phyla_dic[key])
            group_dic = engine.group_dic
            isolates  = engine_w_dialects.family_dic['Isolate']
        response_body += json.dumps([response_dic, group_dic, isolates]) + ");"
        response_body = response_body.encode()
        status = '200 OK'
        response_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]
    elif 'dataForMap' in d:
        response_body = "addToMap("
        response_body += json.dumps([engine.family_group_dic, engine.coord_dic]) + ");"
        response_body = response_body.encode()
        status = '200 OK'
        response_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]
    elif 'provideInventoryTable' in d:
        response_body = d['myCallback'][0] + "("
        response_body += json.dumps(engine_w_dialects.get_table(d['provideInventoryTable'][0])) + ");"
        response_body = response_body.encode()
        status = '200 OK'
        response_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]
    elif 'requestAllSegments' in d:
        response_body = d['myCallback'][0] + "("
        response_body += json.dumps(engine_w_dialects.get_full_table()) + ");"
        response_body = response_body.encode()
        status = '200 OK'
        response_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]
    else:
        response_body = ('Nothing here yet').encode()
        status = '200 OK'
        response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]


# Initialising two search engines (one for languages
# and the other for languages and dialects)
# and a language dictionary for reports.
engine            = LangSearchEngine('dbase/phono_dbase.json', False)
engine_w_dialects = LangSearchEngine('dbase/phono_dbase.json', True)
with open('dbase/phono_dbase.json', 'r', encoding = 'utf-8') as inp:
    lang_dic = json.load(inp)