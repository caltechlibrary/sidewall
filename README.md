Pindu
=============

_Pindu_ is a Python library for interacting with the [Dimensions](https://app.dimensions.ai) search API.

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/caltechlibrary/pindu](https://github.com/caltechlibrary/pindu)<br>
*License*:      BSD/MIT derivative &ndash; see the [LICENSE](LICENSE) file for more information

☀ Introduction
-----------------------------

Dimensions offers a networked API and search language (the [DSL](https://docs.dimensions.ai/dsl/language.html)).  However, there is as yet no object-oriented API library for Python.  Interacting with the DSL currently requires writing strings and sending them to the Dimensions server, a process that is inconvenient for Python users.  _Pindu_ is an effort to create a higher level interface for working with the Dimensions DSL and network API.  It wraps network calls and provides Python objects that can be used in programs to interact with Dimensions.

"Pindu" is an acronym for _**P**rogramming **i**nterface for **n**etworked **D**imensions **u**se_.  (By the way, the pindu is also a [species of fish](https://en.wikipedia.org/wiki/Pindu) that is [critically endangered](http://www.earthsendangered.com/profile.asp?gr=F&sp=4253) due to pollution and other effects due to human activities.)


✺ Installation instructions
---------------------------

The following is probably the simplest and most direct way to install this software on your computer:
```sh
sudo pip3 install git+https://github.com/caltechlibrary/pindu.git
```

Alternatively, you can clone this GitHub repository and then run `setup.py`:
```sh
git clone https://github.com/caltechlibrary/pindu.git
cd pindu
sudo python3 -m pip install .
```

▶︎ Basic operation
------------------

...forthcoming...

⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/pindu/issues) for this repository.


☮︎ Copyright and license
---------------------

Copyright (C) 2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
