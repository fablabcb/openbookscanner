from pytest import fixture, mark
from openbookscanner.parse_update import ParseUpdater
from unittest.mock import Mock
import json


class TestSavingObject:

    data = {"type": "TestSavingObjectMockX", "description": "test description", "valueasdasdsada": 1}

    @fixture
    def obj(self):
        """The object to save."""
        obj = Mock()
        obj.toJSON.return_value = self.data
        return obj
    
    @fixture
    def ss(self):
        """The saving strategy."""
        return Mock()

    @fixture
    def pu(self, obj, ss):
        return ParseUpdater(obj, ss)
    
    def test_object_is_saved_at_start(self, pu, ss):
        ss.save.assert_called_once_with(pu.parse_object)
    
    @mark.parametrize("name,value,exists", [
        ("type", data["type"], True),
        ("description", data["description"], True)
    ])
    def test_attributes_of_object(self, pu, name, value, exists):
        if exists:
            assert (getattr(pu.parse_object, name) == value)
        assert pu.parse_object.has_type == exists
        assert (name in pu.parse_object.attributes) == exists
        
    def test_json_is_included(self, pu):
        data = json.loads(pu.parse_object.json)
        assert data == self.data
    
    def test_valueasdasdsada_is_not_an_attribute(self, pu):
        assert "valueasdasdsada" not in pu.parse_object.attributes


class TestSavingToParse:

    data = {"type": "TestSavingToParseMockX", "description": "test description", "value": 1}

    @fixture
    def obj(self):
        """The object to save."""
        obj = Mock()
        obj.toJSON.return_value = self.data
        return obj
    
    def test_save_to_parse_server(self, obj):
        pu = ParseUpdater(obj)
        assert pu.type == self.data["type"]
        
        
