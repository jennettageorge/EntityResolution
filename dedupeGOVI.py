#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This code demonstrates the Gazetteer.
We will use one of the sample files from the RecordLink example as the
canonical set.
"""
from __future__ import print_function

import os
import csv
import re
import logging
import optparse
import random
import collections
import dedupe
from unidecode import unidecode
import sys

sys.setrecursionlimit(200000)

# ## Logging

optp = optparse.OptionParser()
optp.add_option('-v', '--verbose', dest='verbose', action='count',
                help='Increase verbosity (specify multiple times for more)'
                )
(opts, args) = optp.parse_args()
log_level = logging.WARNING
if opts.verbose:
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG
logging.getLogger().setLevel(log_level)

# ## Setup

output_file = 'gazetteer_output.csv'
settings_file = 'gazetteer_learned_settings'
training_file = 'gazetteer_training.json'


def preProcess(column):
    """
    Do a little bit of data cleaning with the help of Unidecode and Regex.
    Things like casing, extra spaces, quotes and new lines can be ignored.
    """

    column = unidecode(column)
    column = re.sub('\n', ' ', column)
    column = re.sub('-', '', column)
    column = re.sub('/', ' ', column)
    column = re.sub("'", '', column)
    column = re.sub(",", '', column)
    column = re.sub(":", ' ', column)
    column = re.sub(' +', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column:
        column = None
    return column


def readData(filename):
    """
    Read in our data from a CSV file and create a dictionary of records,
    where the key is a unique record ID.
    """

    data_d = {}

    with open(filename) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            clean_row = dict([(k, preProcess(v)) for (k, v) in row.items()])
            data_d[filename + str(i)] = dict(clean_row)

    return data_d


print('importing data ...')
domain = readData('domain.csv')
print('N data 1 records: {}'.format(len(domain)))

rang = readData('range.csv')
print('N data 2 records: {}'.format(len(rang)))


def names():
    for dataset in (domain, rang):
        for record in dataset.values():
            yield record['name']


if os.path.exists(settings_file):
    print('reading from', settings_file)
    with open(settings_file, 'rb') as sf:
        gazetteer = dedupe.StaticGazetteer(sf)

else:
    # Define the fields the gazetteer will pay attention to
    fields = [
        {'field': 'name', 'type': 'String','has missing': True},
        {'field': 'name', 'type': 'Text', 'corpus': names(),'has missing': True},
        {'field': 'address', 'type': 'Text','has missing': True},
        {'field': 'phone', 'type': 'Text','has missing': True},
        ]

    # Create a new gazetteer object and pass our data model to it.
    gazetteer = dedupe.Gazetteer(fields)

    # If we have training data saved from a previous run of gazetteer,
    # look for it an load it in.
    # __Note:__ if you want to train from scratch, delete the training_file
    if os.path.exists(training_file):
        print('reading labeled examples from ', training_file)
        with open(training_file) as tf:
            gazetteer.prepare_training(domain, rang, training_file=tf)
    else:
        gazetteer.prepare_training(domain, rang)

    # ## Active learning
    print('starting active labeling...')

    dedupe.consoleLabel(gazetteer)

    gazetteer.train()

    # When finished, save our training away to disk
    with open(training_file, 'w') as tf:
        gazetteer.writeTraining(tf)

    # Make the canonical set
    gazetteer.index(rang)

    # Save our weights and predicates to disk.  If the settings file
    # exists, we will skip all the training and learning next time we run
    # this file.
    with open(settings_file, 'wb') as sf:
        gazetteer.writeSettings(sf, index=True)

    gazetteer.cleanupTraining()

gazetteer.index(rang)
# Calculate the threshold
print('Start calculating threshold')
threshold = gazetteer.threshold(domain, recall_weight=1.0)
print('Threshold: {}'.format(threshold))

#we want all entities to get a match, even if they are not great matches, so
#we will set the threshold to 0 for the sake of this project. However, if your
#want to use the threshold that was found by the algorithm for best results,
# set 'threshold =threshold'
results = gazetteer.match(domain, threshold=0, n_matches=1, generator=True)

domain_matches = collections.defaultdict(dict)
for matches in results:
    for (domain_id, range_id), score in matches:
        domain_matches[domain_id][range_id] = score

link_ids = {}
link_id = 0
for range_ids in domain_matches.values():
    for range_id in range_ids:
        if range_id not in link_ids:
            link_ids[range_id] = link_id
            link_id += 1

with open(output_file, 'w') as f:
    writer = csv.writer(f)

    range_file = 'range.csv'
    domain_file = 'domain.csv'


    with open(domain_file) as f_input:
        reader = csv.reader(f_input)
        heading_row = next(reader)
        additional_columns = ['Confidence Score','vendor_id', 'factset_entity_id']
        heading_row = additional_columns
        writer.writerow(heading_row)

        for row_id, row in enumerate(reader):
            record_id = domain_file + str(row_id)
            matches = domain_matches.get(record_id)

            if not matches:
                no_match_row = [domain_file, None, None, record_id] + row
                #writer.writerow(no_match_row)
            else:
                for range_id, score in matches.items():
                    link_row = [score, record_id.replace('domain.csv',''),range_id.replace('range.csv','')]
                    writer.writerow(link_row)
