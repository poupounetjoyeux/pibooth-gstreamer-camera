# pibooth-gstreamer-camera plugin
Provide a way to configure an OpenCv camera using a custom GStreamer pipeline for [pibooth](https://github.com/pibooth/pibooth)

### Initial issue
This plugin has been developed following issue using a C790 HDMI adapter for my pibooth instance
When using it with a GoPro camera and a resolution of 1920x180 at 50fps, I got a 'colorimetry 2:3:5:4 is not supported by your device' error

After investigation, it seems that pibooth uses the default OpenCv configuration with the device meaning to implicitly use a RGB3 colorimetry when the device is streaming with a BT601 colorimetry

Second issue was regarding timing, captures was taken to early after setting the resolution, this added a big green line in the bottom of the photo

This implies to have a custom GStreamer pipeline used with OpenCv and custom delay

### Installation
To install this plugin, you can simply use pip. pibooth will automatically enable discover and enable it
```
pip install git+https://github.com/poupounetjoyeux/pibooth-gstreamer-camera.git@v1.0.0
```

### Configuration
Search for your working GStreamer pipeline reagarding your device
You can directly test it using command line without starting pibooth until you find the right settings
Don't hesitate to read the [GStreamer plugins documentation](https://gstreamer.freedesktop.org/documentation/plugins_doc.html)

For the C790, the working GStreamer pipeline for me is
```
v4l2src ! video/x-raw,width=1920,height=1080,framerate=50/1,format=UYVY,colorimetry=bt601 ! videoconvert ! appsink drop=1
```

Update your pibooth config like this
```
[CAMERA]

# The full GStreamer pipeline. Don't forget to append 'appsink drop=1' at the end of the pipeline
gstreamer_pipeline = v4l2src ! video/x-raw,width=1920,height=1080,framerate=50/1,format=UYVY,colorimetry=bt601 ! videoconvert ! appsink drop=1

# Must be greater than 0.5s to ensure OpenCv will have the time to resize the capture frame. By default or if lower, will use 0.5s
smile_display_delay = 0.5
```
**Don't forget to add 'appsink drop=1' at the end of your pipeline. This is mandatory to make it work correctly with OpenCv**

### Thanks
Thanks to the [pibooth](https://github.com/pibooth/pibooth) team that make a really great and amazing job!

