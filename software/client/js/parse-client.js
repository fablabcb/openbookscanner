/* This configuration should be the same as in the Python application.
 *
 */
const CHANNEL_CLASS_PREFIX = "Channel";
const APPLICATION_ID = "OpenBookScanner";


var p;

var fetchObjects = [];

/* add a parseObject to watch for updates and call a function onSuccess and onError */
function notifyOnUpdate(parseObject, onSuccess, onError) {
    // TODO: use live queries
    fetchObjects.push({
        "parseObject": parseObject,
        "onSuccess":onSuccess,
        "onError": onError, 
        "updatedAt": parseObject.updatedAt});
}

function fetchAll() {
    fetchObjects.forEach(function(spec) {
        var promise = spec.parseObject.fetch();
        // fetch returns a promise, see 
        // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise
        if (spec.onSuccess) {
            promise.then(function(newParseObject){
                if (newParseObject.updatedAt.getTime() != spec.updatedAt.getTime()) {
                    spec.parseObject = newParseObject; // not needed but we make sure it works.
                    spec.updatedAt = newParseObject.updatedAt;
                    try {
                        spec.onSuccess(newParseObject);
                    } catch (e) {
                        console.log(e);
                        throw e;
                    }
                }
            });
        };
        if (spec.onError) {
            promise.catch(spec.onError);
        };
    })
}
var fetchAllInterval;

function initializeParse() {
    fetchAllInterval = window.setInterval(fetchAll, 300);
    Parse.initialize("OpenBookScanner");
    Parse.serverURL = "http://" + (document.location.hostname || "localhost") + ":1337/parse";
    console.log("Parse server URL is " + Parse.serverURL);
}


function getChannelClass(channelName) {
    return Parse.Object.extend(CHANNEL_CLASS_PREFIX + channelName);
}

function ParseSubscriber(channelName) {
    this.channelClass = getChannelClass(channelName);
    this.channel = new this.channelClass();
    this.channel.set("messages", []);
    this.channelName = this.channelClass.className;
    this.subscribers = [];
    var me = this;
    this.channel.save(null,{
        "success": function(channel) {
            console.log("Channel " + me.channelName + " with id " + me.channel.id + " saved.");
            notifyOnUpdate(channel, function(channel) {
                me.changed();
            });
        },
        "error": function(channel, error) {
            console.log("Channel not created. " + error.message);
        }
    });
}

ParseSubscriber.prototype.delete = function(){
    this.channel.destroy();
}

ParseSubscriber.prototype.changed = function(){
    var me = this;
    var messages = this.channel.get("messages");
    try {
        messages.forEach(function(message){
            me.channel.remove("messages", message);
            me.subscribers.forEach(function(subscriber){
                var data = JSON.parse(message);
                subscriber.receiveMessage(data);
            });
        });
    } finally {
        me.channel.save();
    }
}

ParseSubscriber.prototype.subscribe = function(subscriber){
    this.subscribers.push(subscriber);
}


function ConsoleMessageLoggingSubscriber(channelName) {
    this.receiveMessage = function(message) {
        console.log((channelName||"") + JSON.stringify(message));
    }
}

window.addEventListener("load", initializeParse);












/* If one day we get liveQuery to work.
    var me = this;
    me.query = new Parse.Query(me.channelClass);
    me.query.notEqualTo("messages", []);
    me.subscription = me.query.subscribe();
    //me.subscription.on("update", me.changed);
    me.subscription.on("enter", function(){
        console.log("Channel " + me.channelName + " with id " + me.channel.id + " entered.");
    });
    me.subscription.on("leave", function(){
        console.log("Channel " + me.channelName + " with id " + me.channel.id + " left.");
    });
    me.subscription.on("create", function(){
        console.log("Channel " + me.channelName + " with id " + me.channel.id + " created.");
    });
    me.subscription.on("update", function(){
        console.log("Channel " + me.channelName + " with id " + me.channel.id + " updated.");
    });
    me.subscription.on("open", function(){
        console.log("Channel " + me.channelName + " with id " + me.channel.id + " opened.");
    });
    me.subscription.on("close", function(){
        console.log("Channel " + me.channelName + " with id " + me.channel.id + " closed.");
    });
*/


