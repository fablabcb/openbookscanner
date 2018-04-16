"""
Interaction with the scanners.


"""
import subprocess
from weakref import WeakValueDictionary
from concurrent.futures import ThreadPoolExecutor
import os

HERE = os.path.dirname(__file__) or os.getcwd()
EXAMPLE_IMAGE = os.path.join(HERE, "static", "img", "test.jpg")


class IDReferenedObject(object):
    _last_id = 0
    _instances = WeakValueDictionary()
    
    def __new__(cls, *args, **kw):
        """Create a new object with an id."""
        obj = object.__new__(cls)
        obj.id = cls.__name__ + "-" + str(cls._last_id)
        cls._last_id += 1
        cls._instances[obj.id] = obj
        return obj
        
    @classmethod
    def get_by_id(cls, id):
        """Get the scan result by its id.
        
        Or None if none exists.
        """
        return cls._instances.get(id)
    
    @property
    def id(self):
        """The id of this object."""
        return self.__id
    @id.setter
    def id(self, value):
        self.__class__._instances[value] = self
        self.__id = value
        del self._instances[self.id]
    
    def toJSONRef(self):
        """Return the JSON reference to this object."""
        return {"type": "reference", "path": "/ref/" + self.id, "id": self.id}
    
    def toJSON(self, *args):
        """Return a JSON representation."""
        d = {"type": self.__class__.__name__, "id": self.id, "isScan": False, "isScannerHardware": False, "isScanner": False,
            "path": self.path}
        for v in reversed(args):
            d.update(v)
        return d
        
    @property
    def path(self):
        """Return the path of the object where it can be found."""
        return  "/ref/" + self.id

get_by_id = IDReferenedObject.get_by_id


class CombinedScanResult:
    """A result of a scan."""
    def __init__(self, pages):
        """Create a new combined scan result."""
        self.pages = pages
    
    def toJSON(self, *args):
        return {"type": self.__class__.__name__, "pages": {
            str(i): scan.toJSON() for i, scan in enumerate(self.pages)}}


class ScanResult(IDReferenedObject):
    """The result of a scan."""

    def __init__(self, image):
        """Create a new scan result."""
        self.image = image
    
    def toJSON(self, *args):
        """Return this object as JOSN represenation."""
        return super().toJSON({"isScan": True, "image":self.path + "/image"}, *args)
        
    def GET_image(self):
        """Return the image of the scan"""
        return open(self.image, "rb")


class ExampleScanResult(ScanResult):
    """This is an example scan."""
    
    def __init__(self):
        """Create an example scan image."""
        super().__init__(EXAMPLE_IMAGE)
        

class NoScanResult(IDReferenedObject):
    """When no scan was attempted, yet."""


class FakeFixedImageScanner(IDReferenedObject):
    """This is not a real scanner.
    
    This scanner just returns the one result passed to it.
    """

    def __init__(self, name):
        """Create a fixed image scanner."""
        self.name = name
        self.scan_result = ExampleScanResult()
    
    def toJSON(self):
        """Return the JSON representation of the scanner with more information."""
        return super().toJSON({"name": self.name, "lastScan": self.get_scan().toJSONRef(), "isScanner": True})
    
    def start_scan(self):
        """Start scanning a document."""
    
    def wait_for_scan_to_end(self):
        """Wait for the scan to end."""
    
    def get_scan(self):
        """Return the scan result."""
        return self.scan_result


class LocalScanner(IDReferenedObject):
    """A Scanner which is connected to the computer."""
    
    def __init__(self, number, device, type, model, producer):
        """Create a fixed image scanner."""
        self.number = number
        self.device = device
        self.type = type
        self.model = model
        self.producer = producer
        self.id = self.device
        self.scan_result = NoScanResult()
        self.name = "Scanner " + number
    
    def toJSON(self):
        """Return the JSON representation of the scanner with more information."""
        return super().toJSON({"hardware": self.type, "name": self.name, "lastScan": self.get_scan().toJSONRef(),
            "number": self.number, "device": self.device, "model": self.model, "producer": self.producer, 
            "isScannerHardware": True})
    
    def start_scan(self):
        """Start scanning a document."""
    
    def wait_for_scan_to_end(self):
        """Wait for the scan to end."""
    
    def get_scan(self):
        """Return the scan result."""
        return self.scan_result

FakeFixedImageScanner1 = FakeFixedImageScanner("Test-Scanner 1")
FakeFixedImageScanner2 = FakeFixedImageScanner("Test-Scanner 2")

scanner_pool = ThreadPoolExecutor(max_workers=1)
scanimage_scanners = {}

def update_local_scanners(threadpool=scanner_pool):
    """Update the local list of printers available."""
    def update():
        p = subprocess.run(["scanimage", "-f", "%i|%d|%t|%m|%v"],
            stdout=subprocess.PIPE, check=True)
        scanimage_scanners.clear()
        for line in p.stdout.decode().splitlines():
            number, device, type, model, producer = line.split("|")
            scanner = LocalScanner(number, device, type, model, producer)
            scanimage_scanners[scanner.id] = scanner
    return threadpool.submit(update)


def get_scanners():
    """Get the available scanners.
    
    Returns a mapping from scanner ID  to scanner object.
    """
    scanners =  {"TestScanner1": FakeFixedImageScanner1,
        "TestScanner2": FakeFixedImageScanner2}
    scanners.update(scanimage_scanners)
    return scanners


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

