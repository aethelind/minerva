from yaml import load_all

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class CorpusAccessor:
    # private 'constructor' for singleton
    # design pattern followed from: https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    class __CorpusAccessor:
        def __init__(self, ctx):
            self.ctx = ctx
            self.documents = {}

            with open(self.ctx.corpus_path(), "r") as corpus_handle:
                corpus_stream = load_all(corpus_handle, Loader=Loader)
                for doc in corpus_stream:
                    self.documents[doc.id] = doc

    corpora = {}

    def __init__(self, ctx):
        self.ctx = ctx
        # if the corpus is not yet in accessor, then load the corpus and put it in corpora
        if not ctx.corpus_path() in self.corpora:
            CorpusAccessor.corpora[ctx.corpus_path()] = CorpusAccessor.__CorpusAccessor(
                ctx
            )

    def access(self, ctx, doc_ids):
        if not doc_ids:
            print("No document IDs given.")
            return []
        elif not ctx.corpus_path() in self.corpora:
            print("Corpus not loaded into memory.")
            return []

        accessor = self.corpora[ctx.corpus_path()]
        results = []

        for i in doc_ids:
            if i in accessor.documents:
                results.append(accessor.documents[i])
            else:
                print("Invalid document id given: " + str(i))

        return results

    def get_size(self):
        if not self.ctx.corpus_path() in self.corpora:
            return 0

        return len(self.corpora[self.ctx.corpus_path()].documents)
