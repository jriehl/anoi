'''A Network of Ideas builtin types.
'''
import dataclasses
import functools
from typing import Any, List, Optional, Union
from . import (
    ANOISpace,
    ANOITrieProxy,
    ANOINamespace
)


@dataclasses.dataclass
class ANOIProperty:
    name: str
    ty: Union['ANOIType', str]


@dataclasses.dataclass
class ANOIType:
    name: str
    properties: List[ANOIProperty] = dataclasses.field(default_factory=list)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.instantiate(*args, **kwds)

    def instantiate(self, space: ANOISpace, *args, **kws):
        result = ANOIAtom(space, None, self)
        result.load(*args, **kws)
        return result


class ANOIAtom:
    space: ANOISpace
    uid: int
    ty: Optional[ANOIType]

    def __init__(
        self,
        space: ANOISpace,
        uid: Optional[int] = None,
        type: Optional[ANOIType] = None,
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
        self.ty = type

    def load(self, *args, **kws) -> None:
        uid = self.uid
        content = tuple(self.obj_to_uid(obj) for obj in args)
        self.space.set_content(uid, content)
        for property_key, property_value in kws.items():
            self.space.cross_equals(
                uid,
                self.obj_to_uid(property_key),
                self.obj_to_uid(property_value)
            )

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


class ANOITypeReflector(ANOIAtom):
    def load(self, *args, **kws):
        raise NotImplementedError()


# class ANOIUserType(ANOIAtom, ANOIType):
#     def __init__(self, space: ANOISpace, name: str, properties) -> None:
#         pass


ANOIStringType = ANOIType('STRING', [ANOIProperty('TYPE', 'STRING')])
ANOIMediaType = ANOIType('MEDIA', [
    ANOIProperty('TYPE', 'MEDIA'),
    ANOIProperty('NAME', 'STRING'),
    ANOIProperty('MIME_TYPE', 'STRING'),
    # Need other metadata here including online origin and date.
])
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
