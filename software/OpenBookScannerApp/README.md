# OpenBookScannerApp

This Android App takes the pictures and registers as a scanner.
You can develop this app with Android Studio 3.1.3.
This app is compatible with old phones until Android 2.3.

## API

The OpenBookScannerApp requires this API endpoint:

- `POST /scanner` with data
  Headers:
  - `Content-Type: application/json`
  ```
  {
    "type": "scanner",
    "name": "<name of the phone>",
    "id": "random id for this run of the app"
  }
  ```
  The attributes have the following meaning:
  - `type` is `"scanner"` because this is what the app is going to do.
  - `name` is the name of the device which should be displayed.
  - `id` is the id of the scanner as there might be multiple devices of the same name.
  This results in `200`.
  Headers:
  - `Content-Type: application/json`
  - if no picture shall be taken:
    ```
    {
      "status": "ok",
      "refresh": 0.5
    }
    ```
  - if a picture shall be taken:
    ```
    {
      "status": "ok",
      "refresh": SECONDS,
      "picture": "<full url>"
    ```
  These are the values explained:
  - `status` should be `"ok"`. Otherwise, there was an error.
  - `refresh` is the seconds as float
     when to re-post to keep the scanner active.
  - `picture` is the full url including `http://hostname:port/path` where
    to post the picture once taken.  
    Method: `POST`
    Headers:
    - `Content-Type: image/jpeg`

## Thanks

- Big thanks to [isnotmenow](https://github.com/isnotmenow/AndroidProjectForAPI9)
  for the [APIv9 app](https://github.com/isnotmenow/AndroidProjectForAPI9).
