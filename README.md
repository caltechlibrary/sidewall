Sidewall<img width="22%" align="right" src=".graphics/tire-sidewall-wikipedia.svg">
=============

_Sidewall_ is a Python library for interacting with the [Dimensions](https://app.dimensions.ai) search API.  It defines object classes for various Dimensions data types, fetches data incrementally, copes with rate limits, and more, to help working with Dimensions more natural for Python programmers.

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/caltechlibrary/sidewall](https://github.com/caltechlibrary/sidewall)<br>
*License*:      BSD/MIT derivative &ndash; see the [LICENSE](LICENSE) file for more information

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.5+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest version](https://img.shields.io/badge/Latest_version-0.0.1-b44e88.svg?style=flat-square)](http://shields.io)

☀ Introduction
-----------------------------

Dimensions offers a networked API and search language (the [DSL](https://docs.dimensions.ai/dsl/language.html)).  However, there is as yet no object-oriented API library for Python.  Interacting with the DSL currently requires sending a search string to the Dimensions server, then interpreting the JSON results and handling various issues such as iterating to obtain more than 1000 values (which requires the use of multiple queries), staying within API rate limits, and more.  _Sidewall_ is an effort to create a higher-level interface for working more conveniently with the Dimensions DSL and network API.  Features of Sidewall include:

* object classes defined for different Dimensions data entities
* object attribute values filled in automatically behind the scenes
* lists returned as efficient generators that fetch data over the net as needed
* automatic caching of search results for speed and efficiency
* automatic throttling to keep within API rate limits

"Sidewall" is a loose acronym for _**Si**mple **D**im**e**nsions **w**r**a**pper c**l**ient **l**ibrary_.

✺ Installation instructions
---------------------------

The following is probably the simplest and most direct way to install this software on your computer:
```sh
sudo python3 -m pip install git+https://github.com/caltechlibrary/sidewall.git --upgrade
```

Alternatively, you can clone this GitHub repository and then run `setup.py`:
```sh
git clone https://github.com/caltechlibrary/sidewall.git
cd sidewall
sudo python3 -m pip install . --upgrade
```

▶︎ Basic operation
------------------

### Data mappings

**_Person_**

Dimensions doesn't expose an underlying base class for people; instead, it returns unnamed data structures that basically refer to people in different contexts.  Sidewall currently understands two such contexts: authors of publications (when a query uses `return publications`), and "researchers" (when a query uses `return researchers`).  Sidewall introduces a parent class called `Person` because the objects in these two contexts are so similar, and provides two derived classes: `Author` and `Researcher`.  The distinction provided by the derived classes is necessary because **the list of affiliations for an `Author` is relative to a particular publication and may not be all the affiliations that a person has**.  Thus, affiliations for others must be understood in the context of a particular search for publications.

```
           ┌──────────────┐
           │    Person    │
           └──────────────┘
                  ^
        ┌─────────┴──────────┐
┌───────┴──────┐      ┌──────┴───────┐
│    Author    │      │  Researcher  │
└──────────────┘      └──────────────┘
```

The following table describes the fields and how they relate to values returned from Dimensions:

|   Field         | In "return researchers"? | In "return publications"? | Sidewall expanded? |
|-----------------|--------------------------|---------------------------|--------------------|
| `affiliations`  | as `research_orgs`       | y                         | y                  |
| `first_name`    | y                        | y                         | n                  |
| `id`            | y                        | as `researcher_id`        | n                  |
| `last_name`     | y                        | y                         | n                  |
| `orcid`         | as `orcid_id`            | y                         | n                  |

When using a query that ends with `return researchers`, Dimensions only provides identifiers for research organizations.  Sidewall attempts to expand on this result by retrieving additional organization field values.  
It does this on demand the first time calling code accesses the field values rather than all at once, to reduce the number of API calls made to the Dimensions server.


**_Organization_**

The following table describes the fields and how they relate to values returned from Dimensions:

|   Field         | In "return research_orgs"? | In "return publications"? | Sidewall expanded? |
|-----------------|----------------------------|---------------------------|--------------------|
| `acronym`       | y                          | n                         | y                  |
| `city`          | n                          | y                         | n                  |
| `city_id`       | n                          | y                         | n                  |
| `country`       | n                          | y                         | n                  |
| `country_code`  | n                          | y                         | n                  |
| `country_name`  | y                          | n                         | y                  |
| `id`            | y                          | y                         | n                  |
| `name`          | y                          | y                         | n                  |
| `state`         | n                          | y                         | n                  |
| `state_code`    | n                          | y                         | n                  |


**_Publication_**



⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/sidewall/issues) for this repository.


☺︎ Acknowledgments
-----------------------

The [vector artwork](https://commons.wikimedia.org/wiki/File:Tire_code_-_en.svg) of a car tire used as a logo for this repository was created by [Flanker](https://commons.wikimedia.org/wiki/User:F_l_a_n_k_e_r).  It is licensed under the Creative Commons [Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/deed.en) license.

☮︎ Copyright and license
---------------------

Copyright (C) 2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
