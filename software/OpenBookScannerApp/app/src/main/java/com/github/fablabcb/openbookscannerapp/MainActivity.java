package com.github.fablabcb.openbookscannerapp;

import android.Manifest;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.hardware.Camera;
import android.hardware.Camera.CameraInfo;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.net.URLEncoder;
import java.util.UUID;


public class MainActivity extends AppCompatActivity {

    private final static String DEBUG_TAG = "MainActivity";
    private final static int DEFAULT_PORT = 8001;

    private ImageView imageView;
    private TextView statusText;
    private Button button;
    private boolean cameraIsAvailable;
    private boolean hasCameraFeature;
    private boolean cameraIsDisabled;
    private Camera camera;
    private EditText addressIP;
    private EditText addressPort;
    private TextView serverStatus;
    private UUID app_id;



    protected void setAttributesOnCreate() {
        setContentView(R.layout.activity_main);
        imageView = (ImageView) findViewById(R.id.imageView);
        statusText = (TextView) findViewById(R.id.statusText);
        button = (Button) findViewById(R.id.takePictureButton);
        PackageManager pm = getApplicationContext().getPackageManager();
        addressIP = (EditText) findViewById(R.id.addressIP);
        addressPort = (EditText) findViewById(R.id.addressPort);
        serverStatus = (TextView) findViewById(R.id.serverStatus);
        hasCameraFeature =  pm.hasSystemFeature(PackageManager.FEATURE_CAMERA);
        // from https://stackoverflow.com/questions/2982748/create-a-guid-in-java#2982751
        app_id = java.util.UUID.randomUUID();;
    }

