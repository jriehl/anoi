from typing import Optional
from lxml import etree
import markdown as md

from . import article
from .. import basis

class ANOIMarkupLoader:
    def __init__(self, namespace: basis.ANOINamespace, verbose: bool = False):
        self.namespace = namespace
        self.html: Optional[etree.Element] = None
        self.struct: Optional[article.ArticleElement] = None

    def load(self, source, **kws):
        self.html = etree.HTML(source)
        self.struct = article.derive_article_structure(self.html)
        return self.struct

class ANOIMarkdownLoader(ANOIMarkupLoader):
    def load(self, source, **kws):
        return super().load(md.markdown(source), **kws)
