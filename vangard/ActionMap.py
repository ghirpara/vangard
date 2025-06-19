"""

    ActionMap.py 



     
    Author: G.Hirpara
    Version: 1.0.0
    Copyright (c) 2025 G.Hirpara
  
    LICENSING FOR THIS CODE IS DOCUMENTED IN THE ACCOMPANYING LICENSE.md FILE. 
    USERS OF THIS CODE AGREE TO TERMS AND CONDITIONS OUTLINED IN THE LICENSE.
  """

import json

class ActionMap:
  
    def __init__(self):
        self.action_map = json.load(open("actions.json", "r"))

    def is_valid_action(self, key):
        return key in self.action_map

    