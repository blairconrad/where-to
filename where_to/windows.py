import ctypes
import sys


class Windows:
    SM_CXSCREEN = 0
    SM_CYSCREEN = 1

    @classmethod
    def get_screen_size(cls):
        width = ctypes.windll.user32.GetSystemMetrics(Windows.SM_CXSCREEN)
        height = ctypes.windll.user32.GetSystemMetrics(Windows.SM_CYSCREEN)
        return (width, height)

    @classmethod
    def is_windows_7(cls):
        windows_version = sys.getwindowsversion()
        return windows_version.major == 6 and windows_version.minor == 1

    class disable_file_system_redirection:
        _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
        _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

        @classmethod
        def __enter__(self):
            self.old_value = ctypes.c_long()
            self.success = self._disable(ctypes.byref(self.old_value))

        @classmethod
        def __exit__(self, type, value, traceback):
            if self.success:
                self._revert(self.old_value)
