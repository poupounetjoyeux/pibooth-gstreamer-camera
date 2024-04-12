"""Plugin to handle camera that needs custom GStreamer command to work with OpenGL"""
import os
import pibooth
from pibooth.utils import LOGGER
from pibooth.camera.opencv import CvCamera
try:
    import cv2
except ImportError:
    cv2 = None  # OpenCV is optional

__version__ = "1.0.0"

@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options."""
    cfg.add_option('CAMERA', 'gstreamer_pipeline', '', "The full GStreamer pipeline. Don't forget to append 'appsink drop=1' at the end of the pipeline")
    cfg.add_option('CAMERA', 'gstreamer_prepare_commands', '', "A set of shell command to execute before starting the GStreamer pipeline")

@pibooth.hookimpl
def pibooth_setup_camera(cfg):
    gstreamer_pipeline = cfg.get('CAMERA', 'gstreamer_pipeline')
    if not gstreamer_pipeline:
        raise EnvironmentError("No GStreamer pipeline defined")

    sh_commands = cfg.gettuple('CAMERA', 'gstreamer_prepare_commands', str)
    if sh_commands:
        for sh_command in sh_commands:
            os.system(sh_command)
            LOGGER.info(f"Preparing camera with shell : {sh_command} ...")
    
    cv_camera = cv2.VideoCapture(gstreamer_pipeline)
    if cv_camera.isOpened():
        LOGGER.info(f"Configuring camera using custom GStreamer pipeline : {gstreamer_pipeline} ...")
        return CvCamera(cv_camera)
        
    raise EnvironmentError(f"Unable to instantiate the custom GStreamer camera using : {gstreamer_pipeline}")