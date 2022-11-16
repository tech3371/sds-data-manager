import unittest
from sds_in_a_box.SDSCode.opensearch_utils.action import Action

class TestIndex(unittest.TestCase):

    def test_validate_action_pass(self):
      """
      Tests that the validate_action method correctly determines
      that an object of type Action is of type Action and is returned
      unchanged
      """

      action = Action.CREATE

      result = Action.validate_action(action)  

      assert result == action

    def test_validate_action_fail(self):
      """
      Tests that the validate_action method correctly throws an error
      if the input is not of type Action.
      """

      action = "this is a string, not an action"

      self.assertRaises(TypeError, Action.validate_action, action)
        

if __name__ == '__main__':
    unittest.main()
