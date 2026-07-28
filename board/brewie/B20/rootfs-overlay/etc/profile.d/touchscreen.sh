# Modern Qt input/display settings corresponding to the legacy touchscreen
# configuration.  The current image uses DRM framebuffer emulation and the
# linuxfb QPA plugin rather than the old eglfs/tslib stack.
export QT_QPA_PLATFORM="linuxfb:fb=/dev/fb0"
export QT_QPA_EVDEV_TOUCHSCREEN_PARAMETERS="rotate=180"
export QT_QPA_EVDEV_MOUSE_PARAMETERS="rotate=270:dejitter=10"
