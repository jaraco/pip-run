"""
This script demonstrates how RWT facilitates the
simple execution of complex tasks with their
dependencies.

Run this example with ``python -m rwt -- $script``.

It creates a MongoDB instance, and then runs some
assertions against it.

MongoDB must be installed to a typical location or
available on PATH.

As it uses jaraco.mongodb, set MONGODB_HOME to
specify the MongoDB version to use for the ephemeral
instance.

Running this script with RWT leaves no trace of its
execution, other than adding packages to the pip
cache (if available).
"""

__requires__ = [
	'pytest',
	'jaraco.mongodb>=3.10',
]

if __name__ == '__main__':
	# invoke pytest on this script
	import pytest
	import sys
	sys.exit(pytest.main(sys.argv))

import random
import itertools

import pytest
from jaraco.mongodb.testing import assert_covered


@pytest.fixture
def docs_in_db(mongodb_instance):
	"""
	Install 100 records with random numbers
	"""
	conn = mongodb_instance.get_connection()
	coll = conn.test_db.test_coll
	coll.drop()
	coll.create_index('number')
	n_records = 100
	for n in itertools.islice(itertools.count(), n_records):
		doc = dict(
			number=random.randint(0, 2**32-1),
			value='some value',
		)
		conn.test_db.test_coll.insert(doc)
	return coll


def test_records(docs_in_db, mongodb_instance):
	"Test 100 records are present and query is covered"
	# load all the numbers to ensure the index is in RAM
	_hint = 'number_1'
	_filter = {'number': {'$gt': 0}}
	_projection = {'number': True, '_id': False}
	cur = docs_in_db.find(filter=_filter, projection=_projection).hint(_hint)
	assert_covered(cur)

	# consume the cursor for good measure
	docs = list(cur)
	assert len(docs) == 100
