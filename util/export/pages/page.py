from abc import ABC,abstractmethod

class Page(ABC):
    @abstractmethod
    def pageWidgetConstraint(self):
        pass

    @abstractmethod
    def collectionConstraint(self):
        pass

    @abstractmethod
    def resolveBibtexReference(predobjs, item, graph):
        pass

    @abstractmethod
    def generatePageWidget(self, graph, memberid, templates, f, pageWidget=False):
        pass

    @abstractmethod
    def generateCollectionWidget(self, graph, templates, subject, f):
        pass