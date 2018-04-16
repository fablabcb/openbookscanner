"""
Interaction with the scanners.


"""

class CombinedScanResult:
    """A result of a scan."""
    def __init__(self, pages):
        """Create a new combined scan result."""
        self.pages = pages
    
    def toJSON(self):
        return {"type": self.__class__.__name__, "pages": {
            str(i): scan.toJSON() for i, scan in enumerate(self.pages)}}


class ScanResult:
    """The result of a scan."""
    
    def toJSON(self):
        """Return this object as JOSN represenation."""
        return {"type": self.__class__.__name__}
    

class FakeFixedImageScanner:
    """This is not a real scanner.
    
    This scanner just returns the one result passed to it.
    """

    def __init__(self):
        """Create a fixed image scanner."""
    
    def toJSON(self):
        """Return the JSON representation of the scanner with more information."""
        return {"type": self.__class__.__name__}
    
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
    return {"TestScanner1": FakeFixedImageScanner(),
            "TestScanner2": FakeFixedImageScanner()}



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

