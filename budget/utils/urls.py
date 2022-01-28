from django.urls import path


class Path:
    def __init__(self, path: str, *args, **kwargs):
        self.path = path
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        for path_prefix in ["", "api/"]:
            yield path(f"{path_prefix}{self.path}", *self.args, **self.kwargs)
