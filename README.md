Sidewall<img width="24%" align="right" src=".graphics/tire-sidewall-wikipedia.svg">
=============

This package has been archived in September, 2024. Much of the functionality of sidewall is now available in the supported [dimcli](https://github.com/digital-science/dimcli) package. Sidewall doesn't support current Dimensions authentication options, and we don't have a good way to test it against the current Dimensions API.

_Sidewall_ is a package for interacting with the [Dimensions](https://app.dimensions.ai) search API.  It provides object classes for Dimensions entities, fetches data incrementally, caches results, copes with rate limits, and more, to make working with Dimensions in Python more natural.  "Sidewall" is a loose acronym for _**Si**mple **D**im**e**nsions **w**r**a**pper c**l**ient **l**ibrary_.

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/caltechlibrary/sidewall](https://github.com/caltechlibrary/sidewall)<br>
*License*:      BSD/MIT derivative &ndash; see the [LICENSE](LICENSE) file for more information

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.5+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest version](https://img.shields.io/badge/Latest_version-1.0.1-b44e88.svg?style=flat-square)](http://shields.io)
[![DOI](http://img.shields.io/badge/DOI-10.22002%20%2f%20D1.1210-blue.svg?style=flat-square)](https://data.caltech.edu/records/1210)


🏁 Log of recent changes
-----------------------

_Version 1.0.1_: This is a significant bug-fix release.

* Fixed serious bugs in creating `Researcher` objects from `Author` objects.
* Fixed bugs in setting `current_organization` on `Person`, `Author` and `Researcher` objects
* Fixed bugs setting `affiliations` on `Researcher` when derived from `Author` objects
* Updated examples in the top-level [README](README.md) file
* Started a [CHANGES](CHANGES.md) file


Table of Contents
-----------------

* [Introduction](#-introduction)
* [Installation instructions](#-installation-instructions)
* [Using Sidewall](#︎-using-sidewall)
   * [Basic setup and use](#basic-setup-and-use)
   * [Basic principles of running queries](#basic-principles-of-running-queries)
   * [Data mappings](#data-mappings)
      * [`Person`](#person), with subclasses `Authors` and `Researchers`
      * [`Organization`](#organization)
      * [`Publication`](#publication)
      * [`Grant`](#grant)
      * [`Journal`, `Category`, `City`, `Country`, `State`](#journal-category-city-country-state)
      * [Unsupported Dimensions data types](#unsupported-dimensions-data-types)
* [Getting help and support](#-getting-help-and-support)
* [Acknowledgments](#︎-acknowledgments)
* [Copyright and license](#︎-copyright-and-license)


☀ Introduction
-----------------------------

[Dimensions](https://app.dimensions.ai) offers a networked API and search language (the [DSL](https://docs.dimensions.ai/dsl/language.html)).  However, interacting with the DSL currently requires sending a search string to the Dimensions server, then interpreting the JSON results and handling various issues such as iterating to obtain more than 1000 values (which requires the use of multiple queries), staying within API rate limits, and more.  _Sidewall_ ("**Si**mple **D**im**e**nsions **w**r**a**pper c**l**ient **l**ibrary") provides a higher-level interface for working more conveniently with the Dimensions DSL and network API.  Features of Sidewall include:

* object classes for different Dimensions data entities
* lazy object values filled in automatically behind the scenes
* results iterator fetches data over the net as needed
* automatic caching of search results for speed and efficiency
* automatic throttling to keep within API rate limits

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

▶︎ Using Sidewall
----------------

Sidewall is meant to be used from other programs; it does not provide a standalone command-line interface or graphical user interface.  At this time, Sidewall only supports certain kinds of Dimensions queries as discussed below.


### Basic setup and use

To use Sidewall, import the package and the symbol `dimensions` in your Python code:

```python
import sidewall
from sidewall import dimensions
```

In case of problems, it may be useful to turn on debugging in Sidewall to see everything that is happening behind the scenes.  You can do that by using `set_debug()` after importing Sidewall:

```python
sidewall.set_debug(True)
```

To run queries, you will need first to have an [account with Dimensions](https://plus.dimensions.ai/support/solutions/articles/23000013103-how-can-i-get-an-individual-login-for-dimensions-and-what-can-i-do-with-this-).  There are multiple ways of supplying user credentials to Sidewall.  The most secure and more convenient way is to invoke the `login()` method without any arguments:

```python
dimensions.login()
```

When done this way, Sidewall will use the operating system's keyring/keychain functionality (via [keyring](https://github.com/jaraco/keyring)) to get the user name and password.  If the information does not exist from a previous call to `dimensions.login()`, Sidewall will ask you for the user name and password interactively, and then store it in the keyring/keychain for next time.

If asking the user for credentials interactively on the command line is unsuitable for the application you are writing, you can also supply a user name and password to the `login()` method as keyword arguments:

```python
dimensions.login(username = 'somelogin', password = 'somepassword')
```


### Basic principles of running queries

Sidewall defines a method, `query()`, which you can use to run a search in Dimensions and get back results.  The method takes a single argument, a string.  Here is an example:

```python
results = dimensions.query('search publications for "SBML" return publications')
```

The form of the search query string that Sidewall can use is limited in ways described shortly.  The `query()` method returns an object that acts as a Python [iterator](https://docs.python.org/3.5/tutorial/classes.html#iterators)&mdash;you can iterate over the results, use `len()`, and do other operations.

The items returned by the iterator will be Sidewall objects of the kind discussed in the section below on [Data mappings]().  The specific classes of objects returned will correspond to the type of record expressed in the tail end of the query handed to `query()`.  For example, a query that ends in `return publications` will produce Sidewall `Publications` objects; a query that ends in `return researchers` will produce Sidewall `Researcher` objects; and so on.

Sidewall currently puts the following limitations on the form of the query search string:
* it must begin with `search`
* it must end with `return publications`, `return researchers`, or `return grants`
* it must only return a single type of thing (i.e., researchers _or_ publications _or_ grants)
* it must not put facet specifiers or limits on the returned results
* it must not use aggregation or other advanced DSL features

The following is a complete example of using Sidewall to search for publications containing thes string "SBML", and then printing the year and DOI for each such publication found:

```python
import sidewall
from sidewall import dimensions

dimensions.login()
results = dimensions.query('search publications for "SBML" return publications')

print('Total found: {}'.format(len(results)))
for pub in results:
    print('{}: {}'.format(pub.year, pub.doi))
```


### Data mappings

Sidewall defines object classes such as `Researcher`, `Publication`, and a few others to represent the different types of entities returned as the results of a Dimensions search query.  Sidewall's objects attempt to smooth over some of the confusing aspects of the data representations in Dimensions by providing single objects that consolidate different fields and facets of the same underlying "thing".  Further, the fields of an object sometimes are not available from a given query Dimensions performed by the user but _may_ be available if a _different_ kind of query is performed; Sidewall uses this knowledge in some cases to expand object field values automatically and behind the scenes as needed.

The following data classes are defined by Sidewall at this time; note that this is not all the types of data that Dimensions provides today, but future work may improve Sidewall's coverage.

* `Person`, with subclasses `Authors` and `Researchers`
* `Organization`
* `Publication`
* `Journal`
* `Grant`
* several very simple objects: `Category`, `City`, `Country`, `State`


#### `Person`

Dimensions doesn't expose an underlying base class for people; instead, it returns unnamed data structures that basically refer to people in different contexts.  Sidewall currently understands two such contexts: authors of publications (when a query uses `return publications`), and "researchers" (when a query uses `return researchers` or objects such as `Grant` contain "researchers" as a data field).  Sidewall introduces a parent class called `Person` because the objects in these two contexts are so similar, and provides two derived classes: `Author` and `Researcher`.  Both of the derived classes have the same fields.  The distinction provided by the derived classes is necessary because **the list of affiliations for an `Author` is relative to a particular publication and may not be all the affiliations that a person has**.  Thus, affiliations for authors must be understood in the context of a particular search for publications.  The use of two classes indicates the context, so that callers can correctly interpret the list of affiliations.

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

|   Field                | Type                   | In `return researchers`? | In `return` `publications`?      | In `return grants`? | Exp.? |
|------------------------|------------------------|--------------------------|--------------------------------|---------------------|---------|
| `affiliations`         | [`Organization`,&nbsp;...]  | via `research_orgs`      | ✓                              | ✓                   | ✓       |
| `current_organization` | `Organization`         | n                        | via `current_organization_id`  | n                   | ✓       |
| `first_name`           | string                 | ✓                        | ✓                              | ✓                    | n       |
| `middle_name`          | string                 | n                        | n                              | ✓                   | n       |
| `id`                   | string                 | ✓                        | as `researcher_id`             | ✓                   | n       |
| `last_name`            | string                 | ✓                        | ✓                              | ✓                    | n       |
| `orcid`                | string                 | as `orcid_id`            | ✓                              | `orcid_id`          | ✓       |
| `role`                 | string                 | n                        | n                              | ✓                   | n       |

("Exp." &rArr; filled or expanded by Sidewall via search if needed.)

The `affiliations` field in Sidewall's `Person` (and consequently `Author` and `Researcher`) is a list of `Organization` class objects (see below).  Although affiliations as returned by Dimensions are sparse when using a query that ends with `return researchers` (they consist only of organization identifiers), Sidewall hides this by providing complete `Organization` objects for the `affiliations` field of a `Person`, and using behind-the-scenes queries to Dimensions to fill out the organization info when the object field values are accessed.  Thus, calling programs do not need to do anything to get organization details in a result regardless of whether they use `return publications` or `return researchers`&mdash;Sidewall always provides `Organization` class objects and handles getting the field values automatically.

To make data access more uniform, Sidewall also replaces the field `current_organization_id` (which in Dimensions is a string, the identifier of an organization) with the field `current_organization`.  Its value is an `Organization` object corresponding to the organization whose identifier is found in `current_organization_id`.

`Author` class objects are returned when returning publication results, and in those cases, the list of a person's affiliations will reflect their affiliations with respect to a particular publication.  However, sometimes it's convenient to get more information about an author, such as the complete list of affiliations that Dimensions has for the person in question.  Sidewall allows you to create a `Researcher` object out of an `Author` object for that reason.  Here is an example to illustrate the differences between authors and researchers and how you can convert the former to the latter:

```python
>>> import sidewall
>>> from sidewall import dimensions, Researcher
>>> dimensions.login()
>>> pubs = dimensions.query('search publications in title_only for "SBML" where year=2003 return publications')
>>> pub = next(pubs)
>>> author1 = pub.authors[0]
>>> author1
<Author ur.0665132124.52>
>>> author1.affiliations
[]
>>> researcher1 = Researcher(author1)
>>> researcher1.affiliations
[<Organization grid.20861.3d>, <Organization grid.10392.39>, <Organization grid.214458.e>]
```

Finally, note that the field `role` is present for `Researcher` objects listed only in the context of `Grant` results.  Its value is not filled in other contexts.


#### `Organization`

Sidewall uses the object class `Organization` to represent an organization in results returned by Dimensions.  In Sidewall, the set of fields possessed by an `Organization` is the union of all fields that Dimensions provides in different contexts for organizations.  The following table describes the fields and how they relate to values returned from Dimensions:

|   Field         | Type   | In "return research_orgs"? | In "return publications"? | Sidewall filled? |
|-----------------|--------|----------------------------|---------------------------|--------------------|
| `acronym`       | string | ✓                          | n                         | ✓                  |
| `city`          | string | n                          | ✓                         | n                  |
| `city_id`       | string | n                          | ✓                         | n                  |
| `country`       | string | n                          | ✓                         | n                  |
| `country_code`  | string | n                          | ✓                         | n                  |
| `country_name`  | string | ✓                          | n                         | ✓                  |
| `id`            | string | ✓                          | ✓                         | n                  |
| `name`          | string | ✓                          | ✓                         | n                  |
| `state`         | string | n                          | ✓                         | n                  |
| `state_code`    | string | n                          | ✓                         | n                  |

Dimensions returns different field values in different contexts.  For example, the information about organizations included in an author's affiliation list in a publication is somewhat different from what is provided if a search ending in `return research_orgs` is used.  Sidewall makes the assumption that an organization with a given organization identifier ("grid id") is the same organization no matter the context in which it is mentioned in a search result, and so Sidewall smooths over the field differences and, as with `Researcher` and `Author`, queries Dimensions behind the scenes to get missing values when it can (and when they exist).


#### `Publication`

The `Publication` object class is mostly unchanged from the Dimensions publication entity, but in Dimensions, different fields are exposed depending on the type of publication and whether fieldset modifiers are being used.  (The available fieldsets for publications are `basics`, `extras`, and `book`.)  Sidewall's `Publication` object class contains all possible fields, but the values of some fields may not be filled in depending on the type of publication in question.  For example, journals will not have a value for `book_doi`.  The following table describes the fields in `Publication` objects:


| Field                        | Type            | In `return publications`? |
|------------------------------|-----------------|---------------------------|
| `altmetric`                  | string          | ✓
| `authors`                    | [`Author`, ...] | via `author_affiliations` |
| `author_affiliations`        | [`Author`, ...] | via `author_affiliations` |
| `book_doi`                   | string          | ✓
| `book_series_title`          | string          | ✓
| `book_title`                 | string          | ✓
| `date`                       | string          | ✓
| `date_inserted`              | string          | ✓
| `doi`                        | string          | ✓
| `field_citation_ratio`       | string          | ✓
| `id`                         | string          | ✓
| `issn`                       | string          | ✓
| `issue`                      | string          | ✓
| `journal`                    | `Journal`       | ✓
| `linkout`                    | string          | ✓
| `mesh_terms`                 | string          | ✓
| `open_access`                | string          | ✓
| `pages`                      | string          | ✓
| `pmcid`                      | string          | ✓
| `pmid`                       | string          | ✓
| `proceedings_title`          | string          | ✓
| `publisher`                  | string          | ✓
| `references`                 | string          | ✓
| `relative_citation_ratio`    | string          | ✓
| `research_org_country_names` | string          | ✓
| `research_org_state_names`   | string          | ✓
| `supporting_grant_ids`       | string          | ✓
| `times_cited`                | string          | ✓
| `title`                      | string          | ✓
| `type`                       | string          | ✓
| `volume`                     | string          | ✓
| `year`                       | string          | ✓

Sidewall's `Publication` objects use a list of `Author` objects to represent authors, and introduce an alias called `authors` for the field `author_affiliations`.  The latter alias is for convenience and an attempt to bring more intuitiveness to the structure of publications records.  (The name `author_affiliations` in the Dimensions data is potentially confusing because the name suggests it may be a list of organizations rather than a list of authors.  Providing a field named `authors` removes this ambiguity.)


#### `Grant`

The `Grant` object in Sidewall maps directly to the entity representing grants in Dimensions.  The fields in `Grants` are all identical to the Dimensions results, and use lists of other objects where appropriate.  For example, the `funders` field is created as a list of `Organization` objects.

| Field                      | Type                  |
|----------------------------|-----------------------|
| `FOR`                      | [`Category`, ...]     |
| `FOR_first`                | [`Category`, ...]     |
| `HRCS_HC`                  | [`Category`, ...]     |
| `HRCS_RAC`                 | [`Category`, ...]     |
| `RCDC`                     | [`Category`, ...]     |
| `abstract`                 | string                |
| `active_year`              | [`int`, ...]          |
| `date_inserted`            | string                |
| `end_date`                 | string                |
| `funder_countries`         | [`Country`, ...]      |
| `funders`                  | [`Organization`, ...] |
| `funding_aud`              | `float`               |
| `funding_cad`              | `float`               |
| `funding_chf`              | `float`               |
| `funding_eur`              | `float`               |
| `funding_gbp`              | `float`               |
| `funding_jpy`              | `float`               |
| `funding_usd`              | `float`               |
| `funding_org_acronym`      | string                |
| `funding_org_city`         | string                |
| `funding_org_name`         | string                |
| `id`                       | string                |
| `language`                 | string                |
| `linkout`                  | string                |
| `original_title`           | string                |
| `project_num`              | string                |
| `research_org_cities`      | [`City`, ...]         |
| `research_org_countries`   | [`Country`, ...]      |
| `research_org_name`        | string                |
| `research_org_state_codes` | [`State`, ...]        |
| `research_orgs`            | [`Organization`, ...] |
| `researchers`              | [`Researcher`, ...]   |
| `start_date`               | string                |
| `start_year`               | `int`                 |
| `title`                    | string                |
| `title_language`           | string                |

The Dimensions data fields in grant entities have an anomaly in that `funding_org_city` is a string, but cities in another field (`research_org_cities`) are represented as structured objects.  The `Grant` object in Sidewall does not smooth over this inconsistency in its current version, although perhaps it should in a future release.


#### `Journal`, `Category`, `City`, `Country`, `State`

Rounding out the classes implemented in Sidewall are a small number of very simple classes used to store data that Dimensions returns in structured form: `Journal`, `Category`, `City`, `Country`, `State`.  They are all basically identical, each containing only two static fields having string values.  In the case of `Journal` one of the fields is named differently (`title` versus `name` for the others).  More specifically, `Journal` has the following form:

| Field | Type   | In `return publications`? |
|-------|--------|---------------------------|
| id    | string | ✓                         |
| title | string | ✓                         |

All of the other classes (`Category`, `City`, `Country`, `State`) have the following form:

| Field | Type   |
|-------|--------|
| id    | string |
| name  | string |


#### Currently unsupported Dimensions data types

As of this version, Sidewall does not offer support for representing Dimensions policy and patent entities.  This is purely due to resource constraints and not due to an inherent limitation in the Sidewall design.  Future development could easily add new object classes to support these other data entities.


⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/sidewall/issues) for this repository.


☺︎ Acknowledgments
-----------------------

The [vector artwork](https://commons.wikimedia.org/wiki/File:Tire_code_-_en.svg) of a car tire used as a logo for this repository was created by [Flanker](https://commons.wikimedia.org/wiki/User:F_l_a_n_k_e_r).  It is licensed under the Creative Commons [Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/deed.en) license.

Sidewall makes use of numerous open-source packages, without which it would have been effectively impossible to develop Sidewall with the resources we had.  We want to acknowledge this debt.  In alphabetical order, the packages are:

* [humanize](https://github.com/jmoiron/humanize) &ndash; print numbers in a human-friendly format
* [keyring](https://github.com/jaraco/keyring) &ndash; access the system keyring service from Python
* [requests](http://docs.python-requests.org) &ndash; an HTTP library for Python
* [setuptools](https://github.com/pypa/setuptools) &ndash; library for `setup.py`
* [urllib3](https://urllib3.readthedocs.io/en/latest/) &ndash; HTTP client library for Python
* [validators](https://github.com/kvesteri/validators) &ndash; data validation package for Python


☮︎ Copyright and license
---------------------

Copyright (C) 2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
