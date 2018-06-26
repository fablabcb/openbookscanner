Phone camera access
--------

This directory serves as a test for accessing the phone camera with Javascript by using [`MediaDevices.getUserMedia()`](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).

- [Constrained by video resolution?](https://stackoverflow.com/a/26501469)

Alternative solutions:

- [MDN sample](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Taking_still_photos) - Three year old example from Mozilla using individual browsers' implementations. Did not work on Firefox 60.0.2.

- [MIT App Inventor](http://appinventor.mit.edu/) - "Camera" object is only capable of registering an intent to the phone's camera app which needs a button press to work.