    private int findFrontFacingCamera() {
        // Search for the front facing camera
        // from http://www.vogella.com/tutorials/AndroidCamera/article.html
        int numberOfCameras = Camera.getNumberOfCameras();
        for (int cameraId = 0; cameraId < numberOfCameras; cameraId++) {
            CameraInfo info = new CameraInfo();
            Camera.getCameraInfo(cameraId, info);
            if (info.facing == CameraInfo.CAMERA_FACING_BACK) {
                Log.d(DEBUG_TAG, "Camera found");
                return cameraId;
            }
        }
        return -1;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d(DEBUG_TAG, "onCreate");
        setAttributesOnCreate();



        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                tryToTakeAPicture();
            }
        });
    }

    private void tryToTakeAPicture() {
        if (cameraIsAvailable) {
            setCameraParameters();
            camera.startPreview();
            camera.takePicture(null, null,
                    new Camera.PictureCallback() {
                        @Override
                        public void onPictureTaken(byte[] data, Camera camera) {
                            Bitmap bm = BitmapFactory.decodeByteArray(data, 0, data.length);
                            imageView.setImageBitmap(bm);
                            camera.stopPreview();
                        }
                    });
        }
        notifyServer();
    }

    protected void setCameraParameters() {
        // https://developer.android.com/reference/android/hardware/Camera.Parameters
        //  	setJpegQuality(int quality)
        //  	setPictureSize(int width, int height)
        //  	getSupportedPictureSizes()
        Camera.Parameters params = camera.getParameters();
        Camera.Size maxSize = params.getSupportedPictureSizes().get(0);
        for (Camera.Size size : params.getSupportedPictureSizes()) {
            if (size.width >= maxSize.width && size.height > maxSize.height) {
                maxSize = size;
            }
        }
        params.setPictureSize(maxSize.width, maxSize.height);
        Log.d(DEBUG_TAG, "Camera resolution: " + maxSize.width + "x" + maxSize.height + "px");
        params.setJpegQuality(100); // no compression
        camera.setParameters(params);
    }

    @Override
    protected void onPause() {
        // from http://www.vogella.com/tutorials/AndroidCamera/article.html
        // see also https://developer.android.com/reference/android/hardware/Camera (10)
        if (cameraIsAvailable) {
            camera.release();
            camera = null;
        }
        super.onPause();
    }

    @Override
    protected void onResume() {
        // from https://developer.android.com/reference/android/hardware/Camera (10)

        openCamera();
        statusText.setText(cameraIsAvailable  ? R.string.camera_status_available  :
                           cameraIsDisabled   ? R.string.camera_status_disabled   :
                           !hasCameraFeature  ? R.string.camera_status_no_feature : R.string.TODO);
        super.onResume();
    }

    private void openCamera() {
        if (hasCameraFeature) {
            int cameraId = findFrontFacingCamera();
            try {
                camera = Camera.open(cameraId);
                cameraIsDisabled = false;
            } catch (RuntimeException e) {
                // this occurs if no permissions are given, see thedocumentation of Camera.open.
                cameraIsDisabled = true;
            }
        }
        cameraIsAvailable = hasCameraFeature && !cameraIsDisabled;
        if (cameraIsDisabled) {
            // from https://androidkennel.org/android-camera-access-tutorial/
            // imageView.setImageResource(); // TODO: change picture
            ActivityCompat.requestPermissions(this, new String[] {Manifest.permission.CAMERA}, 0);
        }
    }

    public int getPort() {
        // from https://stackoverflow.com/a/25804635/1320237
        try {
            return Integer.parseInt(addressPort.getText().toString());
        } catch (NumberFormatException e) {
            return DEFAULT_PORT;
        }
    }

    public String getHostname() {
        return addressIP.getText().toString();
    }

    public URL getServerUrl() throws MalformedURLException {
        return new URL("http", getHostname(), getPort(), "/scanner");
    }

    protected void notifyServer() {
        URL url;
        setServerStatus(R.string.server_status_starting_request);
        try {
            url = getServerUrl();
        } catch (MalformedURLException e) {
            e.printStackTrace();
            setServerStatus(R.string.server_status_malformed_url);
            return;
        }
        Log.d(DEBUG_TAG, "URL: " + url.toString());
        // see https://www.wikihow.com/Execute-HTTP-POST-Requests-in-Android
        HttpURLConnection client;
        try {
            client = (HttpURLConnection) url.openConnection();
        } catch (IOException e) {
            setServerStatus(R.string.server_status_connection_error);
            e.printStackTrace();
            return;
        }
        try {
            client.setRequestMethod("POST");
        } catch (ProtocolException e) {
            setServerStatus(R.string.server_status_protocol_exception);
            e.printStackTrace();
            return;
        }
        // from https://stackoverflow.com/a/34555324/1320237
        client.addRequestProperty("Accept", "application/json");
        client.addRequestProperty("Content-Type", "application/json");
        client.setDoOutput(true);
        client.setChunkedStreamingMode(0);
        // write data to the server
        DataOutputStream os;
        // from https://stackoverflow.com/q/42767249/1320237
        JSONObject notification = new JSONObject();
        try {
            notification.put("type", "scanner");
            notification.put("name", getDeviceName());
            notification.put("id", app_id.toString());
        } catch (JSONException e) {
            setServerStatus(R.string.server_status_create_notification_exception);
            e.printStackTrace();
            return;
        }
        try {
            os = new DataOutputStream(client.getOutputStream());
            os.writeBytes(notification.toString());
            os.flush();
            os.close();
        } catch (IOException e) {
            setServerStatus(R.string.server_status_send_notification_exception);
            e.printStackTrace();
            return;
        }
        Log.d(DEBUG_TAG, "POST request sent.");
        try {
            Log.i("STATUS", String.valueOf(client.getResponseCode()));
            Log.i("MSG" , client.getResponseMessage());
        } catch (IOException e) {
            setServerStatus(R.string.server_status_get_server_response_error);
            e.printStackTrace();
            return;
        }
        setServerStatus(R.string.server_status_get_server_response);

    }

    private void setServerStatus(int resourceId) {
        serverStatus.setText(resourceId);
    }

    public String getDeviceName() {
        // from https://stackoverflow.com/a/12707479/1320237
        String manufacturer = Build.MANUFACTURER;
        String model = Build.MODEL;
        if (model.toLowerCase().startsWith(manufacturer.toLowerCase())) {
            return capitalize(model);
        } else {
            return capitalize(manufacturer) + " " + model;
        }
    }


    private String capitalize(String s) {
        // form https://stackoverflow.com/a/12707479/1320237
        if (s == null || s.length() == 0) {
            return "";
        }
        char first = s.charAt(0);
        if (Character.isUpperCase(first)) {
            return s;
        } else {
            return Character.toUpperCase(first) + s.substring(1);
        }
    }

}
