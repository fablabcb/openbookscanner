import os
os.environ["PARSE_API_ROOT"] = "http://localhost:1337/parse"

from parse_rest.datatypes import Object
from parse_rest.connection import register
from pprint import pprint

register("APPLICATION_ID", "test123")

class GameScore(Object):
    pass
    
gameScore = GameScore(score=1337, player_name='John Doe', cheat_mode=False)
try:
    gameScore.save()
except Exception as e:
    pprint(vars(e))

pprint(vars(gameScore))

