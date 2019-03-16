Change log for Sidewall
=======================

Version 1.0.1
-------------

This is a bug-fix release.

* Fixed serious bugs in creating `Researcher` objects from `Author` objects. A previously internal change borked the functionality almost completely.
* Fixed bugs in setting `current_organization` on `Person`, `Author` and `Researcher` objects
* Fixed bugs setting `affiliations` on `Researcher` when derived from `Author` objects
* Updated examples in the top-level [README](README.md) file
* Started a [CHANGES](CHANGES.md) file
