///////////////////////////////////////////////////////////////////////////////
//                     State machines
//
// In this section, the different state machines are handled and updated.
//

// This is the status state machine.
function Status(state) {
    this.statusElement = new StatusListElement(state.json);
    console.log("create_status", state);
}

Status.prototype.update = function (state) {
    this.statusElement.updateModel(state.json);
    console.log("update_status", state);
};

// This is a state machine specially for scanners.
function ScannerListEntry(state) {
    var root = this.root = document.createElement("div");
    ["scanner", "s-grid-full", "m-grid-half", "l-grid-third", "padded", "bordered"].forEach(function(e){
        root.classList.add(e);
    });
    addNamedDivToRoot(this, "name");
    addNamedDivToRoot(this, "device");
    this.scanButton = new StateButton("can_scan", "Scan!", function() {
        console.log("scan " + state.json.id + "!");
    });
    this.root.appendChild(this.scanButton.getHTMLElement());
    var scanners = document.getElementById("scanner-list");
    scanners.appendChild(this.root);
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
};


const relationsToStateMachineViews = {"status": [Status], "listener": [Status], "scanner": [Status, ScannerListEntry]};

