merveilles_io
=============

A flask + kyotocabinet app that lists links posted to it in a timeline like fashion.

Installation
============

Running the development version is relatively simple. You'll need python2, pip
and preferably virtualenvwrapper.

1. Create virtual environment: `mkvirtualenv merveilles`
2. Install requirements: `pip install -r requirements.txt`
3. Install Kyoto Cabinet:

```
    cd dependencies/
    tar -xf kyotocabinet-1.2.76.tar.gz
    cd kyotocabinet-1.2.76
    ./configure
    make
    sudo make install
```

4. Install kyoto cabinet python bindings into your virtual environment

```
    cd dependencies/
    tar -xf ./kyotocabinet-python-1.23.tar.gz
    cd kyotocabinet-python-1.23
    make
    sudo make install
    python setup.py install
```

5. You'll also need [OlegDB](http://olegdb.org/) running to handle user stuff.
We have a multi-database paradigm! Great!
6. Make sure OlegDB is running on the default host/port.
7. Run the dev server: `python src/main.py --debug --db=./merveilles.kct`

Thats pretty much it. Running it in production involves uwsgi and I don't want
to write that up right now.
