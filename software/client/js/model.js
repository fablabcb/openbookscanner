
const PUBLIC_MODEL_CLASS_NAME = "OpenBookScanner";
const CHANNEL_NAME_FROM_BOOKSCANNER = "OpenBookScannerOutgoing";
const CHANNEL_NAME_TO_BOOKSCANNER = "OpenBookScannerIncoming";

var model;

// This is the model class for the whole open book scanner
function Model() {
    this.outgoingMessages = new ParseSubscriber(CHANNEL_NAME_FROM_BOOKSCANNER);
    this.outgoingMessages.subscribe(new ConsoleMessageLoggingSubscriber(CHANNEL_NAME_FROM_BOOKSCANNER));
    this.outgoingMessages.subscribe(new ReloadWhenBookscannerRestarts());
    this.incomingMessages = new ParsePublisher(CHANNEL_NAME_TO_BOOKSCANNER);
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
                console.log("Error:", e);
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
                console.log("Error:", e);
                throw e;
            }
        }
    });
}

// deliver a message to the bookscanner
Model.prototype.deliverMessage = function(message) {
    console.log("model.deliverMessage:", message);
    this.incomingMessages.deliverMessage(message);
}


window.addEventListener("load", function () {
    model = new Model();
    scrollToAnchor();
});

// scroll to the #
function scrollToAnchor() {
    if (document.location.hash == "") {
        return;
    }
    // behavioral configuration
    var secondsWithoutChangeToCancel = 1;
    var maximumSeconds = 3;
    var intervalInMilliseconds = 200;
    
    // computed values
    var scollsWithoutChangeToCancel = secondsWithoutChangeToCancel * 1000 / intervalInMilliseconds;
    var timesScrolledWithoutChange = 0;
    var intervalId = setInterval(function(){
        // from https://stackoverflow.com/a/3163635
        var old_position = window.pageYOffset;
        window.location.hash = window.location.hash;
        var new_position = window.pageYOffset;
        if (new_position == old_position) {
            timesScrolledWithoutChange += 1;
        } else {
            timesScrolledWithoutChange = 0;
            console.log("Content changed, scrolling to " + document.location.hash + ".");
        }
        if (timesScrolledWithoutChange >= scollsWithoutChangeToCancel) {
            clearInterval(intervalId);
            console.log("Done scrolling after " + secondsWithoutChangeToCancel + " of no change.");
        }
    }, intervalInMilliseconds);

}


// This is an image object
function Image(imageData) {
    this.json = imageData;
    this.url = getImageURL(imageData);
    this.id = this.json.id;
    this.name = this.json.name;
}


