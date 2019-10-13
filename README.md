# Govini Entity Resolution and Deduplification


One of the problems that we face at Govini is mapping entities between disparate data sets. We collect data from a variety of different sources, and knowing that a certain entity is the same from one data set to another is essential.

For example, there may be a company named "FOO" in one data set, and a company named "foo 123" in another. We need to be able to determine with a high enough confidence that those are the same entity. However, a majority of the time, the data does not share a unique key.

Using the data available, as well as relationships and metadata, we map these together with a high precision. We need you to devise an algorithm that could automatically tie related entities together. The output should have the matches as well as a confidence score for the match.

We are giving you two sample data sets, and it'll be up to you to generate a mapping between the two. In most cases, the mapping should be one to one. An ID from data set A should map to an ID in data set B.

The sample data sets are available at the following link:
https://s3.amazonaws.com/BUCKET_FOR_FILE_TRANSFER/interview.tar.xz

The archive contains five files, described below:

Procurement Data:

data/mdl__dim_vendor.csv - Company Information
data/mdl__dim_geo.csv - Location Information

mdl__dim_vendor.csv references mdl__dim_geo.csv via the column geo_id.

Finance Data:

data/factset__ent_entity_coverage.csv - Company Information
data/factset__ent_entity_structure.csv - Company Hierarchy
data/factset__ent_entity_address.csv - Location Information

All of these files are tied together using factset_entity_id.

The end goal of this exercise is to explore the data, and map mdl__dim_vendor.vendor_id to corresponding factset__ent_entity_coverage.factset_entity_id. Ideally, a file containing three columns: vendor_id, factset_entity_id, confidence_of_match. Please make sure there is a README file that explains how your algorithm works.
