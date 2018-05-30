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
    console.log("update Status of", state.json.type, state);
};

var scannerIdToScannerEntry = {};
var scannerIdToLastScannedImage = {};

// This is a state machine specially for scanners.
function ScannerListEntry(state) {
    this.id = state.json.id;
    var me = this;
    var root = this.root = document.createElement("div");
    root.classList.add("scanner", "s-grid-full", "m-grid-full", "l-grid-half", "bordered");
    addNamedDivToRoot(this, "name", ["padded", "element-heading", "grid-whole"]);
    addNamedDivToRoot(this, "device", ["padded", "grid-whole"]);
    addNamedDivToRoot(this, "button", ["padded", "grid-whole"]);
    addNamedDivToRoot(this, "images", ["padded", "grid-whole"]);
    this.image = document.createElement("img");
    this.images.appendChild(this.image);
    var scanners = document.getElementById("scanner-list");
    scanners.appendChild(this.root);
    scannerIdToScannerEntry[this.id] = this;
    this.scanButton = new StateButton("can_scan", "Scan!", function() {
        console.log("Scan " + me.id + "!");
        model.deliverMessage(message("scan", {"to": [me.id]}));
    }, ["scan-button"]);
    this.button.appendChild(this.scanButton.getHTMLElement());
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
        this.image.src = image.url;
        this.image.alt = image.name;
        this.image.model = image;
    }
}


// Show the storage
function Storage(state) {
    this.root = document.getElementById("images-list");
    this.listedImages = {};
    this.update(state);
    this.root.model = this;
};

Storage.prototype.update = function (state) {
    var images = state.json.storage.images;
    this.updateScannerImages(images);
    this.updateImageListing(images);
};
Storage.prototype.updateImageListing = function(images) {
    var me = this;
    images.forEach(function (json) {
        var image = new Image(json);
        var listedImage = me.listedImages[image.id];
        if (listedImage) {
            listedImage.update(image);
        } else {
            var listedImage = new ListedImage(me.root, image);
            me.listedImages[image.id] = listedImage;
        }
    });
};

Storage.prototype.updateScannerImages = function(images) {
    images.forEach(function(image){
        scannerIdToLastScannedImage[image.scanner.id] = new Image(image);
    });
    forAttr(scannerIdToScannerEntry, function(scannerId, scanner){
        scanner.updateImage();
    });
};

function ListedImage(container, image) {
    this.container = container;
    this.image = image;
    this.root = document.createElement("div");
    this.container.appendChild(this.root);
    this.root.classList.add("s-grid-whole", "m-grid-half", "l-grid-third", "listed-image", "padded");
    
    this.img = document.createElement("img");
    this.root.appendChild(this.img);
    this.update(image);
}

ListedImage.prototype.update = function(image) {
    this.img.src = image.url;
}

// Middle interface to communicate with the scanners

var scanners = [];

function ScannerInteraction(state) {
    console.log("ScannerInteraction", state);
    this.id = state.json.id;
    scanners.push(this);
}

ScannerInteraction.prototype.update = function(state) {
}



const relationsToStateMachineViews = {
    "status": [Status],
    "listener": [Status],
    "usb_stick_listener": [Status],
    "scanner": [Status, ScannerListEntry, ScannerInteraction],
    "storage": [Status, Storage],
    "usb_stick": [Status]
};

