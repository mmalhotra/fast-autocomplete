import bisect
import json
import os
import time
from collections import (
    defaultdict,
    deque, OrderedDict)
from itertools import islice
from enum import Enum
from threading import Lock
from pprint import pprint
from fast_autocomplete.lfucache import LFUCache
from fast_autocomplete.misc import _extend_and_repeat, my_tqdm
from fast_autocomplete.normalize import normalize_node_name

from sortedcontainers import SortedDict
from Levenshtein import distance as levenshtein_distance

DELIMITER = '__'
ORIGINAL_KEY = 'original_key'
INF = float('inf')

time_dict = {}

class NodeNotFound(ValueError):
    pass


def toggle_time(label, my_time_dict):
    cur_time = time.time()
    label_dict = my_time_dict.setdefault(label, {})
    st = label_dict.get('st')
    if st:
        label_dict['total'] = label_dict.get('total', 0) + (cur_time - st)
        label_dict['freq'] = label_dict.get('freq', 0) + 1
        del label_dict['st']
    else:
        label_dict['st'] = time.time()

def format_time(my_time_dict):
    for label, timings in my_time_dict.items():
        new_dict = {}
        for name, value in timings.items():
            new_dict[name] = "{:.10f}".format(1000*value) if name in {'total', 'st'} else value
        my_time_dict[label] = new_dict

class KeyList(object):
    # bisect doesn't accept a key function, so we build the key into our sequence.
    def __init__(self, l, key):
        self.l = l
        self.key = key

    def __len__(self):
        return len(self.l)

    def __getitem__(self, index):
        return self.key(self.l[index])


def common_prefix(a, b):
    _common = []
    for i in range(min(len(a), len(b))):
        if a[i] == b[i]:
            _common.append(a[i])
        else:
            break
    return "".join(_common)


def get_prefixes_from_list(word, prefixes, start, end):
    results = []
    if start > end:
        return results
    middle = int((start + end) / 2)
    mword = prefixes[middle]
    go_left, go_right = (False, False)
    pref_mword = common_prefix(word, mword)
    if pref_mword == mword:
        results.append(middle)
        go_left, go_right = (True, True)
    else:
        prob_prefix = 0
        min_word = prefixes[start]
        max_word = prefixes[end]
        pref_min_word = common_prefix(word, min_word)
        pref_max_word = common_prefix(word, max_word)
        if min_word <= pref_min_word <= mword:
            go_left = True
        if min_word <= pref_min_word + word[len(pref_min_word):len(pref_min_word) + 1] <= mword:
            go_left = True
        if min_word <= pref_mword <= mword:
            go_left = True
        if min_word <= pref_mword + word[len(pref_mword):len(pref_mword) + 1] <= mword:
            go_left = True
        if max_word >= pref_max_word >= mword:
            go_right = True
        if max_word >= pref_max_word + word[len(pref_max_word):len(pref_max_word) + 1] >= mword:
            go_right = True
        if max_word >= pref_mword >= mword:
            go_right = True
        if max_word >= pref_mword + word[len(pref_mword):len(pref_mword) + 1] >= mword:
            go_right = True
    if go_left:
        results.extend(get_prefixes_from_list(word, prefixes, start, middle - 1))
    if go_right:
        results.extend(get_prefixes_from_list(word, prefixes, middle + 1, end))
    return results


class FindStep(Enum):
    start = 0
    descendants_only = 1
    fuzzy_try = 2
    fuzzy_found = 3
    rest_of_fuzzy_round2 = 4
    not_enough_results_add_some_descandants = 5


