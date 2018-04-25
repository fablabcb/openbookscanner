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
function Scanner(state) {
    this.root = document.createElement("div");
    this.root.classList.add("scanner");
    addNamedDivToRoot(this, "name");
    addNamedDivToRoot(this, "device");
    this.scanButton = new StateButton(state.json, "can_scan", "Scan!", function(){
        console.log("scan " + state.json.id + "!");
    });
    this.root.appendChild(this.scanButton.getHTMLElement());
    var scanners = document.getElementById("scanner-list");
    scanners.appendChild(this.root);
    this.update(state);
}

Scanner.prototype.update = function (state) {
    this.scanButton.update(state.json);
    this.name.innerText = state.json.model + " " + state.json.number;
    this.device.innerText = "(" + state.json.device + ")"
};


const relationsToStateMachineViews = {"status": [Status], "listener": [Status], "scanner": [Status, Scanner]};

