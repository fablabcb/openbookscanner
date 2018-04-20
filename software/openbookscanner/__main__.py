"""
Run the module with

    python3 -m openbookscanner

"""
import os
import pdb
os.environ.setdefault("PARSE_API_ROOT", "http://localhost:1337/parse")

from openbookscanner.cli import cli

try:
    cli()
except Exception as e:
    print("e =", e, e.__class__.__qualname__, vars(e))
    pdb.post_mortem()
