import unittest
from sds_in_a_box.SDSCode.opensearch_utils.action import Action

class TestAction(unittest.TestCase):

    def test_validate_action_pass(self):
      """
      Tests that the validate_action method correctly determines
      that an object of type Action is of type Action and is returned
      unchanged
      """
      ## Arrange ##
      action_true = Action.CREATE

      ## Act ##
      action_out = Action.validate_action(action_true)  

      ## Assert ##
      assert action_true == action_out

    def test_validate_action_fail(self):
      """
      Tests that the validate_action method correctly throws an error
      if the input is not of type Action.
      """
      ## Arrange ##
      action = "this is a string, not an action"

      ## Act / Assert ##
      self.assertRaises(TypeError, Action.validate_action, action)
        

if __name__ == '__main__':
    unittest.main()
