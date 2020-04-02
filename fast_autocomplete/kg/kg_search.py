import os
import pprint
import readline
import time

import json
if os.environ.get('OLD') == '1':
    from fast_autocomplete.dwg_old import AutoComplete
else:
    from fast_autocomplete.dwg import AutoComplete
import sys
import mmap

from fast_autocomplete.kg.StringUtil import cleanString
from fast_autocomplete.misc import my_tqdm


def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines

words = {}
# synonyms = {}
files_names = []
loaded = False
for file_name in sys.argv[1:]:
    files_names.append(os.path.basename(file_name))

try:
    with open("%s_autocomplete.json" % "_".join(files_names), "r") as in_fd:
        autocomplete = AutoComplete(words=None, in_fd=in_fd)
    loaded = True
except Exception as e:
    print(e)
    for file_name in sys.argv[1:]:
        with open(file_name) as ff:
            for t in my_tqdm(ff, desc="Processing %s" % file_name, total=get_num_lines(file_name)):
                if file_name.endswith(".jsonl"):
                    tj = json.loads(t)
                    first_word = None
                    for kn in ['Ti', 'Ak']:
                        for tok in tj[kn]:
                            if not first_word:
                                first_word = cleanString(tok)
                                if first_word:
                                    words[first_word] = {}
                            else:
                                ctok = cleanString(tok)
                                if ctok:
                                    words[ctok] = {}
                                    # synonyms.setdefault(first_word, set()).add(ctok)
                else:
                    words[cleanString(t)] = {}
    autocomplete = AutoComplete(words=words)#, synonyms=synonyms)
# with open("autocomplete.json", "r") as in_fd:
#     autocomplete = AutoComplete(words=None, in_fd=in_fd)
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')
max_cost = 3
size = 5
while True:
    test_query_all = input("(query)$ ")
    if test_query_all == "q":
        break
    if test_query_all.startswith(":"):
        cmd = ":".join(test_query_all.split(":")[1:])
        if cmd in ["max_cost", "size"]:
            test_query_all = input("(%s)$ " % cmd)
            if cmd == "max_cost":
                max_cost = int(test_query_all)
            elif cmd == "size":
                size = int(test_query_all)
    st = time.time()
    #import pdb;pdb.set_trace()
    result_dict = autocomplete.search(word=cleanString(test_query_all), max_cost=max_cost, size=size)
    en = time.time()
    pprint.pprint(result_dict)
    print("In %s ms" % str(1000*(en-st)))
if not loaded:
    with open("%s_autocomplete.json" % "_".join(files_names), "w") as out_fd:
        autocomplete.dump(out_fd)
