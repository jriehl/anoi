import itertools
from typing import Any, Dict, Iterable, Optional, Tuple
from . import (
    ANOISpace,
    ANOINamespace,
)


class ANOIAtom:
    '''Utility class for an ANOI atom proxy.
    '''
    space: ANOISpace
    uid: int
    contents: Optional[Tuple[int]] = None
    properties: Optional[Dict[int, int]] = None

    def __init__(
        self,
        space: ANOISpace,
        uid: Optional[int] = None,
        default_namespace: Optional[ANOINamespace] = None,
    ):
        self.space = space
        if uid is None:
            self.uid = space.get_uid()
        else:
            space.check(uid)
            self.uid = uid
        if default_namespace is not None:
            self.default_namespace = default_namespace
        else:
            self.default_namespace = ANOINamespace.get(space, 'wordnet')

    def load(self):
        self.contents = self.space.get_content(self.uid)
        self.properties = dict(
            (key, self.space.cross_equals(self.uid, key))
            for key in self.space.get_keys(self.uid))

    def store(self):
        if self.contents is None or self.properties is None:
            raise ValueError('unable to store uninitialized ANOIAtom')
        self.space.set_content(self.contents)
        for key, value in self.properties.items():
            self.space.cross_equals(self.uid, key, value)

    def _build(self, *args, **kws) -> Tuple[Tuple[int], Dict[int, int]]:
        return (
            tuple(self.obj_to_uid(obj) for obj in args),
            dict((self.obj_to_uid(key), self.obj_to_uid(value))
                for key, value in kws.items())
        )

    def build(self, *args, **kws) -> None:
        self.contents, self.properties = self._build(*args, **kws)

    def append(self, *args, **kws) -> None:
        tail, updates = self._build(*args, **kws)
        self.contents = tuple(itertools.chain(self.contents, tail))
        self.properties = self.properties.update(updates)

    def set_contents_from_string(self, in_str: str) -> None:
        '''Utility for quickly loading a sole Unicode string into an atom.
        May be overridden to throw a TypeError if the atom type doesn't support
        arbitrary length strings, or UID's in the Unicode code point range.
        '''
        self.contents = tuple(ord(ch) for ch in in_str)

    def obj_to_uid(self, obj: Any) -> int:
        if isinstance(obj, int):
            self.space.check(obj)
            return obj
        elif isinstance(obj, str):
            return self.default_namespace.get_name(obj)
        elif isinstance(obj, ANOIAtom):
            return obj.uid
        else:
            raise TypeError(f"unhandled input type '{type(obj)}'")
