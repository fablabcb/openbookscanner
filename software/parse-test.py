import os
os.environ["PARSE_API_ROOT"] = "http://localhost:1337/parse"

from parse_rest.datatypes import Object
from parse_rest.connection import register
from pprint import pprint
import random

register("APPLICATION_ID", "test123")

def heading(h):
    print()
    print(h)
    print("=" * len(h))

heading("GameScore from Guide")

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

heading("Test Relations")

class RelObj1(Object):
    pass
class RelObj2(Object):
    pass
class RelObj3(Object):
    """Like rel1 but with different type in attribute."""

Obj = Object.factory("Obj123123")# + str(random.randint(0, 100000)))
obj = Obj(name="obj")
rel11 = RelObj1(name="rel11", attribute1="test")
rel12 = RelObj1(name="rel12", attribute1="test")
rel2 = RelObj2(name="rel2", attribute2="test")
rel3 = RelObj3(name="rel3", attribute1=123)
obj.save()
obj.save()

rel = obj.relation("rel")
print("obj", vars(obj))
print("rel", rel)
rel.add([rel11, rel12, rel2, rel3])

for o in Obj.Query.all():
    rel = o.relation("rel")
    pprint([vars(x) for x in rel.query()])
print("seems like objects of a relation can only be of one class")

heading("Test Nested Objects")

class NestingObj(Object):
    pass

p = NestingObj(attr={"name":"test"})
p.save()
assert p.attr["name"] == "test"
print("can nest dicts")



heading("Test class factory")


print(Object.factory("Channel_") is Object.factory("Channel_"))

heading("chat via broker - run several instances")

from openbookscanner.broker import ParseBroker
from openbookscanner.message import message

class MessageReceiver:

    def receive_message(self, message):
        pprint(message)

broker = ParseBroker("test")
broker.subscribe(MessageReceiver())

while True:
    text = input("Type and press ENTER to chat: ")
    broker.deliver_message(message.test(text=text))
    broker.receive_messages()
        

