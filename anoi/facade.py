import functools
import inspect
from . import basis, wordnet as wn


class ANOIFacade:
    def __init__(self, space_or_cls, verbose:bool = False, *args, **kws):
        is_cls = inspect.isclass(space_or_cls)
        if is_cls and issubclass(space_or_cls, basis.ANOISpace):
            self.space = space_or_cls(*args, **kws)
        elif isinstance(space_or_cls, basis.ANOISpace):
            self.space = space_or_cls
        else:
            raise TypeError(f'{space_or_cls} is not an instance or subtype '
                'of ANOISpace')
        self.namespace = basis.ANOINamespace(self.space, 'wordnet')
        self.name_uid = self.namespace.basis.get_name('NAME')
        self.loader = wn.ANOIWordNetLoader(self.namespace, verbose)
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

    def render_uid(self, uid: int) -> str:
        uid_to_html = self.uid_to_html
        space = self.space
        if not space.is_valid(uid):
            raise ValueError()
        iter_0 = ((uid_to_html(key), uid_to_html(space.cross(uid, key)))
            for key in sorted(space.get_keys(uid)))
        nav_iter = ((key if len(key) > 1 else f'"{key}"', value)
            for key, value in iter_0)
        navbar = ''.join(
            f'<li>{key} : {value}</li>' for key, value in nav_iter)
        contents = ''.join(
            uid_to_html(child) for child in space.get_content(uid))
        title = f'UID {uid} ({hex(uid)})'
        return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
  </head>
  <body>
    <h1>{title}</h1>
    <ul>{navbar}</ul>
    <p>{contents}</p>
  </body>
</html>
'''


@functools.cache
def get_facade(
    space_or_cls = basis.ANOIInMemorySpace, *args, **kws
) -> ANOIFacade:
    return ANOIFacade(space_or_cls, *args, **kws)
