# Govini Entity Resolution and Deduplification

## Assignment

We collect data from a variety of different sources, and knowing that a certain entity is the same from one data set to another is essential.

For example, there may be a company named "FOO" in one data set, and a company named "foo 123" in another. We need to be able to determine with a high enough confidence that those are the same entity. However, a majority of the time, the data does not share a unique key.

Using the data available, as well as relationships and metadata, we map these together with a high precision. We need you to devise an algorithm that could automatically tie related entities together. The output should have the matches as well as a confidence score for the match.

We are giving you two sample data sets, and it'll be up to you to generate a mapping between the two. In most cases, the mapping should be one to one. An ID from data set A should map to an ID in data set B.

The sample data sets are available at the following link:
https://s3.amazonaws.com/BUCKET_FOR_FILE_TRANSFER/interview.tar.xz

The archive contains five files, described below:

<b>Procurement Data:</b>

- data/mdl__dim_vendor.csv - Company Information
- data/mdl__dim_geo.csv - Location Information

mdl__dim_vendor.csv references mdl__dim_geo.csv via the column geo_id.

<b>Finance Data:</b>

- data/factset__ent_entity_coverage.csv - Company Information
- data/factset__ent_entity_structure.csv - Company Hierarchy
- data/factset__ent_entity_address.csv - Location Information

All of these files are tied together using factset_entity_id.
The end goal of this exercise is to explore the data, and map mdl__dim_vendor.vendor_id to corresponding factset__ent_entity_coverage.factset_entity_id. Ideally, a file containing three columns: vendor_id, factset_entity_id, confidence_of_match. Please make sure there is a README file that explains how your algorithm works.

## Algorithm

For this project, we will be implementing [Dedupe](https://github.com/dedupeio/dedupe), a python library used for entity resolution and deduplification. Dedupe relies on string metrics, in particular the Affice Gap Distance (a variation of thE popular Hamming Distance), to find matches in entities.

The nice thing about dedupe is that it allows you to seemlessly choose the columns of your dataframe which you want to be considered in the resolution process. The dedupe algorithm compares each field individually instead of concatenating together, which gives the advantage of adding weights to columns that are more relevant to matching using regularized logistic regression. Naively, I chose to use name, address, phone since these were 3 reliable fields that both datasets contained and they are unique enough to supply insight into the entity resolution. If given more time, I could have played around with feature extraction better but due to lack of time, this seemed like a good subset of features to start with.

The secret sauce of dedupe is the active learning process:
>In order to learn the field weights, Dedupe.io needs example pairs with labels. Most of the time, we will need people to supply those labels. To reduce the amount of time that labeling takes, we use an approach called active learning.
>With active learning, Dedupe.io keeps track of unlabeled pairs and their currently learned weights. At any time, there will be a record pair Dedupe.io will believe have a near a 50% chance of being a duplicate or distinct. By always asking you to label the record pair Dedupe.io is least certain about, we will learn the most we possibly can about your dataset for each training pair.

## Pipeline
 Dedupe uses python logging to show or suppress verbose output. Added for convenience.  To enable verbose logging, run `python examples/csv_example/csv_example.py -v`.

#### Step 1 `preProcess(column)`:
Do a little bit of data cleaning with the help of Unidecode and Regex.Things like casing, extra spaces, quotes and new lines can be ignored.


#### Step 2: `readData(filename)`
Read in our data from a CSV file and create a dictionary of records, where the key is a unique record ID.

#### Step 3: `Gazetteer = dedupe.Gazetteer(settingsfile)`
Create a new gazetteer object and pass our data model to it.

If we have training data saved from a previous run of gazetteer, look for it an load it in.
<b> Note: if you want to train from scratch, delete the training_file </b>
`gazetteer.prepare_training`

#### Step 4: Active Learning: `gazetteer.train`
Dedupe will find the next pair of records it is least certain about and ask you to label them as matches or not. Use 'y', 'n' and 'u' keys to flag duplicates press 'f' when you are finished.

#### Step 5:
Save our weights and predicates to disk.  If the settings file exists, we will skip all the training and learning next time we run this file.

#### Step 6: Calculate Threshold
```Python
threshold = gazetteer.threshold(domain, recall_weight=1.0)
```

we want all entities to get a match, even if they are not great matches, so we will set the threshold to 0 for the sake of this project. However, if your want to use the threshold that was found by the algorithm for best results, set `threshold =threshold`

`results = gazetteer.match(domain, threshold=0, n_matches=1, generator=True)`

#### Step 7: Write to disk

## How to Run

This process takes upwards of 7 hours to run.

You have 2 options. I have supplied you with my `gazetteer_learned_settings` and `gazetteer_training.json` data. If you want to run the model with my learned settings, then run:
```consoleLabel
 cd govinidata
pip install dedupe
pip install unidecode
python dedupeGOVI.py
```

and wait for it to finish training. However, you have the option to train the model yourself if you want to see how it works. To do so, delete these two files and run the above code in command line. This will prompt you to train the model by asking you to use 'y','n', and 'u' keys to flag duplicates for active learning, it is recommended to flag at least 10 yes and 10 no for best results.

<i>Note: I preprocessed the two datasets (basic merging and feature extraction) into the files "domain.csv" and "range.csv", included in the git repo, and these are the files that will be be fed into the algorithm.</i>
