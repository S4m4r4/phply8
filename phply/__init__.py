import warnings as _w

with _w.catch_warnings():
    _w.simplefilter("ignore")
    try:
        __import__("pkg_resources").declare_namespace(__name__)
    except Exception:
        pass
