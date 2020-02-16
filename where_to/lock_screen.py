import os

from .windows import Windows


logon_screen_dimensions = [
    (1360, 768),
    (1280, 768),
    (1920, 1200),
    (1440, 900),
    (1600, 1200),
    (1280, 960),
    (1024, 768),
    (1280, 1024),
    (1024, 1280),
    (960, 1280),
    (900, 1440),
    (768, 1280),
]


def show(lock_image):
    # change the logon UI background if on Windows 7. From learning at
    # http://www.withinwindows.com/2009/03/15/windows-7-to-officially-support-logon-ui-background-customization/
    if not Windows.is_windows_7():
        print("not windows 7")
        return

    logon_background_dir = r"%(windir)s\system32\oobe\info\backgrounds" % os.environ

    if not os.path.exists(logon_background_dir):
        os.makedirs(logon_background_dir)

    logon_background_path = os.path.join(logon_background_dir, "background%dx%d.jpg" % lock_image.size)
    quality = 80
    with Windows.disable_file_system_redirection():
        while quality > 0:
            lock_image.save(logon_background_path, "JPEG", quality=quality)
            file_size = os.path.getsize(logon_background_path)
            if file_size < 256 * 1000:
                break
            quality -= 5


def get_best_size():
    screen_size = Windows.get_screen_size()
    for possible_screen_size in logon_screen_dimensions:
        if possible_screen_size[0] * screen_size[1] == possible_screen_size[1] * screen_size[0]:
            return possible_screen_size

    return logon_screen_dimensions[0]
