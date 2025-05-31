from ._get_frame import _get_frame

def getframe(depth, number=0):
    frame = _get_frame(depth + (4 + number))
    code = frame.f_code

    try:
        name = frame.f_globals["__name__"]
    except KeyError:
        name = None

    return (name, code.co_name, frame.f_lineno)