
const PUBLIC_MODEL_CLASS_NAME = "OpenBookScanner";


var model;

// This is the model class for the whole open book scanner
function Model() {
    this.outgoingMessages = new ParseSubscriber("OpenBookScannerOutgoing");
    this.outgoingMessages.subscribe(new ConsoleMessageLoggingSubscriber("OpenBookScannerOutgoing"));
    this.modelClass = Parse.Object.extend(PUBLIC_MODEL_CLASS_NAME);
    this.relations = relationsToStateMachineViews;
    this.createdRelationObjectIdsToStates = {};
    this.retrieveModel();
}

// private: this is called once to retrieve the model
Model.prototype.retrieveModel = function() {
    var me = this;
    var query = new Parse.Query(this.modelClass);
    // Retrieve the most recent ones
    query.descending("createdAt");
    query.limit(1);
    forAttr(this.relations, function(attr) {
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
    forAttr(this.relations, function(attr) {
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
                        state.views = [];
                        me.relations[relationName].forEach(function(constructor) {
                            state.views.push(new constructor(state));
                        });
                        notifyOnUpdate(relatedObject, function (relatedObject) {
                            updateState(relatedObject);
                            state.views.forEach(function(view){
                                view.update(state);
                            });
                        });
                    } else {
                        console.log("Relation " + relationName + " for " + relatedObject.id + " already exists.");
                    }
                });
            } catch (e) {
                console.log(e);
                throw e;
            }
        }
    });
}



window.addEventListener("load", function () {
    model = new Model();
});

