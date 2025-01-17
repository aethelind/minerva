from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from os import path
from .invertedindex import IndexValue
import pkg.index.ottawau as ottawau
import pkg.index.reuters as reuters


class BigramIndexAccessor:
    index = {}

    # private singleton class
    class __BigramIndexAccessor:
        def __init__(self, ctx):
            self.ctx = ctx
            if not path.exists(ctx.bigram_index_path()):
                self._build()
            with open(self.ctx.bigram_index_path(), "r") as bigram_index_handle:
                self.index = load(bigram_index_handle, Loader=Loader)

        def _build(self):
            if self.ctx.corpus_type() is "reuters":
                reuters.ReutersIndexBuilder(self.ctx).build_bigram_index()
            else:
                ottawau.OttawaUIndexBuilder(self.ctx).build_bigram_index()

    def __init__(self, ctx):
        if ctx.bigram_index_path() not in self.index:
            BigramIndexAccessor.index[
                ctx.bigram_index_path()
            ] = BigramIndexAccessor.__BigramIndexAccessor(ctx)

    def access(self, ctx, term):
        accessor = BigramIndexAccessor.index[ctx.bigram_index_path()].index
        try:
            return accessor[term]
        except KeyError:
            return []


class WeightedIndexAccessor:
    index = {}

    # private singleton class
    class __WeightedIndexAccessor:
        def __init__(self, ctx):
            self.ctx = ctx
            if not path.exists(ctx.weighted_index_path()):
                self._build()
            with open(self.ctx.weighted_index_path(), "r") as weighted_index_handle:
                self.index = load(weighted_index_handle, Loader=Loader)

        def _build(self):
            if self.ctx.corpus_type() is "reuters":
                reuters.ReutersIndexBuilder(self.ctx).build_weighted_index()
            else:
                ottawau.OttawaUIndexBuilder(self.ctx).build_weighted_index()

    def __init__(self, ctx):
        if ctx.weighted_index_path() not in self.index:
            WeightedIndexAccessor.index[
                ctx.weighted_index_path()
            ] = WeightedIndexAccessor.__WeightedIndexAccessor(ctx)

    def access(self, ctx, term):
        accessor = WeightedIndexAccessor.index[ctx.weighted_index_path()].index
        try:
            return accessor[term]
        except KeyError:
            return []


class IndexAccessor:
    index = {}

    # private 'constructor' for singleton
    # design pattern followed from: https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    # Note that the caller is responsible for ensuring both indices exist on disk, otherwise this will throw
    # FileNotFoundError
    class __IndexAccessor:
        def __init__(self, ctx):
            self.ctx = ctx
            if not path.exists(ctx.inverted_index_path()):
                self._build()
            with open(self.ctx.inverted_index_path(), "r") as index_handle:
                self.index = load(index_handle, Loader=Loader)

        def _build(self):
            if self.ctx.corpus_type() is "reuters":
                reuters.ReutersIndexBuilder(self.ctx).build()
            else:
                ottawau.OttawaUIndexBuilder(self.ctx).build()

    def __init__(self, ctx):
        # if the index is not yet in accessor, then opportunistically load the index
        if ctx.inverted_index_path() not in self.index:
            IndexAccessor.index[
                ctx.inverted_index_path()
            ] = IndexAccessor.__IndexAccessor(ctx)
            # is using the corpus_path as a dict key a bad idea?

    def access(self, ctx, term):
        accessor = IndexAccessor.index[ctx.inverted_index_path()]
        try:
            return accessor.index[term]
        except KeyError:
            return IndexValue(0, [])
