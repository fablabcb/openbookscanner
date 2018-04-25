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




const relationsToStateMachineViews = {"status": [Status], "listener": [Status], "scanner": [Status]};

