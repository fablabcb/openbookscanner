

// create a new status list
function StatusListElement(model) {
    this.root = document.createElement("div");
    this.root.classList.add("statusListElement");
    this.addElement("name");
    this.addElement("description");
    this.addElement("state");
    this.updateModel(model);
    document.getElementById("statusList").appendChild(this.root);
}

// this is internally called to add new fields to the gui
StatusListElement.prototype.addElement = function (name) {
    this[name] = document.createElement("div");
    this[name].classList.add(name);
    this.root.appendChild(this[name]);
}

// call this if the model changes
StatusListElement.prototype.updateModel = function (model) {
    this.name.innerText = model.type || "";
    this.description.innerText = model.description;
    this.state.innerText = model.state.description;
}




