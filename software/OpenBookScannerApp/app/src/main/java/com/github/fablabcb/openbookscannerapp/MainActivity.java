package com.github.fablabcb.openbookscannerapp;

import android.Manifest;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.hardware.Camera;
import android.hardware.Camera.CameraInfo;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {

    private final static String DEBUG_TAG = "MainActivity";

    private ImageView imageView;
    private FloatingActionButton fab;
    private TextView statusText;
    private Toolbar toolbar;
    private boolean cameraIsAvailable;
    private boolean hasCameraFeature;
    private boolean cameraIsDisabled;
    private Camera camera;



    protected void setAttributesOnCreate() {
        setContentView(R.layout.activity_main);
        toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        imageView = (ImageView) findViewById(R.id.imageView);
        fab = (FloatingActionButton) findViewById(R.id.fab);
        statusText = (TextView) findViewById(R.id.statusText);
        PackageManager pm = getApplicationContext().getPackageManager();
        hasCameraFeature =  pm.hasSystemFeature(PackageManager.FEATURE_CAMERA);
        if (hasCameraFeature) {
            int cameraId = findFrontFacingCamera();
            try {
                camera = Camera.open(cameraId);
                cameraIsDisabled = false;
            } catch (RuntimeException e) {
                cameraIsDisabled = true;
            }
        }
        cameraIsAvailable = hasCameraFeature && !cameraIsDisabled;
    }

    private int findFrontFacingCamera() {
        // Search for the front facing camera
        // from http://www.vogella.com/tutorials/AndroidCamera/article.html
        int numberOfCameras = Camera.getNumberOfCameras();
        for (int cameraId = 0; cameraId < numberOfCameras; cameraId++) {
            CameraInfo info = new CameraInfo();
            Camera.getCameraInfo(cameraId, info);
            if (info.facing == CameraInfo.CAMERA_FACING_FRONT) {
                Log.d(DEBUG_TAG, "Camera found");
                return cameraId;
            }
        }
        return -1;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setAttributesOnCreate();


        statusText.setText(cameraIsAvailable ? "A camera is available." :
                           cameraIsDisabled  ? "Camera use is disabled for this app: no permission." :
                           !hasCameraFeature  ? "This app has no camera feature." : "TODO");
        if (!cameraIsAvailable) {
            // from https://androidkennel.org/android-camera-access-tutorial/
            // imageView.setImageResource(); // TODO: not picture
            ActivityCompat.requestPermissions(this, new String[] { Manifest.permission.CAMERA, Manifest.permission.WRITE_EXTERNAL_STORAGE }, 0);
        }

        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (cameraIsAvailable) {
                    camera.startPreview();
                    camera.takePicture(null, null,
                            new Camera.PictureCallback() {
                                @Override
                                public void onPictureTaken(byte[] data, Camera camera) {
                                    Bitmap bm = BitmapFactory.decodeByteArray(data, 0, data.length);
                                    imageView.setImageBitmap(bm);
                                }
                            });
                }
            }
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }


    @Override
    protected void onPause() {
        // from http://www.vogella.com/tutorials/AndroidCamera/article.html
        if (camera != null) {
            camera.release();
            camera = null;
        }
        super.onPause();
    }
}
