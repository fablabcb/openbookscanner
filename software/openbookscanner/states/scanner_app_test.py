import sys, os
print("sys.path", sys.path)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from openbookscanner.states.scanner_app import main
main()
