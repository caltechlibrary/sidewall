Sidewall
=============

_Sidewall_ is a Python library for interacting with the [Dimensions](https://app.dimensions.ai) search API.

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/caltechlibrary/sidewall](https://github.com/caltechlibrary/sidewall)<br>
*License*:      BSD/MIT derivative &ndash; see the [LICENSE](LICENSE) file for more information

☀ Introduction
-----------------------------

Dimensions offers a networked API and search language (the [DSL](https://docs.dimensions.ai/dsl/language.html)).  However, there is as yet no object-oriented API library for Python.  Interacting with the DSL currently requires writing strings and sending them to the Dimensions server, a process that is inconvenient for Python users.  _Sidewall_ is an effort to create a higher level interface for working with the Dimensions DSL and network API.  It wraps network calls and provides Python objects that can be used in programs to interact with Dimensions.

"Sidewall" is a loose acronym for _**Si**mple **D**im**e**nsions **w**rapper **A**PI **l**ibrary_.


✺ Installation instructions
---------------------------

The following is probably the simplest and most direct way to install this software on your computer:
```sh
sudo pip3 install git+https://github.com/caltechlibrary/sidewall.git
```

Alternatively, you can clone this GitHub repository and then run `setup.py`:
```sh
git clone https://github.com/caltechlibrary/sidewall.git
cd sidewall
sudo python3 -m pip install .
```

▶︎ Basic operation
------------------

...forthcoming...

⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/sidewall/issues) for this repository.


☮︎ Copyright and license
---------------------

Copyright (C) 2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
