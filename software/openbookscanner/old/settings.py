import os
import copy
import jsonschema


HERE = os.path.dirname(__file__) or os.getcwd()
SCHEMA_FILE_NAME = "settings.schema"
SCHEMA_FILE = os.path.join(HERE, SCHEMA_FILE_NAME)
SETTINGS_FILE_NAME = "settings.json"
SETTINGS_FILE = os.path.join(HERE, SETTINGS_FILE_NAME)



class Settings:

    @staticmethod
    def load_schema():
        """Load the settings schema from the file."""
        with open(SCHEMA_FILE) as f:
            schema = json.load(f)
            return jsonschema.Draft4Validator(schema)

    def __init__(self):
        """Create a settings object."""
        self._schema = load_schema()
        self.load_default_settings()
    
    def load_default_settings(self):
        with open(SETTINGS_FILE) as f:
            self.set("/", json.load(f))
    
    def set(self, path, value):
        """Set the settings."""
        assert path.startswith("/")
        path = path[1:]
        if path:
            new_settings = copy.deepcopy(self._settings)
            new_settings[path] = value
        else:
            new_settings = value
        self._schema.validate(new_settings)
        self._settings = new_settings
        
    def get(self, path="/"):
        """Get a value from the settings."""
        assert path.startswith("/")
        path = path[1:]
        if path:
            return self._settings[path]
        return self._settings



