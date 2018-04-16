
// remove all children from an HTML element
function removeAllChildren(element) {
  while (element.firstElementChild) {
    element.removeChild(element.firstElementChild);
  }
}

// iterate over all attributes
function forAttr(obj, callback) {
  // from https://stackoverflow.com/a/16735184
  var attributes = [];
  for (var property in obj) {
    if (obj.hasOwnProperty(property)) {
        attributes.push(property);
    }
  }
  attributes.sort();
  attributes.forEach(function(property) {callback(property, obj[property]);});
}

