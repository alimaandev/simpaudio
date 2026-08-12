import sys
import threading
import traceback
from datetime import datetime
from tkinter import messagebox

from utils import ERROR_LOG
from ui.app import App


def _log_exception(exc_type, exc_value, exc_tb):
    details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n===== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n")
            f.write(details)
    except OSError:
        pass
    return details


def _handle_uncaught(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        return
    details = _log_exception(exc_type, exc_value, exc_tb)
    try:
        messagebox.showerror(
            "Simpaudio Error",
            "An unexpected error occurred:\n\n"
            f"{exc_value}\n\n"
            f"Details were saved to:\n{ERROR_LOG}",
        )
    except Exception:
        pass


def _handle_thread_exception(args):
    _log_exception(args.exc_type, args.exc_value, args.exc_traceback)


def main():
    sys.excepthook = _handle_uncaught
    threading.excepthook = _handle_thread_exception
    app = App()
    app.run()


if __name__ == "__main__":
    main()