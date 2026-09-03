import sys
import typing

# Python 3.10 backward compatibility polyfill for PEP 655 (NotRequired / Self)
if sys.version_info < (3, 11):
    try:
        import typing_extensions
        if not hasattr(typing, "NotRequired"):
            typing.NotRequired = typing_extensions.NotRequired
        if not hasattr(typing, "Self"):
            typing.Self = typing_extensions.Self
        if not hasattr(typing, "TypeAlias"):
            typing.TypeAlias = getattr(typing_extensions, "TypeAlias", None)
    except ImportError:
        pass
