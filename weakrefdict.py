import weakref


class WeakReferencableDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._weakrefs = []

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._weakrefs = []
        return obj

    def __del__(self):
        for ref in self._weakrefs:
            ref()

    def __int__(self):
        return self["id"]


def create_weakref(obj):
    weak_ref = weakref.ref(obj, (lambda *args, **kwargs: None))
    obj._weakrefs.append(weak_ref)
    return weak_ref
