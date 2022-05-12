'''A Network of Ideas builtin types.
'''
import abc
import dataclasses
import functools
from typing import Any, Dict, List, Optional, Set, Union
from . import (
    ANOISpace,
    ANOITrieProxy,
    ANOINamespace,
)
from .atom import ANOIAtom


class ANOITypeVar:
    name: str


class ANOIAbstractType(abc.ABC):
    def check(self, atom: ANOIAtom) -> List[str]:
        '''Check that an atom is in this type, returning an empty list on
        success, or a non-empty list of error strings.
        '''
        raise NotImplementedError()

    def get_free_vars(self) -> Set[ANOITypeVar]:
        raise NotImplementedError()

    def build(self, *args, **kws) -> ANOIAtom:
        '''Returns an instance of this type where args are mapped to atom
        contents, and keywords mapped to properties.

        Raises TypeError if the type is open, and ValueError if the instance
        fails to type check.
        '''
        raise NotImplementedError()

    def reify(self, space: ANOISpace) -> ANOIAtom:
        '''Return an atom representing the current type.
        '''
        raise NotImplementedError()


@dataclasses.dataclass
class ANOIType(ANOIAbstractType):
    name: str
    properties: List['ANOIProperty'] = dataclasses.field(default_factory=list)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.instantiate(self, *args, **kwds)

    def check(self, atom: 'ANOIAtom') -> List[str]:
        result = []
        for prop in self.properties:
            if prop in atom:
                prop.get_type().check()
        return result

    def get_free_vars(self) -> Set['ANOITypeVar']:
        return set.union(*(prop.get_type().get_free_vars()
            for prop in self.properties))



# FIXME Not sure I have the nomenclature pinned down here.  The ANOIType is the
# type description dataclass, while the PyANOIType is a union of possible
# Python types that reference an ANOI type within a space.
PyANOIType = Union[ANOIType, str, int]


class ANOIGenericType(ANOIType):
    tyvars: Dict[ANOITypeVar, Optional[ANOIType]] = dataclasses.field(
        default_factory=dict)


@dataclasses.dataclass
class ANOIProperty:
    name: str
    ty: PyANOIType

    def get_type(self) -> ANOIAbstractType:
        raise NotImplementedError()


@functools.cache
def ty_to_uid(space: ANOISpace, ty: PyANOIType) -> int:
    if isinstance(ty, int):
        return ty
    else:
        tys = anoi_types(space)
        if isinstance(ty, str):
            return tys[ty]
        return tys[ty.name]


def instantiate(space: ANOISpace, ty: PyANOIType, *args, **kws):
    result = ANOIAtom(space)
    result.load(*args, **kws)
    return result


class ANOITypeReflector(ANOIAtom):
    def load(self, *args, **kws):
        raise NotImplementedError()


# class ANOIUserType(ANOIAtom, ANOIType):
#     def __init__(self, space: ANOISpace, name: str, properties) -> None:
#         pass


ANOIVectorType = ANOIGenericType('VECTOR', [])
ANOIStringType = ANOIType('STRING', [ANOIProperty('TYPE', 'STRING')])
ANOIMediaType = ANOIType('MEDIA', [
    ANOIProperty('TYPE', 'MEDIA'),
    ANOIProperty('NAME', 'STRING'),
    ANOIProperty('MIME_TYPE', 'STRING'),
    # Need other metadata here including online origin and date.
])
ANOIAuthorType = ANOIType('AUTHOR', [ANOIProperty('TYPE', 'AUTHOR')])
ANOIArticleType = ANOIType('ARTICLE', [
    ANOIProperty('TYPE', 'ARTICLE'),
    ANOIProperty('TITLE', 'STRING'),
    ANOIProperty('AUTHORS', None),  # FIXME!!!
    ANOIProperty('SOURCE', 'MEDIA'),
    ANOIProperty('DATE', 'DATE'),
])


BUILTINS = {
    'STRING': ANOIStringType,
}


@functools.cache
def anoi_types(space: ANOISpace) -> ANOITrieProxy:
    result = ANOITrieProxy(ANOINamespace(space, 'TYPES'))
    for builtin in ('STRING',):
        result[builtin] = space.get_uid()
    return result
