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

gameScore.addToArray("key", ["object1", "object2"])
gameScore.save()
gameScore.removeFromArray("key", ["object2"])
gameScore.save()

pprint(vars(gameScore))
pprint(gameScore.objectId)


print(Object.factory("Channel_") is Object.factory("Channel_"))


from openbookscanner.broker import ParseBroker
from openbookscanner.message import message

class MessageReceiver:

    def receive_message(self, message):
        pprint(message)

broker = ParseBroker("test")
broker.subscribe(MessageReceiver())

while True:
    text = input()
    broker.deliver_message(message.test(text=text))
    broker.receive_messages()
        

