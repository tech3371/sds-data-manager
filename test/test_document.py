import unittest
from sds_in_a_box.SDSCode.opensearch_utils.document import Document
from sds_in_a_box.SDSCode.opensearch_utils.index import Index

class TestIndex(unittest.TestCase):

    def setUp(self):
        self.my_index = Index("test_index")

    def test_create(self):
        
        

    def test_delete(self):
        pass
    
    def test_index(self):
        pass

    def test_size_in_bytes(self):
        pass

    def test_repr(self):
        pass

if __name__ == '__main__':
    unittest.main()