import functools
from . import basis, wordnet as wn


class ANOIFacade:
    def __init__(self, space_cls, *args, **kws):
        if not issubclass(space_cls, basis.ANOISpace):
            raise TypeError(f'{space_cls} is not a subtype of ANOISpace')
        self.space = space_cls(*args, **kws)
        self.namespace = basis.ANOINamespace(self.space, 'wordnet')
        self.name_uid = self.namespace.basis.get_name('NAME')
        self.loader = wn.ANOIWordNetLoader(self.namespace, True)
        if not self.loader.loaded:
            self.loader.load()

    @functools.lru_cache(maxsize=65536)
    def uid_to_html(self, uid):
        valid = self.space.is_valid(uid)
        if uid < 0x110000 and (char := chr(uid)).isprintable():
            uid_str = f'{char}'
        elif uid in basis.ANOIReservedSet:
            reserved = basis.ANOIReserved(uid)
            uid_str = reserved.name
        elif valid and (
            (name := self.space.cross(uid, self.name_uid)) !=
            basis.ANOIReserved.NIL.value
        ):
            uid_str = basis.vec_to_str(self.space.get_content(name))
        else:
            uid_str = hex(uid)
        return f'<a href="{hex(uid)}">{uid_str}</a>' if valid else uid_str


@functools.cache
def get_facade(
    space_cls = basis.ANOIInMemorySpace, *args, **kws
) -> ANOIFacade:
    return ANOIFacade(space_cls, *args, **kws)
