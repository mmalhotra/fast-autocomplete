#!/usr/bin/env python
#
# genericFileInterfaces.py
#
# $Id: genericFileInterfaces.py,v 1.15 2016/05/27 19:14:53 prabhat.gupta Exp $

import copy, os
import codecs
import marshal

from fast_autocomplete.kg import genericMergeLib


def writeFile(outFilename, excepFilename, dataStore, schema, ignoreAttr=None, knockOffData=None,
              mode='w', encoding='utf8'):
    excepFile = genericMergeLib.myfile(excepFilename, 'a')

    try:
        outFile = genericMergeLib.myfile(outFilename, mode, encoding)
    except:
        excepFile.mywrite('ERROR: Input file cannot be opened. filename - %s\n' % outFilename)
        return

    ignoreAttrHash = {}
    if ignoreAttr != None:
        if not isinstance(ignoreAttr, dict):
            ignoreAttrHash = dict.fromkeys(ignoreAttr)
        else:
            ignoreAttrHash = ignoreAttr

    knockOffDataHash = {}
    if knockOffData != None:
        if not isinstance(knockOffData, dict):
            knockOffDataHash = dict.fromkeys(knockOffData)
        else:
            knockOffDataHash = knockOffData

    schemaList = sorted([(i, k) for (k, i) in schema.items() if k not in ignoreAttrHash])
    for key, curTuple in dataStore.items():
        tuple_len = len(curTuple)
        for index, attribute in schemaList:
            if attribute in knockOffDataHash:
                outFile.write('%s: \n' % attribute)
            else:
                if index < tuple_len:
                    outFile.mywrite('%s: %s\n' % (attribute, curTuple[index]))
                else:
                    continue
        # out_str = '\n'.join(['%s: %s' % (a, curTuple[i] if a not in knockOffDataHash else '') for i, a in schemaList if i < tuple_len])
        # outFile.mywrite(out_str+"\n")

    outFile.close()

    excepFile.close()


def writeSingleRecord(out_file, record, schema, encoding='utf8', skip_empty=False, recSeperator=''):
    """
    Write the given record in the file pointer
    """
    field_list = [''] * len(schema)
    for attr, ii in schema.items():
        field_list[ii] = attr
    len_diff = len(field_list) - len(record)
    if len_diff > 0:
        for i in range(len_diff):
            record.append('')
    for index, field in enumerate(field_list):
        value = record[index]
        if skip_empty and not value and index != 0:
            continue
        if isinstance(value, str):
            value = value.encode(encoding)
        if field == "@#":
            out_file.write("@#@\n")
            continue
        out_file.write(field)
        out_file.write(': ')
        out_file.write(value)
        out_file.write('\n')
    if recSeperator:
        out_file.write(recSeperator)
        out_file.write('\n')


def loadPickleFile(inFilename, pickle_suffix, excepFilename, delimAttr='Gi', ignoreAttr=None, \
                   knockOffData=None, addAttr=None, primaryKey='Gi', attr2load=set(),
                   encoding='utf8'):
    # check pickle file
    pickled_file = inFilename + pickle_suffix
    if os.path.exists(pickled_file):
        pickled_f = open(pickled_file, 'r')
        my_data_tuple = marshal.load(pickled_f)
        pickled_f.close()
        my_data, my_schema = my_data_tuple
    else:
        my_data = {}
        my_schema = {}
        loadFile(inFilename, excepFilename, my_data, my_schema, delimAttr, ignoreAttr, knockOffData,
                 addAttr, primaryKey, attr2load, encoding)
        pickled_f = open(pickled_file, 'w')
        my_data_tuple = (my_data, my_schema)
        marshal.dump(my_data_tuple, pickled_f)
        pickled_f.close()

    return (my_data, my_schema)


def get_schema(inFilename, delimAttr='Gi'):
    schema = {delimAttr: 0}

    delim_found = False
    inFile = open(inFilename, 'r')
    for l in inFile:
        attr = l[:2]
        if attr == delimAttr:
            if delim_found == False:
                delim_found = True
            else:
                break
        if delim_found == True:
            if attr not in schema:
                schema[attr] = len(schema)
    inFile.close()

    return schema


def updateRecordInLoadFile(primaryKey, min_record_len, record_data, schema, sorted_schema,
                           dataStore):
    for k in record_data:
        if k not in schema:
            sorted_schema.append((len(schema), k))
            schema[k] = len(schema)
    primaryKeyData = record_data.get(primaryKey, None)
    if primaryKeyData:
        if min_record_len > sorted_schema:
            min_record_len = len(sorted_schema)
        dataStore[primaryKeyData] = [record_data.get(k, '') for (i, k) in sorted_schema]
    record_data.clear()
    return min_record_len


