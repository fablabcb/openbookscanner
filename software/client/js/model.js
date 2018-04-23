
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

Model.prototype.modelUpdated = function() {
    var me = this;
    this.relations.forEach(function(attr) {
        me.updateModelRelation(attr);
    });
};

Model.prototype.updateModelRelation = function(relationName) {
    var me = this;
    var relation = me.model.relation(relationName);
    relation.query().find({
        "success": function(relatedObjects){
            relatedObjects.forEach(function (relatedObject) {
                var state  = me.createdRelationObjectIdsToStates[relatedObject.id];
                if (!state) {
                    var constructor = me["create_" + relationName];
                    var state = typeof constructor == "function" ? constructor(relatedObject) : {};
                    me.createdRelationObjectIdsToStates[relatedObject.id] = state;
                    var updateFunction = me["update_" + relationName];
                    if (typeof updateFunction == "function") {
                        notifyOnUpdate(relatedObject, function () {
                            var updateFunction = me["update_" + relationName];
                            updateFunction(relatedObject, state);
                        });
                    } else {
                        console.log("no update function for " + relationName);
                    }
                } else {
                    console.log("relation " + relationName + " for " + relatedObject.id + " is not updated.")
                    me["update_" + relationName](relatedObject, state);
                }
            });
        }
    });
}

Model.prototype.create_status = function (relatedObject, state) {
    console.log("create_status", relatedObject);
}

Model.prototype.update_status = function (relatedObject, state) {
    console.log("update_status", relatedObject);
}



window.addEventListener("load", function () {
    model = new Model();
});

