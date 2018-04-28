///////////////////////////////////////////////////////////////////////////////
//                     State machines
//
// In this section, the different state machines are handled and updated.
//

// This is the status state machine.
function Status(state) {
    this.statusElement = new StatusListElement(state.json);
    console.log("create Status of", state.json.type, state);
}

Status.prototype.update = function (state) {
    this.statusElement.updateModel(state.json);
    console.log("update Status", state.json.type, state);
};

var scannerIdToScannerEntry = {};
var scannerIdToLastScannedImage = {};

// This is a state machine specially for scanners.
function ScannerListEntry(state) {
    this.id = state.json.id;
    var me = this;
    var root = this.root = document.createElement("div");
    ["scanner", "s-grid-full", "m-grid-half", "l-grid-third", "padded", "bordered"].forEach(function(e){
        root.classList.add(e);
    });
    addNamedDivToRoot(this, "name");
    addNamedDivToRoot(this, "device");
    addNamedDivToRoot(this, "images");
    this.image = document.createElement("img");
    this.images.appendChild(this.image);
    this.scanButton = new StateButton("can_scan", "Scan!", function() {
        console.log("Scan " + me.id + "!");
        model.deliverMessage(message("scan", {"to": [me.id]}));
    });
    this.root.appendChild(this.scanButton.getHTMLElement());
    var scanners = document.getElementById("scanner-list");
    scanners.appendChild(this.root);
    scannerIdToScannerEntry[this.id] = this;
    this.update(state);
}

ScannerListEntry.prototype.update = function (state) {
    this.scanButton.update(state.json);
    this.name.innerText = state.json.name;
    this.device.innerText = state.json.model + " (" + state.json.device + ") is " +
                            camelCaseToSpacing(state.json.state.type) + ".";
    if (state.json.is_plugged_in) {
        this.root.classList.remove("hidden");
    } else {
        this.root.classList.add("hidden");
    }
    this.updateImage();
};

ScannerListEntry.prototype.updateImage = function() {
    var image = scannerIdToLastScannedImage[this.id];
    if (image) {
        src = getImageURL(image);
        this.image.src = src;
    }
}


// Show the storage
function Storage(state) {
    this.update(state);
    
}
Storage.prototype.update = function (state) {
    var images = state.json.storage.images;
    images.forEach(function(image){
        scannerIdToLastScannedImage[image.scanner.id] = image;
    });
    forAttr(scannerIdToScannerEntry, function(scannerId, scanner){
        scanner.updateImage();
    });
}


const relationsToStateMachineViews = {
    "status": [Status],
    "listener": [Status], 
    "scanner": [Status, ScannerListEntry],
    "storage": [Status, Storage]
};