def loadFile(inFilename, excepFilename, dataStore, schema, delimAttr='Gi', ignoreAttr=None,
             knockOffData=None, \
             addAttr=None, primaryKey='Gi', attr2load=set(), encoding='utf8'):
    excepFile = genericMergeLib.myfile(excepFilename, 'a')
    try:
        inFile = open(inFilename, 'r')
    except:
        excepFile.mywrite('ERROR: Input file cannot be opened. filename - %s\n' % inFilename)
        return

    ignoreAttrHash = {}
    if ignoreAttr != None:
        if not isinstance(ignoreAttr, dict):
            ignoreAttrHash = dict.fromkeys(ignoreAttr)
        else:
            ignoreAttrHash = ignoreAttr

    knockOffDataHash = {}
    if knockOffData != None:
        if not isinstance(knockOffData, dict):
            knockOffDataHash = dict.fromkeys(knockOffData)
        else:
            knockOffDataHash = knockOffData

    record_data = {}
    if not schema:
        schema.update(get_schema(inFilename, delimAttr))
    sorted_schema = sorted([(i, k) for (k, i) in schema.items()])
    min_record_len = 5000
    for inputLine in inFile:
        inputLine = inputLine.rstrip('\n').decode(encoding)
        token = inputLine[:2]
        if token in ignoreAttrHash or (attr2load and token not in attr2load):
            continue

        # data = inputLine[4:].strip() if token not in knockOffDataHash else ''
        if token not in knockOffDataHash:
            data = inputLine[4:].strip()
        else:
            data = ''
        if token == delimAttr:
            if len(record_data):
                min_record_len = updateRecordInLoadFile(primaryKey, min_record_len, record_data,
                                                        schema, sorted_schema, dataStore)

        record_data[token] = data

    if len(record_data) > 0:
        min_record_len = updateRecordInLoadFile(primaryKey, min_record_len, record_data, schema,
                                                sorted_schema, dataStore)

    if addAttr != None:
        list(map(lambda x: schema.setdefault(x, len(schema)), addAttr))

    # Adjust the dataStore.
    schema_len = len(schema)
    if min_record_len < schema:
        for record in dataStore.values():
            len_diff = schema_len - len(record)
            if len_diff > 0:
                record.extend([''] * len_diff)

    inFile.close()
    excepFile.close()


def guidLocationIterator(inFilename, schema=None, delimAttr='Gi'):
    f = open(inFilename, 'r')
    oldPos = 0
    for line in f:
        if line[:2] == delimAttr:
            yield (line[4:].strip(), str(oldPos))
        if schema != None:
            schema.setdefault(line[:2], len(schema))
        oldPos += len(line)
    f.close()


def getGuidPositionHash(inFilename, schema, typeslist=None, delimAttr='Gi'):
    data = {}
    types_hash = {}
    f = open(inFilename, 'r')
    oldPos = 0
    last_gid = ''
    for line in f:
        token = line[:2]
        value = line[4:].strip()
        if token == delimAttr:
            last_gid = value
            data[value] = str(oldPos)
        elif typeslist and token == 'Vt' and value in typeslist:
            types_hash.setdefault(value, set()).add(last_gid)
        schema.setdefault(token, len(schema))
        oldPos += len(line)
    f.close()
    return data, types_hash


def getSingleRecord(fh, pos, sorted_schema, encoding='utf-8', delimAttr='Gi'):
    fh.seek(int(pos), 0)  # move to pos from 0

    record = {}
    for l in fh:
        token = l[:2]
        if token == delimAttr:
            if len(record):
                break
        record[token] = l[4:].rstrip('\n').decode(encoding).strip()

    if record:
        return [record.get(k, '') for (i, k) in sorted_schema]

    return None


