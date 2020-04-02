
from fast_autocomplete.kg.data_schema import get_schema
import sys
import json
import os,re

from fast_autocomplete.kg import genericFileInterfaces

"""Add only in small case."""
IGNORE_GIDS_DICT = {
        'por' : {'canal':['WIKI5623']},
        'eng' : {},
        'deu' : {},
        'ita' : {}
    }

out_file = open(sys.argv[3], 'w')
def get_list_of_only_lang(field, lang, fallback_to_none = False):
    field_s = field.split("<>")
    out = []
    for each_f in field_s:
        if re.match(".*[{,:]"+lang+"[},:].*",each_f):
            cleaned = re.sub(r'{.*?}', '',re.sub(r'\([^)]*\)', '', each_f))
            out.append(cleaned)
    if len(out) == 0 and fallback_to_none:
        for each_f in field_s:
            cleaned = re.sub(r'{.*?}', '',re.sub(r'\([^)]*\)', '', each_f))
            out.append(cleaned)
    return out
schema_list = ['Gi','Ak','Ti','Ik', 'Vt']
schema = get_schema(schema_list)

def remove_ignored_phrases(phrase_list, gid):
    return [x for x in phrase_list if x.lower() not in IGNORE_GIDS_DICT or gid not in IGNORE_GIDS_DICT[x.lower()]]

for data in genericFileInterfaces.fileIterator(os.path.join(sys.argv[1]), schema):
    data[schema['Ti']] = remove_ignored_phrases(get_list_of_only_lang(data[schema['Ti']],sys.argv[2], fallback_to_none = True), data[schema['Gi']])
    data[schema['Ak']] = remove_ignored_phrases(get_list_of_only_lang(data[schema['Ak']],sys.argv[2]), data[schema['Gi']])
    data[schema['Ik']] = remove_ignored_phrases(get_list_of_only_lang(data[schema['Ik']],sys.argv[2]), data[schema['Gi']])


    if not data[schema['Ti']] and not data[schema['Ak']]:
        continue
    out_file.write(json.dumps({schema_key: data[schema[schema_key]] for schema_key in schema_list})+'\n')


