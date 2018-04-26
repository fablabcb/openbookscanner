

// create a new status list
function StatusListElement(model) {
    this.root = root = document.createElement("div");
    ["statusListElement", "s-grid-whole", "m-grid-half", "l-grid-third", "padded", "bordered"].forEach(function(e){
        root.classList.add(e);
    });
    this.addElement("name", ["centered"]);
    this.addElement("description");
    this.addElement("state");
    this.updateModel(model);
    document.getElementById("statusList").appendChild(this.root);
}

// this is internally called to add new fields to the gui
StatusListElement.prototype.addElement = function (name, classList) {
    addNamedDivToRoot(this, name, classList);
}

// call this if the model changes
StatusListElement.prototype.updateModel = function (model) {
    this.name.innerText = "The " + camelCaseToSpacing(model.type);
    if (model.name) {
        this.name.innerText += " \"" + model.name + "\"";
    }
    if (model.state.type) {
        this.name.innerText += " is " + camelCaseToSpacing(model.state.type) + ".";
    }
    this.description.innerText = model.description;
    this.state.innerText = model.state.description;
    if (model.state.is_final) {
        this.root.classList.add("final");
    } else {
        this.root.classList.remove("final");
    }
}




