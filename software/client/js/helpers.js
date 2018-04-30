
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


function deepEqual(x, y) {
  // from https://stackoverflow.com/a/32922084
  return (x && y && typeof x === 'object' && typeof y === 'object') ?
    (Object.keys(x).length === Object.keys(y).length) &&
      Object.keys(x).reduce(function(isEqual, key) {
        return isEqual && deepEqual(x[key], y[key]);
      }, true) : (x === y);
}

function addNamedDivToRoot(me, name, classList) {
    var div = me[name] = me.root[name] = document.createElement("div");
    [name].concat(classList || []).forEach(function (e) {
        div.classList.add(e);
    });
    me.root.appendChild(div);
}

function camelCaseToSpacing(string) {
    var result = "";
    for (var i = 0; i < string.length; i += 1) {
        var character = string.charAt(i);
        if (character.toLowerCase() == character) {
            result += character;
        } else if (i == 0) {
            result += character.toLowerCase();
        } else {
            result += " " + character.toLowerCase();
        }
    }
    return result;
}

