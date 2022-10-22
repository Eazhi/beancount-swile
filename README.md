# Beancount Swile

`beancount-swile` is a beancount importer for swile transactions.

## Extract transactions

The script `retrieve_transactions.py` allows you to extract your transactions.

## Installation

```sh
$ pip install beancount-swile
```

## Usage

```python
from beancount_swile import SwileImporter


CONFIG = [SwileImporter("Assets:Swile")]
```
