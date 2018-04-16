from bottle import run, route, get, static_file, response, post
import os
from openbookscanner.scanner import (
    get_scanners, scan_one_page, update_local_scanners, get_by_id
)
import json

APPLICATION = 'OpenBookScanner'
HERE = os.path.dirname(__file__) or os.getcwd()
STATIC_BASE_PATH = os.path.join(HERE, "static")
ZIP_PATH = "/" + APPLICATION + ".zip"
ZIP_CONTENT_PATH = os.path.join(HERE, "..") # include the directory below

#
# Modifiers for requests
#


def enable_javascript_access(fn):
    """Enable the headers necessary for JavaScript to read the content."""
    # from https://stackoverflow.com/a/17262900
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization'
        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)
    return _enable_cors


def return_json(obj):
    """Return formatted JSON."""
    response.headers["Content-Type"] = "application/json"
    return json.dumps(obj, indent=4)

#
# Serving some content.
#

@get('/')
@get('/<path:re:css/.*|.*\\.(css|js|html|png|jpg|svg)>')
def get_static_file(path="index.html"):
    return static_file(path, root=STATIC_BASE_PATH)


#
# Interaction with the app.
#

scans = {} # scan-id : scan

@post("/scan")
@enable_javascript_access
def app_scan_one_page():
    """Scan one document page on both sides."""
    global next_scan_id
    scanner1_id = request.get("scanner1")
    scanner2_id = request.get("scanner2")
    scanner1 = get_scanners()[scanner1_id]
    scanner2 = get_scanners()[scanner1_id]
    scan = scan_one_page(scanner1, scanner2)
    scans[scan.id] = scan
    return return_json({"scans" : {scan.id: scan.toJSON()}})


@get("/scanners.json")
def get_the_avaliable_scanners():
    return return_json({"scanners": {id: scanner.toJSON() for id, scanner in get_scanners().items()}})


@get("/ref/<id>")
def get_reference(id):
    """Call a reference function."""
    reference = get_by_id(id)
    assert reference is not None, "Reference \"{}\" could not be resolved.".format(id)
    return reference.toJSON()


@get("/ref/<id>/<name>")
def call_reference(id, name):
    """Call a reference function."""
    reference = get_by_id(id)
    assert reference is not None, "Reference \"{}\" could not be resolved.".format(id)
    function_name = "GET_" + name
    function = getattr(reference, function_name)
    return function()

#
# Get the source code.
# According to AGPL I would like to get people the ability to know what is going on in this app.
#

@get('/source')
def get_source_redirect():
    """Download the source of this application."""
    redirect(ZIP_PATH)


@get(ZIP_PATH)
def get_source():
    """Download the source of this application."""
    # from http://stackoverflow.com/questions/458436/adding-folders-to-a-zip-file-using-python#6511788
    path = shutil.make_archive("/tmp/" + APPLICATION, "zip", ZIP_CONTENT_PATH)
    return static_file(path, root="/")




def main():
    """Run the openbookscanner server."""
    update_local_scanners()
    run(host='0.0.0.0', port=8001, debug=True, reload=True)

if __name__ == "__main__":
    main()
