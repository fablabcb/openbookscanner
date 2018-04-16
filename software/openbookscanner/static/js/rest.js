/* This document provides the API of the app.py file.
 *
 *
 */


function requestJSON(method, path, request, onSuccess, onError) {
  // from https://stackoverflow.com/a/9713078
  var http = new XMLHttpRequest();
  var url = document.location.protocol + "//" + document.location.host + path;
  var params = JSON.stringify(request);
  http.open(method, url, true);

  //Send the proper header information along with the request
  http.setRequestHeader("Content-type", "application/json");
  http.setRequestHeader("Accept", "application/json");

  http.onreadystatechange = function() {//Call a function when the state changes.
    if(http.readyState == 4) {
      if (http.status == 200) {
        var data = JSON.parse(http.responseText);
        onSuccess(data);
      } else if (onError) {
        onError(http);
      } else {
        console.log("ERROR at " + path + " with params " + params + ": " + http.status + " - " + http.responseText);
      }
    } 
  }
  http.send(params);
}

function getScanners(onSuccess, onError) {
  // get the scanners
  requestJSON("GET", "/scanners.json", null, function(data){
    onSuccess(data.scanners);
  }, onError);
}