# When we want to persist the index of input schema, and then append other fields, appendSchema - True will help
def fileIterator(inFilename, schema, delimAttr='Gi', encoding='utf8', appendSchema=False,
                 multi_field_sep=''):
    inFile = open(inFilename, 'r')
    change_schema = not len(schema) or appendSchema

    if not schema:
        schema.update(get_schema(inFilename, delimAttr))
    sorted_schema = sorted([(i, k) for (k, i) in schema.items()])
    schema_len = len(sorted_schema)

    record_data = {}
    for inputLine in inFile:
        inputLine = inputLine.rstrip('\n').decode(encoding)
        token = inputLine[:2]
        data = inputLine[4:].strip()

        if token == delimAttr:
            if len(record_data):
                if change_schema:
                    for k in record_data:
                        if k not in schema:
                            sorted_schema.append((len(schema), k))
                            schema[k] = len(schema)
                    schema_len = len(sorted_schema)
                tuple = [record_data.get(k, '') for (i, k) in sorted_schema]
                send_again_flag = yield tuple
                while send_again_flag:
                    yield None  # To make the send method yield nothing
                    send_again_flag = yield tuple
                if schema_len != len(
                        schema):  # schema is changed outside after yield like in GMRFMerge.py
                    sorted_schema = sorted([(i, k) for (k, i) in schema.items()])
                record_data.clear()

        if multi_field_sep and token in record_data:
            record_data[token] = '%s%s%s' % (record_data[token], multi_field_sep, data)
        else:
            record_data[token] = data

    if len(record_data):
        if change_schema:
            for k in record_data:
                if k not in schema:
                    sorted_schema.append((len(schema), k))
                    schema[k] = len(schema)
        tuple = [record_data.get(k, '') for (i, k) in sorted_schema]
        send_again_flag = yield tuple
        while send_again_flag:
            yield None  # To make the send method yield nothing
            send_again_flag = yield tuple

    inFile.close()


def loadFileWithSeperator(file_name, seperator, field_list, primary_key_index=0, data={}, schema={},
                          encoding='utf-8', ignore_prefix=None):
    """
    here in the file, every record is in single line. every field value is seperated by seperator. Field index is as field_list.
    field_list is list giving field_name for each value in the file. eg. ['Gi', 'Ti']
    """
    my_f = open(file_name, 'r')
    orig_schema = dict([(field_list[index], index) for index in range(len(field_list))])
    if schema:
        new_field_list = [''] * len(schema)
        for key, value in list(schema.items()):
            new_field_list[value] = key
    for line in my_f:
        line = line.strip()
        if not line:
            continue
        line = line.decode(encoding)
        if ignore_prefix and line.startswith(ignore_prefix):
            continue
        record = line.split(seperator)
        try:
            assert len(record) == len(field_list)
        except AssertionError:
            print("AssertionError at: %s" % line.encode(encoding))
        pk = record[primary_key_index]
        if schema:
            # need to make new record acc to schema
            new_record = [record[orig_schema[new_field_list[index]]] for index in
                          range(len(schema))]
            record = new_record
        data[pk] = record
    my_f.close()
    if not schema:
        schema.update(orig_schema)


def iterateWithSeperator(file_name, seperator, field_list, schema={}, encoding='utf-8',
                         ignore_prefix=None):
    """
    """
    my_f = open(file_name, 'r')
    orig_schema = dict([(field_list[index], index) for index in range(len(field_list))])
    new_field_list = []
    if schema:
        new_field_list = [''] * len(schema)
        for key, value in list(schema.items()):
            new_field_list[value] = key
    if not schema:
        schema.update(orig_schema)
    old_line = ''
    for line in my_f:
        line = line[:-1]
        if not line:
            continue
        line = line.decode(encoding)
        if old_line:
            line = old_line + line
            old_line = ''
        if ignore_prefix and line.startswith(ignore_prefix):
            continue
        record = line.split(seperator)
        try:
            assert len(record) == len(field_list)
        except AssertionError:
            print("AssertionError at: %s" % line)
            old_line = line
            continue
        if new_field_list:
            # need to make new record acc to schema
            new_record = [record[orig_schema[new_field_list[index]]] for index in
                          range(len(schema))]
            record = new_record
        yield record
    my_f.close()


def read_genre_map(genre_mapping_file):
    genre_map = {}

    fd = codecs.open(genre_mapping_file, 'r', 'utf8').read()
    for line in fd.splitlines():
        flds = line.strip().split('\t')
        if len(flds) > 1:
            for i in range(len(flds)):
                parent = flds[i].strip()
                for child in flds[i:]:
                    genre_map.setdefault(child.strip(), set([])).add(parent)

    return genre_map


def conceptIterator(concepts_file_path, schema, encoding='utf8', appendSchema=False,
                    skip_header=True):
    change_schema = not len(schema) or appendSchema

    if change_schema:
        for line in open(concepts_file_path):
            if line.strip() == '@#@':
                break
            if line.startswith('@'):
                continue
            if line.startswith('$'):
                token = line[1:3]
                schema.setdefault(token, len(schema))

    for data in fileIterator(concepts_file_path, schema, encoding=encoding):
        if skip_header:  # Skip header
            skip_header = False
            continue
        yield data


def test():
    data = {}
    schema = {}
    for record in fileIterator("test.in", schema):
        guid = record[schema['Gi']]
        data[guid] = record
    writeFile("test.out", 'error.log', data, schema)


if "__main__" == __name__:
    test()

