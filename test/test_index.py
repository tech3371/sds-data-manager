import unittest
from sds_in_a_box.SDSCode.opensearch_utils.index import Index

class TestIndex(unittest.TestCase):

    def test_create(self):
        # need to figure temp create then delete a new index to an
        # open search database
        pass

    def test_repr(self):
        index_name = 'python-test-index3'
        index_body = {
        'settings': {
            'index': {
            'number_of_shards': 4
            }
        }
        }

        my_index = Index(index_name, index_body)

        assert str(my_index) == str({'python-test-index3': {'settings': {'index': {'number_of_shards': 4}}}})

if __name__ == '__main__':
    unittest.main()
