import os

def test_parse_environment_variable_is_set():
    message = """The environment variable PARSE_API_ROOT must be set.
    
    When you start the Parse Server, you get the URL of the parse server.
    
        serverURL: http://localhost:1337/parse
    
    Put this into the environment variable like so:
    
        export PARSE_API_ROOT="http://localhost:1337/parse"
    
    Then, you can start pytest.
    """
    print(message)
    assert "PARSE_API_ROOT" in os.environ, message
