import unittest
from sds_in_a_box.SDSCode.opensearch_utils.index import Index

class TestIndex(unittest.TestCase):

    def test_get_name(self):
        ## Arrange ##
        index_name_true = 'python-test-index3'
        index_body = {
        'settings': {
            'index': {
            'number_of_shards': 4
            }
        }
        }
        index = Index(index_name_true, index_body)

        ## Act ##
        index_name_out = index.get_name()

        ## Assert ##
        assert index_name_true == index_name_out

    def test_get_body(self):
        ## Arrange ##
        index_name = 'python-test-index3'
        index_body_true = {
        'settings': {
            'index': {
            'number_of_shards': 4
            }
        }
        }
        index = Index(index_name, index_body_true)

        ## Act ##
        index_body_out = index.get_body()

        ## Assert ##
        assert index_body_true == index_body_out

    
    def test_validate_index(self):
        ## Arrange ##
        index_name = 'python-test-index3'
        index_body = {
        'settings': {
            'index': {
            'number_of_shards': 4
            }
        }
        }
        index_true = Index(index_name, index_body)

        ## Act ##
        index_out = Index.validate_index(index_true)

        ## Assert ##
        assert index_true == index_out

    def test_validate_index_error(self):
        ## Arrange ##
        index = "string, not an Index"

        ## Act / Assert ##
        self.assertRaises(TypeError, Index.validate_index, index)

    def test_repr(self):
        ## Arrange ##
        index_name = 'python-test-index3'
        index_body = {
        'settings': {
            'index': {
            'number_of_shards': 4
            }
        }
        }
        my_index = Index(index_name, index_body)
        index_string_true = str({'python-test-index3': {'settings': {'index': {'number_of_shards': 4}}}})

        ## Act ##
        index_string_out = str(my_index)

        ## Assert ##
        assert index_string_true == index_string_out

if __name__ == '__main__':
    unittest.main()
