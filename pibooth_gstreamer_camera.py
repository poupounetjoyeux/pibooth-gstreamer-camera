"""Plugin to handle camera that needs custom GStreamer pipeline to work with OpenGL"""
import time
import pibooth
from pibooth.utils import LOGGER
from pibooth.camera.opencv import CvCamera
import cv2

__version__ = "1.0.0"

class CvCameraWithDelay(CvCamera):

    def __init__(self, camera_proxy, smile_display_delay):
        super(CvCameraWithDelay, self).__init__(camera_proxy)
        self.smile_display_delay = smile_display_delay

    def capture(self, effect=None):
        """Capture a new picture.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        if self.capture_iso != self.preview_iso:
            self._cam.set(cv2.CAP_PROP_ISO_SPEED, self.capture_iso)

        time.sleep(self.smile_display_delay)  # To let time to see "Smile"
        LOGGER.debug("Taking capture at resolution %s", self.resolution)
        ret, image = self._cam.read()
        if not ret:
            raise IOError("Can not capture frame")
        image = self._rotate_image(image, self.capture_rotation)

        LOGGER.debug("Putting preview resolution back to %s", self._preview_resolution)
        self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, self._preview_resolution[0])
        self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self._preview_resolution[1])

        if self.capture_iso != self.preview_iso:
            self._cam.set(cv2.CAP_PROP_ISO_SPEED, self.preview_iso)

        self._captures.append((image, effect))

        self._hide_overlay()  # If stop_preview() has not been called

@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('CAMERA', 'gstreamer_pipeline', '', "The full GStreamer pipeline. Don't forget to append 'appsink drop=1' at the end of the pipeline")
    cfg.add_option('CAMERA', 'smile_display_delay', 0.5, " Must be greater than 0.5s to ensure OpenCv will have the time to resize the capture frame. By default or if lower, will use 0.5s")
    
@pibooth.hookimpl
def pibooth_setup_camera(cfg):
    gstreamer_pipeline = cfg.get('CAMERA', 'gstreamer_pipeline')
    if not gstreamer_pipeline:
        raise EnvironmentError("No GStreamer pipeline defined, please update the pibooth configuration by adding  in the [CAMERA] section")
    
    smile_display_delay = cfg.getfloat('CAMERA', 'smile_display_delay')
    if not smile_display_delay:
        smile_display_delay = 0.5
 
    cv_camera = cv2.VideoCapture(gstreamer_pipeline)
    if cv_camera.isOpened():
        LOGGER.info(f"Configuring OpenCv camera using GStreamer pipeline : {gstreamer_pipeline} ...")
        return CvCameraWithDelay(cv_camera, smile_display_delay)
        
    raise EnvironmentError(f"Unable to instantiate the OpenCv camera using GStreamer pipeline : {gstreamer_pipeline}")