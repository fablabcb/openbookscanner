

// create a new status list
function StatusListElement(model) {
    this.root = root = document.createElement("div");
    ["statusListElement", "s-grid-full", "m-grid-half", "l-grid-third", "padded", "bordered"].forEach(function(e){
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
    var me = this;
    this[name] = document.createElement("div");
    [name].concat(classList).forEach(function (e) {
        me[name].classList.add(e);
    });
    this.root.appendChild(this[name]);
}

// call this if the model changes
StatusListElement.prototype.updateModel = function (model) {
    this.name.innerText = model.type || "";
    this.description.innerText = model.description;
    this.state.innerText = model.state.description;
}




