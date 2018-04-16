"""
Interaction with the scanners.


"""
import threading
from weakref import WeakValueDictionary


class IDReferenedObject:
    _last_id = 0
    _results = WeakValueDictionary()
    
    def __new__(cls):
        """Create a new object with an id."""
        obj = super().__new__(cls)
        obj.id = cls.__name__ + "-" + str(cls._last_id)
        cls._last_id += 1
        cls._results[obj.id] = obj
        return obj
        
    @classmethod
    def get_by_id(cls, id):
        """Get the scan result by its id.
        
        Or None if none exists.
        """
        return self._results.get(id)


class CombinedScanResult:
    """A result of a scan."""
    def __init__(self, pages):
        """Create a new combined scan result."""
        self.pages = pages
    
    def toJSON(self):
        return {"type": self.__class__.__name__, "pages": {
            str(i): scan.toJSON() for i, scan in enumerate(self.pages)}}


class ScanResult(IDReferenedObject):
    """The result of a scan."""

    
    def __init__(self):
        """Create a new scan result."""
    
    def toJSON(self):
        """Return this object as JOSN represenation."""
        return {"type": self.__class__.__name__, "id": self.id}
    

class FakeFixedImageScanner:
    """This is not a real scanner.
    
    This scanner just returns the one result passed to it.
    """

    def __init__(self, name):
        """Create a fixed image scanner."""
        self.name = name
    
    def toJSON(self):
        """Return the JSON representation of the scanner with more information."""
        return {"type": self.__class__.__name__, "name": self.name, "lastScan": self.get_scan().id}
    
    def start_scan(self):
        """Start scanning a document."""
    
    def wait_for_scan_to_end(self):
        """Wait for the scan to end."""
    
    def get_scan(self):
        """Return the scan result."""
        return ScanResult()
    

def get_scanners():
    """Get the available scanners.
    
    Returns a mapping from scanner ID  to scanner object.
    """
    return {"TestScanner1": FakeFixedImageScanner("Test-Scanner 1"),
            "TestScanner2": FakeFixedImageScanner("Test-Scanner 2")}



def scan_one_page(scanner1, scanner2):
    """Scan one page with two scanners."""
    scanner1.start_scan()
    if scanner1 != scanner2:
        scanner2.start_scan()
        scanner2.wait_for_scan_to_end()
    else:
        scanner2 = scanner1
    scanner1.wait_for_scan_to_end()
    return CombinedScanResult(scanner1.get_scan(), scanner2.get_scan())

