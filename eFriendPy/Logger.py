from datetime import datetime


class DefaultLogger:
    def __init__(self, headerTimeFormat="[%Y/%m/%d %H:%M:%S]") -> None:
        self.headerTimeFormat = headerTimeFormat

    def __call__(self, msg):
        print(self.Format(msg))

    def Header(self):
        return datetime.now().strftime(self.headerTimeFormat)

    def Format(self, msg):
        return f"{self.Header()} {msg}"