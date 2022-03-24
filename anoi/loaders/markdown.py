from ast import literal_eval
import dataclasses
from typing import Iterable, List, Tuple
from lxml.etree import Element

HEADERS = set(f'h{num}' for num in range(1, 7))

@dataclasses.dataclass
class ArticleScaffold:
    level: int
    elem: Element
    children : List['ArticleElement'] = dataclasses.field(default_factory=list)

    def append(self, child: 'ArticleElement'):
        self.children.append(child)

    def asfrozen(self) -> 'ArticleElement':
        return ArticleElement(
            self.level,
            self.elem,
            tuple(child.asfrozen() for child in self.children)
        )

@dataclasses.dataclass(eq=True, frozen=True)
class ArticleElement:
    level: int
    elem: Element
    children: Tuple['ArticleElement'] = dataclasses.field(
        default_factory=tuple)

def derive_article_structure(elem: Element) -> ArticleElement:
    top_of_stack = ArticleScaffold(0, elem)
    stack = [top_of_stack]
    def build_article(elem: Element):
        for child in elem:
            tag = child.tag
            if tag in HEADERS:
                crnt_index = literal_eval(tag[1:])
                while stack[-1].level >= crnt_index:
                    # Pop.
                    stack.pop()
                new_tos = ArticleScaffold(crnt_index, child)
                stack[-1].append(new_tos)
                stack.append(new_tos)
            else:
                stack[-1].append(ArticleScaffold(stack[-1].level, child))
                if len(child) > 0 and tag not in {'p', 'ul', 'ol'}:
                    build_article(child)
    build_article(elem)
    return top_of_stack.asfrozen()

def walk_article(article: ArticleElement) -> Iterable[ArticleElement]:
    yield article
    for child in article.children:
        for descendant in walk_article(child):
            yield descendant
