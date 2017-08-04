<a href="http://sophia.systems/"><img src="http://media.charlesleifer.com/blog/photos/sophia-logo.png" width="215px" height="95px" /></a>

`sophy`, fast Python bindings for [Sophia embedded database](http://sophia.systems), v2.2.

About sophy:

* Written in Cython for speed and low-overhead
* Clean, memorable APIs
* Extensive support for Sophia's features
* Python 2 **and** Python 3 support
* No 3rd-party dependencies besides Cython

About Sophia:

* Ordered key/value store
* Keys and values can be composed of multiple fieldsdata-types
* ACID transactions
* MVCC, optimistic, non-blocking concurrency with multiple readers and writers.
* Multiple databases per environment
* Multiple- and single-statement transactions across databases
* Prefix searches
* Automatic garbage collection and key expiration
* Hot backup
* Compression
* Multi-threaded compaction
* `mmap` support, direct I/O support
* APIs for variety of statistics on storage engine internals
* BSD licensed

Some ideas of where Sophia might be a good fit:

* Running on application servers, low-latency / high-throughput
* Time-series
* Analytics / Events / Logging
* Full-text search
* Secondary-index for external data-store

Limitations:

* Not tested on Windoze.

If you encounter any bugs in the library, please [open an issue](https://github.com/coleifer/sophy/issues/new), including a description of the bug and any related traceback.

## Installation

The [sophia](http://sophia.systems) sources are bundled with the `sophy` source
code, so the only thing you need to install is [Cython](http://cython.org). You
can install from [GitHub](https://github.com/coleifer/sophy) or from
[PyPI](https://pypi.python.org/pypi/sophy/).

Pip instructions:

```console
$ pip install Cython
$ pip install sophy
```

Git instructions:

```console
$ pip install Cython
$ git clone https://github.com/coleifer/sophy
$ cd sophy
$ python setup.py build
$ python setup.py install
```

## Overview

Sophy is very simple to use. It acts like a Python `dict` object, but in
addition to normal dictionary operations, you can read slices of data that are
returned efficiently using cursors. Similarly, bulk writes using `update()` use
an efficient, atomic batch operation.

Despite the simple APIs, Sophia has quite a few advanced features. There is too
much to cover everything in this document, so be sure to check out the official
[Sophia storage engine documentation](http://sophia.systems/v2.2/).

The next section will show how to perform common actions with `sophy`.

## Using Sophy

Let's begin by import `sophy` and creating an environment. The environment
can host multiple databases, each of which may have a different schema. In this
example our database will store arbitrary binary data as the key and value.
Finally we'll open the environment so we can start storing and retrieving data.

```python
from sophy import Sophia, Schema, StringIndex

# Instantiate our environment by passing a directory path which will store the
# various data and metadata for our databases.
env = Sophia('/path/to/store/data')

# We'll define a very simple schema consisting of a single binary value for the
# key, and a single binary value for the associated value.
schema = Schema(key_parts=[StringIndex('key')],
                value_parts=[StringIndex('value')])

# Create a key/value database using the schema above.
db = env.add_database('example_db', schema)

if not env.open():
    raise Exception('Unable to open Sophia environment.')
```

### CRUD operations

Sophy databases use the familiar `dict` APIs for CRUD operations:

```python

db['name'] = 'Huey'
db['animal_type'] = 'cat'
print db['name'], 'is a', db['animal_type']  # Huey is a cat

'name' in db  # True
'color' in db  # False

db['temp_val'] = 'foo'
del db['temp_val']
print db['temp_val']  # raises a KeyError.
```

Use `update()` for bulk-insert, and `multi_get()` for bulk-fetch. Unlike
`__getitem__()`, calling `multi_get()` with a non-existant key will not raise
an exception and return `None` instead.

```python
db.update(k1='v1', k2='v2', k3='v3')

for value in db.multi_get('k1', 'k3', 'kx'):
    print value
# v1
# v3
# None
```

### Other dictionary methods

Sophy databases also provides efficient implementations for  `keys()`,
`values()` and `items()`. Unlike dictionaries, however, iterating directly over
a Sophy database will return the equivalent of the `items()` (as opposed to the
just the keys):

```python

db.update(k1='v1', k2='v2', k3='v3')

list(db)
# [('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')]


db.items()
# same as above.


db.keys()
# ['k1', 'k2', 'k3']


db.values()
# ['v1', 'v2', 'v3']
```

There are two ways to get the count of items in a database. You can use the
`len()` function, which is not very efficient since it must allocate a cursor
and iterate through the full database. An alternative is the `index_count`
property, which may not be exact as it includes transactional duplicates and
not-yet-merged duplicates.

```python

print len(db)
# 4

print db.index_count
# 4
```

### Fetching ranges

Because Sophia is an ordered data-store, performing ordered range scans is
efficient. To retrieve a range of key-value pairs with Sophy, use the ordinary
dictionary lookup with a `slice` instead.

```python

db.update(k1='v1', k2='v2', k3='v3', k4='v4')


# Slice key-ranges are inclusive:
db['k1':'k3']
# [('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')]


# Inexact matches are fine, too:
db['k1.1':'k3.1']
# [('k2', 'v2'), ('k3', 'v3')]


# Leave the start or end empty to retrieve from the first/to the last key:
db[:'k2']
# [('k1', 'v1'), ('k2', 'v2')]

db['k3':]
# [('k3', 'v3'), ('k4', 'v4')]


# To retrieve a range in reverse order, use the higher key first:
db['k3':'k1']
# [('k3', 'v3'), ('k2', 'v2'), ('k1', 'v1')]
```

To retrieve a range in reverse order where the start or end is unspecified, you
can pass in `True` as the `step` value of the slice to also indicate reverse:

```python

db[:'k2':True]
# [('k2', 'k1'), ('k1', 'v1')]

db['k3'::True]
# [('k4', 'v4'), ('k3', 'v3')]

db[::True]
# [('k4', 'v4'), ('k3', 'v3'), ('k2', 'v2'), ('k1', 'v1')]
```

### Cursors

For finer-grained control over iteration, or to do prefix-matching, Sophy
provides a cursor interface.

The `cursor()` method accepts 5 parameters:

* `order` (default=`>=`) -- semantics for matching the start key and ordering
  results.
* `key` -- the start key
* `prefix` -- search for prefix matches
* `keys` -- (default=`True`) -- return keys while iterating
* `values` -- (default=`True`) -- return values while iterating

Suppose we were storing events in a database and were using an
ISO-8601-formatted date-time as the key. Since ISO-8601 sorts
lexicographically, we could retrieve events in correct order simply by
iterating. To retrieve a particular slice of time, a prefix could be specified:

```python

# Iterate over events for July, 2017:
for timestamp, event_data in db.cursor(key='2017-07-01T00:00:00',
                                       prefix='2017-07-'):
    do_something()
```

### Transactions

TODO

## Multi-field keys and values

TODO

## Configuring and Administering Sophia

TODO
