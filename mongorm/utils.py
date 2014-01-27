

def setdefaultattr(obj, name, default):
    if not hasattr(obj, name):
        setattr(obj, name, default)
    return getattr(obj, name)
