# UK Local Authority Names and Codes Lookup

Lookup between the many, many different ways of naming and coding UK local authorities.

If you ever try to match UK local authority statistics against each other you'll quickly find your efforts frustrated by inconsistent uses of official codes and different versions of LA names. These lookups are an on-going tool to help translate between these. 

To update this information, update the files in the `source` folder:

* `source\local-authority-info.json` is the core file, with most key relational information. 
* `source\lookups` contains csvs which will be merged on the basis of keys in the main file. This is mostly for lookups between ID schemes. 

Updating these files and pushing to github will trigger a rebuild and test of the output files.

The output files avaliable are:

* `uk_local_authorities.csv` - big lookup table. 
* `lookup_name_to_registry.csv` combines all alternate names into one column to let you quickly match any data and get back a canonical code (which can be checked against the other table to convert to your preferred format). Also combined with this [name lookup](https://github.com/openregister/local-authority-data/edit/master/maps/name.tsv) from openregister for fuller coverage.
* `lookup_gss_to_registry.csv` file converts from present and former GSS LAD codes (which refer to the boundary shape rather than the authority to the canonical code. 
* `lookup_lsoa_to_registry.csv` lookup from lsoa/datazone/soa to *current* local authority. 

## What is 'local-authority-code'

This project originally used the official [local authority registers](https://github.com/openregister/local-authority-data) to provide a canonical three character code and a canonical name for the local authority. This is required because the more common GSS id refers to boundaries rather than legal entities.

The registers are now depricated but the existing three letter codes will continue to be used. Technically these codes are independent of the register (they are BS-6879), but they are less likely to be released quickly and are not widely used anyway.

As such, there is now a seperate 'BS-6879' column that reflects the official code, and the internal 'local-authority-code' where new additions will be assigned a three digit code for use in this register.

As these codes are not widely used in data releases, it feels likely that maintaining continuity for pipelines and datasets produced using this sheet will be more important than the divergence if different codes are then assigned. 

It is annoying and confusing that `local-authority-code` and `BS-6879` columns may become almost but not entirely identical, but this entire project is required because of a series of similarly annoying and confusing problems, so we might just have to live with that. 

## Useful fields

* local-authority-code - internal three character code
* official-name - 'official' local authority name
* overlapping-la - for london and non-metropolitan councils, id of GLA or overlapping county council. 
* alt-name-1 - canonical shorter name
* alt-name-2 - variations on name
* alt-name-3 - variations on name
* gov-uk-slug - slug used for page-urls relevant to a local authority on gov.uk
* gss-code - current standard 9-character ONS code. *
* archaic-gss-code - old codes (changed because of boundary changes) to help with mismatches on some datasets (even recent datasets may use the wrong codes).
* snac - old ONS Standard Names and Codes code
* os - Ordnance Survey code
* old-ons-la-code - old ONS code for local authorities. 
* ofcom - variant on snac authority code used in coding survey responses (for instance in OFCOM's [Connected Nations report](https://www.ofcom.org.uk/research-and-data/infrastructure-research/connected-nations-2015))
* ecode - used in [revenue and accounting documents](https://www.gov.uk/government/collections/local-authority-revenue-expenditure-and-financing)

Additional maps can be found [here](https://github.com/openregister/local-authority-data/tree/master/maps).

*The gss code used for the Greater London Authority is the gss code is for London region - when working from code point open use E18000007 and the NHS_HA_code column.
