

// This is a button which enables/disables an action based on a given attribute.
function StateButton(attribute, text, onClick) {
    this.attribute = attribute;
    this.onClick = onClick;
    this.button = document.createElement("input");
    this.button.type = "button";
    this.button.value = text;
    this.button.classList.add("StateButton");
    var me = this;
    this.button.onclick = function() {
        if (me.enabled) {
            onClick(me);
        } else {
            console.log("disabled");
        }
    };
    this.enabled = true;
    this.button.view = this;
}

StateButton.prototype.update = function(stateMachineJSON) {
    this.enabled = stateMachineJSON[this.attribute] ? true : false;
    this.button.disabled = !this.enabled;
    if (this.enabled) {
        this.button.classList.add("enabled");
        this.button.classList.remove("disabled");
    } else {
        this.button.classList.remove("enabled");
        this.button.classList.add("disabled");
    }
}

StateButton.prototype.getHTMLElement = function() {
    return this.button;
}