class AutoComplete:
    CACHE_SIZE = 2048
    SHOULD_INCLUDE_COUNT = True
    DUMP_ATTRS = ["_clean_synonyms", "_partial_synonyms",
                  "_reverse_synonyms", "_full_stop_words", "words", ]

    def __init__(self, words, synonyms=None, full_stop_words=None, logger=None, in_fd=None):
        """
        Inistializes the Autocomplete module

        :param words: A dictionary of words mapped to their context
        :param synonyms: (optional) A dictionary of words to their synonyms.
                         The synonym words should only be here and not repeated in words parameter.
        """
        self._lock = Lock()
        self._dwg = None
        if os.environ.get('DEBUG') == '1':
            self.CACHE_SIZE = 0
        self._lfu_cache = LFUCache(self.CACHE_SIZE)
        self._raw_synonyms = synonyms or {}
        self.logger = logger
        if in_fd:
            self._load(in_fd)
        else:
            self._clean_synonyms, self._partial_synonyms = \
                    self._get_clean_and_partial_synonyms()
            self._reverse_synonyms = self._get_reverse_synonyms(self._clean_synonyms)
            self._full_stop_words = set(full_stop_words) if full_stop_words else None
            self.words = words
            new_words = self._get_partial_synonyms_to_words()
            self.words.update(new_words)
        self.sorted_words = None
        self._populate_dwg()

    def dump(self, out_fd):
        """
        Dumps the Autocomplete state as a JSON.

        :param out_fd: File descriptor to write to
        """
        json.dump({attr_name: getattr(self, attr_name) for attr_name in self.DUMP_ATTRS}, out_fd)

    def _load(self, in_fd):
        """
        Load the Autocomplete state from a JSON File.

        :param in_fd: File descriptor to read from.
        """
        loaded_json = json.load(in_fd)
        for attr_name in self.DUMP_ATTRS:
            attr_value = loaded_json[attr_name]
            setattr(self, attr_name, attr_value)

    def _get_clean_and_partial_synonyms(self):
        """
        Synonyms are words that should produce the same results.

        - For example `beemer` and `bmw` should both give you `bmw`.
        - `alfa` and `alfa romeo` should both give you `alfa romeo`

        The synonyms get divided into 2 groups:

        1. clean synonyms: The 2 words share little or no words. For example `beemer` vs. `bmw`.
        2. partial synonyms: One of the 2 words is a substring of the other one. For example `alfa` and `alfa romeo` or `gm` vs. `gmc`.

        """
        clean_synonyms = {}
        partial_synonyms = {}
        sorted_synonyms = []
        for key, synonyms in my_tqdm(self._raw_synonyms.items(), desc="Clean Partial Synonyms"):
            key = key.strip().lower()
            _clean = []
            _partial = []
            for syn in synonyms:
                syn = syn.strip().lower()
                if key.startswith(syn):
                    _partial.append(syn)
                else:
                    _clean.append(syn)
            if _clean:
                clean_synonyms[key] = _clean
            if _partial:
                partial_synonyms[key] = _partial

        return clean_synonyms, partial_synonyms

    def _get_reverse_synonyms(self, synonyms):
        result = {}
        if synonyms:
            for key, value in my_tqdm(synonyms.items(), desc="Reverse Synonyms"):
                for item in value:
                    result[item] = key
        return result

    def _get_partial_synonyms_to_words(self):
        new_words = {}
        for key, value in my_tqdm(self.words.items(), desc="Partial Synonyms to Words"):
            # data is mutable so we copy
            try:
                value = value.copy()
            # data must be named tuple
            except Exception:
                new_value = value._asdict()
                new_value[ORIGINAL_KEY] = key
                value = type(value)(**new_value)
            else:
                value[ORIGINAL_KEY] = key
            for syn_key, syns in self._partial_synonyms.items():
                if key.startswith(syn_key):
                    for syn in syns:
                        new_key = key.replace(syn_key, syn)
                        new_words[new_key] = value
        return new_words

    def _populate_dwg(self):
        if not self._dwg:
            with self._lock:
                if not self._dwg:
                    self._dwg = _DawgNode()
                    for word, value in my_tqdm(self.words.items(), desc="Populate DWG"):
                        original_key = value.get(ORIGINAL_KEY)
                        word = word.strip().lower()
                        count = value.get('count', 0)
                        leaf_node = self.insert_word_branch(
                            word,
                            original_key=original_key,
                            count=count
                        )
                        if self._clean_synonyms:
                            for synonym in self._clean_synonyms.get(word, []):
                                self.insert_word_branch(
                                    synonym,
                                    leaf_node=leaf_node,
                                    add_word=False,
                                    count=count
                                )

    def insert_word_callback(self, word):
        """
        Once word is inserted, run this.
        """
        pass

    def insert_word_branch(self, word, leaf_node=None, add_word=True, original_key=None, count=0):
        """
        Inserts a word into the Dawg.

        :param word: The word to be inserted as a branch of dwg
        :param leaf_node: (optional) The leaf node for the node to merge into in the dwg.
        :param add_word: (Boolean, default: True) Add the word itself at the end of the branch.
                          Usually this is set to False if we are merging into a leaf node and do not
                          want to add the actual word there.
        :param original_key: If the word that is being added was originally another word.
                             For example with synonyms, you might be inserting the word `beemer` but the
                             original key is `bmw`. This parameter might be removed in the future.

        """
        if leaf_node:
            temp_leaf_node = self._dwg.insert(
                word[:-1],
                add_word=add_word,
                original_key=original_key,
                count=count,
                insert_count=self.SHOULD_INCLUDE_COUNT
            )
            temp_leaf_node.children[word[-1]] = leaf_node
        else:
            leaf_node = self._dwg.insert(
                word,
                original_key=original_key,
                count=count,
                insert_count=self.SHOULD_INCLUDE_COUNT
            )
        self.insert_word_callback(word)
        return leaf_node

    def _find_and_sort(self, word, max_cost, size):
        toggle_time("_find_and_sort", time_dict)
        output_keys_set = set()
        results, find_steps = self._find(word, max_cost, size)
        results_keys = list(results.keys())
        results_keys.sort()
        for key in results_keys:
            for output_items in results[key]:
                for i, item in enumerate(output_items):
                    reversed_item = self._reverse_synonyms.get(item)
                    if reversed_item:
                        output_items[i] = reversed_item
                    elif item not in self.words:
                        output_items[i] = item
                output_items_str = DELIMITER.join(output_items)
                if output_items and output_items_str not in output_keys_set:
                    output_keys_set.add(output_items_str)
                    yield output_items
                    if len(output_keys_set) >= size:
                        toggle_time("_find_and_sort", time_dict)
                        return
        toggle_time("_find_and_sort", time_dict)

    def get_tokens_flat_list(self, word, max_cost=3, size=10):
        """
        Gets a flat list of tokens.
        This requires the original search function from this class to be run,
        instead of subclasses of AutoComplete.
        """
        result = AutoComplete.search(self, word, max_cost=max_cost, size=size)
        return [item for sublist in result for item in sublist]

    def get_word_context(self, word):
        """
        Gets the word's context from the words dictionary
        """
        word = normalize_node_name(word)
        return self.words.get(word)

    def search(self, word, max_cost=2, size=5):
        """
        parameters:
        - word: the word to return autocomplete results for
        - max_cost: Maximum Levenshtein edit distance to be considered when calculating results
        - size: The max number of results to return
        """
        global time_dict
        toggle_time("search", time_dict)
        word = normalize_node_name(word)
        if not word:
            return []
        key = f'{word}-{max_cost}-{size}'
        result = self._lfu_cache.get(key)
        if result == -1:
            result = list(self._find_and_sort(word, max_cost, size))
            self._lfu_cache.set(key, result)
        toggle_time("search", time_dict)
        format_time(time_dict)
        print(json.dumps(time_dict, sort_keys=True, indent=4))
        time_dict = {}
        return result

    @staticmethod
    def _len_results(results):
        return sum(map(len, results.values()))

    @staticmethod
    def _is_enough_results(results, size):
        return AutoComplete._len_results(results) >= size

    def _is_stop_word_condition(self, matched_words, matched_prefix_of_last_word):
        return (self._full_stop_words and matched_words and matched_words[
            -1] in self._full_stop_words and not matched_prefix_of_last_word)

    def _find(self, word, max_cost, size, call_count=0):
        """
        The search function returns a list of all words that are less than the given
        maximum distance from the target word
        """
        toggle_time("_find", time_dict)
        results = defaultdict(list)
        fuzzy_matches = defaultdict(list)
        rest_of_results = {}
        fuzzy_matches_len = 0

        toggle_time("_find__prefix_autofill", time_dict)
        fuzzy_min_distance = min_distance = INF
        matched_prefix_of_last_word, rest_of_word, new_node, matched_words = self._prefix_autofill(
            word=word)
        toggle_time("_find__prefix_autofill", time_dict)

        last_word = matched_prefix_of_last_word + rest_of_word

        if matched_words:
            results[0] = [matched_words.copy()]
            min_distance = 0
            # under certain condition with finding full stop words, do not bother with finding
            # more matches
            if self._is_stop_word_condition(matched_words, matched_prefix_of_last_word):
                find_steps = [FindStep.start]
                toggle_time("_find", time_dict)
                return results, find_steps
        if len(rest_of_word) < 3:
            find_steps = [FindStep.descendants_only]
            toggle_time("_find__add_descendants_words_to_results", time_dict)
            self._add_descendants_words_to_results(node=new_node, size=size,
                                                   matched_words=matched_words, results=results,
                                                   distance=1)
            toggle_time("_find__add_descendants_words_to_results", time_dict)
        else:
            find_steps = [FindStep.fuzzy_try]
            word_chunks = deque(filter(lambda x: x, last_word.split(' ')))
            new_word = word_chunks.popleft()

            # TODO: experiment with the number here
            # 'in los angeles' gets cut into `in los` so it becomes a closer match to `in lodi`
            # but if the number was bigger, we could have matched with `in los angeles`
            while len(new_word) < 5 and word_chunks:
                new_word = f'{new_word} {word_chunks.popleft()}'
            fuzzy_rest_of_word = ' '.join(word_chunks)

            for _word in self.words:
                if abs(len(_word) - len(new_word)) > max_cost:
                    continue
                dist = levenshtein_distance(new_word, _word)
                if dist < max_cost:
                    fuzzy_matches_len += 1
                    _value = self.words[_word].get(ORIGINAL_KEY, _word)
                    fuzzy_matches[dist].append(_value)
                    fuzzy_min_distance = min(fuzzy_min_distance, dist)
                    if fuzzy_matches_len >= size or dist < 2:
                        break

            if fuzzy_matches_len:
                find_steps.append(FindStep.fuzzy_found)
                if fuzzy_rest_of_word:
                    call_count += 1
                    if call_count < 2:
                        rest_of_results, rest_find_steps = self._find(word=fuzzy_rest_of_word,
                                                                      max_cost=max_cost, size=size,
                                                                      call_count=call_count)
                        find_steps.append({FindStep.rest_of_fuzzy_round2: rest_find_steps})
                for _word in fuzzy_matches[fuzzy_min_distance]:
                    if rest_of_results:
                        rest_of_results_min_key = min(rest_of_results.keys())
                        for _rest_of_matched_word in rest_of_results[rest_of_results_min_key]:
                            results[fuzzy_min_distance].append(
                                matched_words + [_word] + _rest_of_matched_word)
                    else:
                        results[fuzzy_min_distance].append(matched_words + [_word])
                        _matched_prefix_of_last_word_b, not_used_rest_of_word, fuzzy_new_node, _matched_words_b = self._prefix_autofill(
                            word=_word)
                        if self._is_stop_word_condition(matched_words=_matched_words_b,
                                                        matched_prefix_of_last_word=_matched_prefix_of_last_word_b):
                            break
                        self._add_descendants_words_to_results(node=fuzzy_new_node, size=size,
                                                               matched_words=matched_words,
                                                               results=results,
                                                               distance=fuzzy_min_distance)

            if matched_words and not self._is_enough_results(results, size):
                find_steps.append(FindStep.not_enough_results_add_some_descandants)
                total_min_distance = min(min_distance, fuzzy_min_distance)
                self._add_descendants_words_to_results(node=new_node, size=size,
                                                       matched_words=matched_words, results=results,
                                                       distance=total_min_distance + 1)

        toggle_time("_find", time_dict)
        return results, find_steps

    def _prefix_autofill(self, word, node=None):
        len_prev_rest_of_last_word = INF
        matched_words = []
        matched_words_set = set()

        def _add_words(words):
            is_added = False
            for word in words:
                if word not in matched_words_set:
                    matched_words.append(word)
                    matched_words_set.add(word)
                    is_added = True
            return is_added

        matched_prefix_of_last_word, rest_of_word, node, matched_words_part, matched_condition_ever, matched_condition_in_branch = self._prefix_autofill_part(
            word, node)
        _add_words(matched_words_part)
        result = (matched_prefix_of_last_word, rest_of_word, node, matched_words)
        len_rest_of_last_word = len(rest_of_word)

        while len_rest_of_last_word and len_rest_of_last_word < len_prev_rest_of_last_word:
            word = matched_prefix_of_last_word + rest_of_word
            word = word.strip()
            len_prev_rest_of_last_word = len_rest_of_last_word
            matched_prefix_of_last_word, rest_of_word, node, matched_words_part, matched_condition_ever, matched_condition_in_branch = self._prefix_autofill_part(
                word, node=self._dwg, matched_condition_ever=matched_condition_ever,
                matched_condition_in_branch=matched_condition_in_branch)
            is_added = _add_words(matched_words_part)
            if is_added is False:
                break
            len_rest_of_last_word = len(rest_of_word)
            result = (matched_prefix_of_last_word, rest_of_word, node, matched_words)

        return result

    def prefix_autofill_part_condition(self, node):
        pass

    PREFIX_AUTOFILL_PART_CONDITION_SUFFIX = ''

    def _add_to_matched_words(self, node, matched_words, matched_condition_in_branch,
                              matched_condition_ever, matched_prefix_of_last_word):
        if matched_words:
            last_matched_word = matched_words[-1].replace(
                self.PREFIX_AUTOFILL_PART_CONDITION_SUFFIX, '')
            if node.value.startswith(last_matched_word):
                matched_words.pop()
        value = node.value
        if self.PREFIX_AUTOFILL_PART_CONDITION_SUFFIX:
            if self._node_word_info_matches_condition(node, self.prefix_autofill_part_condition):
                matched_condition_in_branch = True
                if matched_condition_ever and matched_prefix_of_last_word:
                    value = f"{matched_prefix_of_last_word}{self.PREFIX_AUTOFILL_PART_CONDITION_SUFFIX}"
        matched_words.append(value)
        return matched_words, matched_condition_in_branch

    def _prefix_autofill_part(self, word, node=None, matched_condition_ever=False,
                              matched_condition_in_branch=False):
        node = node or self._dwg
        que = deque(word)

        matched_prefix_of_last_word = ''
        matched_words = []
        nodes_that_words_were_extracted = set()

        while que:
            char = que.popleft()
            toggle_time("_prefix_autofill_part_each_char", time_dict)

            if node.children:
                if char not in node.children:
                    space_child = node.children.get(' ')
                    if space_child and char in space_child.children:
                        node = space_child
                    else:
                        que.appendleft(char)
                        toggle_time("_prefix_autofill_part_each_char", time_dict)
                        break
                node = node.children[char]
                if char != ' ' or matched_prefix_of_last_word:
                    matched_prefix_of_last_word += char
                if node.word:
                    if que:
                        next_char = que[0]
                        if next_char != ' ':
                            toggle_time("_prefix_autofill_part_each_char", time_dict)
                            continue
                    matched_words, matched_condition_in_branch = self._add_to_matched_words(node, matched_words, matched_condition_in_branch, matched_condition_ever, matched_prefix_of_last_word)
                    nodes_that_words_were_extracted.add(node)
                    matched_prefix_of_last_word = ''
            else:
                if char == ' ':
                    node = self._dwg
                    if matched_condition_in_branch:
                        matched_condition_ever = True
                else:
                    que.appendleft(char)
                    toggle_time("_prefix_autofill_part_each_char", time_dict)
                    break
            toggle_time("_prefix_autofill_part_each_char", time_dict)

        if not que and node.word and node not in nodes_that_words_were_extracted:
            matched_words, matched_condition_in_branch = self._add_to_matched_words(node, matched_words, matched_condition_in_branch, matched_condition_ever, matched_prefix_of_last_word)
            matched_prefix_of_last_word = ''

        rest_of_word = "".join(que)
        if matched_condition_in_branch:
            matched_condition_ever = True

        return (matched_prefix_of_last_word, rest_of_word, node, matched_words,
                matched_condition_ever, matched_condition_in_branch)

    def _add_descendants_words_to_results(self, node, size, matched_words, results, distance,
                                          should_traverse=True):
        descendant_words = list(node.get_descendants_words(size, should_traverse,
                                                           full_stop_words=self._full_stop_words))
        extended = _extend_and_repeat(matched_words, descendant_words)
        if extended:
            results[distance].extend(extended)
        return distance

    def _node_word_info_matches_condition(self, node, condition):
        _word = node.word
        word_info = self.words.get(_word)
        if word_info:
            return condition(word_info)
        else:
            return False

    def get_all_descendent_words_for_condition(self, word, size, condition):
        new_tokens = []

        matched_prefix_of_last_word, rest_of_word, node, matched_words_part, matched_condition_ever, matched_condition_in_branch = self._prefix_autofill_part(
            word=word)
        if not rest_of_word and self._node_word_info_matches_condition(node, condition):
            found_nodes_gen = node.get_descendants_nodes(size,
                                                         insert_count=self.SHOULD_INCLUDE_COUNT)
            for node in found_nodes_gen:
                if self._node_word_info_matches_condition(node, condition):
                    new_tokens.append(node.word)
        return new_tokens

    def update_count_of_word(self, word, count=None, offset=None):
        """
        Update the count attribute of a node in the dwg. This only affects the autocomplete
        object and not the original count of the node in the data that was fed into fast_autocomplete.
        """
        matched_prefix_of_last_word, rest_of_word, node, matched_words_part, matched_condition_ever, matched_condition_in_branch = self._prefix_autofill_part(
            word=word)
        if node:
            if offset:
                with self._lock:
                    node.count += offset
            elif count:
                with self._lock:
                    node.count = count
        else:
            raise NodeNotFound(f'Unable to find a node for word {word}')
        return node.count

    def get_count_of_word(self, word):
        return self.update_count_of_word(word)


