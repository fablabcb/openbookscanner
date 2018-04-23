
const PUBLIC_MODEL_CLASS_NAME = "OpenBookScanner";


var model;


function Model() {
    this.outgoingMessages = new ParseSubscriber("OpenBookScannerOutgoing");
    this.outgoingMessages.subscribe(new ConsoleMessageLoggingSubscriber("OpenBookScannerOutgoing"));
    this.modelClass = Parse.Object.extend(PUBLIC_MODEL_CLASS_NAME);
    this.relations = ["status"];
    this.createdRelationObjectIdsToStates = {};
    this.retrieveModel();
}

Model.prototype.retrieveModel = function() {
    var me = this;
    var query = new Parse.Query(this.modelClass);
    // Retrieve the most recent ones
    query.descending("createdAt");
    query.limit(1);
    this.relations.forEach(function(attr) {
        query.include(attr);
    });
    query.find({
        "success": function(models) {
            try {
                me.model = models[0];
                me.modelUpdated();
                notifyOnUpdate(me.model, function(new_model){
                    me.model = new_model;
                    me.modelUpdated();
                });
            } catch (e) {
                console.log(e);
                throw e;
            }
        }
    });
};

// This function is called when the bookscanner model is updated.
// It queries the relations of the bookscanner object and updates listeners.
Model.prototype.modelUpdated = function() {
    var me = this;
    this.relations.forEach(function(attr) {
        me.updateModelRelation(attr);
    });
};

// This updates one specific model relation.
// If a new object is related to by the model, the create function for it is called.
// If the related object changes, the update function for it is called.
Model.prototype.updateModelRelation = function(relationName) {
    var me = this;
    var relation = me.model.relation(relationName);
    relation.query().find({
        "success": function(relatedObjects){
            try {
                relatedObjects.forEach(function (relatedObject) {
                    var state  = me.createdRelationObjectIdsToStates[relatedObject.id];
                    if (!state) {
                        var constructor = me["create_" + relationName];
                        var state = me.createdRelationObjectIdsToStates[relatedObject.id] = {};
                        function updateState(parseObject) {
                            state.parseObject = parseObject;
                            var json = parseObject.get("json");
                            if (json) {
                                state.json = JSON.parse(json);
                            } else {
                                state.json = null;
                            }
                        }
                        updateState(relatedObject);
                        if (typeof constructor == "function") {
                            constructor(state);
                        }
                        var updateFunction = me["update_" + relationName];
                        if (typeof updateFunction == "function") {
                            notifyOnUpdate(relatedObject, function () {
                                var updateFunction = me["update_" + relationName];
                                updateState(relatedObject);
                                updateFunction(state);
                            });
                        } else {
                            console.log("no update function for " + relationName);
                        }
                    } else {
                        console.log("relation " + relationName + " for " + relatedObject.id + " is not updated.")
                        me["update_" + relationName](relatedObject, state);
                    }
                });
            } catch (e) {
                console.log(e);
                throw e;
            }
        }
    });
}

Model.prototype.create_status = function (state) {
    state.statusElement = new StatusListElement(state.json);
    console.log("create_status", state);
}

Model.prototype.update_status = function (state) {
    state.statusElement.updateModel(state.json);
    console.log("update_status", state);
}


window.addEventListener("load", function () {
    model = new Model();
});

