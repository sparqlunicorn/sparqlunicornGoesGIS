from .uiutils import UIUtils
from ..sparqlutils import SPARQLUtils
from qgis.PyQt.QtCore import QSortFilterProxyModel, Qt

class ClassTreeSortProxyModel(QSortFilterProxyModel):
    """Sorting proxy model that always places folders on top."""
    def __init__(self, sourcemodel=None):
        super().__init__()
        self.sort(0)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        if sourcemodel!=None:
            self.setSourceModel(sourcemodel)

    def lessThan(self, left, right):
        """Perform sorting comparison.

        Since we know the sort order, we can ensure that folders always come first.
        """
        left_is_class = (left.data(UIUtils.dataslot_nodetype)==SPARQLUtils.classnode or left.data(UIUtils.dataslot_nodetype)==SPARQLUtils.geoclassnode)
        left_data = str(left.data(Qt.DisplayRole))
        right_is_class = (right.data(UIUtils.dataslot_nodetype)==SPARQLUtils.classnode or right.data(UIUtils.dataslot_nodetype)==SPARQLUtils.geoclassnode)
        right_data = str(right.data(Qt.DisplayRole))
        sort_order = self.sortOrder()

        if left_is_class and not right_is_class:
            result = sort_order == Qt.AscendingOrder
        elif not left_is_class and right_is_class:
            result = sort_order != Qt.AscendingOrder
        else:
            result = left_data < right_data
        return result

    def filter_accepts_row_itself(self, row_num, parent):
        return super(ClassTreeSortProxyModel, self).filterAcceptsRow(row_num, parent)

    def filter_accepts_any_parent(self, parent):
        while parent.isValid():
            if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False

    def has_accepted_children(self, row_num, parent):
        ''' Starting from the current node as root, traverse all
            the descendants and test if any of the children match
        '''
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)

        children_count =  model.rowCount(source_index)
        for i in range(children_count):
            if self.filterAcceptsRow(i, source_index):
                return True
        return False

    def filterAcceptsRow(self, source_row, source_parent):
        # check if an item is currently accepted
        if self.filter_accepts_row_itself(source_row, source_parent):
            return True
            # Traverse up all the way to root and check if any of them match
        if self.filter_accepts_any_parent(source_parent):
            return True
        if self.has_accepted_children(source_row,source_parent):
            return True
        return False