class _DawgNode:
    """
    The Dawg data structure keeps a set of words, organized with one node for
    each letter. Each node has a branch for each letter that may follow it in the
    set of words.
    """

    __slots__ = ("_id", "word", "original_key", "children", "count")
    NextId = 0
    def __init__(self):
        self.word = None
        self.original_key = None
        self.children = {}
        self.count = 0
        self._id = _DawgNode.NextId
        _DawgNode.NextId += 1

    def __getitem__(self, key):
        return self.children[key]

    def __repr__(self):
        return f'<DawgNode children={list(self.children.keys())}, {self._id}>'

    @property
    def value(self):
        return self.original_key or self.word

    def insert(self, word, add_word=True, original_key=None, count=0, insert_count=True):
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = _DawgNode()

            node = node.children[letter]

        if add_word:
            node.word = word
            node.original_key = original_key
            if insert_count:
                node.count = int(count)  # converts any str to int
        return node

    def get_descendants_nodes(self, size, should_traverse=True, full_stop_words=None, insert_count=True):
        toggle_time("get_descendants_nodes", time_dict)
        if insert_count is True:
            size = INF

        que = deque()
        unique_nodes = {self}
        found_nodes_set = set()
        full_stop_words = full_stop_words if full_stop_words else set()
        toggle_time("get_descendants_nodes_first_que", time_dict)

        for letter, child_node in self.children.items():
            toggle_time("ResultDawgNode", time_dict)
            toggle_time("ResultDawgNode", time_dict)
            if child_node not in unique_nodes:
                unique_nodes.add(child_node)
                que.append((letter, child_node))
        toggle_time("get_descendants_nodes_first_que", time_dict)

        while que:
            letter, child_node = que.popleft()
            child_value = child_node.value
            if child_value:
                if child_value in full_stop_words:
                    should_traverse = False
                if child_value not in found_nodes_set:
                    found_nodes_set.add(child_value)
                    yield child_node
                    if len(found_nodes_set) > size:
                        break
            toggle_time("get_descendants_nodes_traverse_que", time_dict)

            if should_traverse:
                for letter, grand_child_node in child_node.children.items():
                    toggle_time("get_descendants_nodes_traverse_que_prep", time_dict)
                    toggle_time("ResultDawgNode", time_dict)
                    toggle_time("ResultDawgNode", time_dict)
                    toggle_time("get_descendants_nodes_traverse_que_prep", time_dict)
                    toggle_time("get_descendants_nodes_traverse_que_add", time_dict)
                    if grand_child_node not in unique_nodes:
                        unique_nodes.add(grand_child_node)
                        que.append((letter, grand_child_node))
                    toggle_time("get_descendants_nodes_traverse_que_add", time_dict)
            toggle_time("get_descendants_nodes_traverse_que", time_dict)
        toggle_time("get_descendants_nodes", time_dict)

    def get_descendants_words(
            self, size, should_traverse=True, full_stop_words=None, insert_count=True):
        found_nodes_gen = self.get_descendants_nodes(
            size,
            should_traverse=should_traverse,
            full_stop_words=full_stop_words,
            insert_count=insert_count
        )

        if insert_count is True:
            found_nodes = sorted(
                found_nodes_gen,
                key=lambda node: node.count,
                reverse=True
            )[:size + 1]
        else:
            found_nodes = islice(found_nodes_gen, size)

        return map(lambda word: word.value, found_nodes)

