from openbookscanner.parse_update import OnChangeStrategy, BatchStrategy
from unittest.mock import Mock
from pytest import fixture


class TestOnChangeStrategy:

    @fixture
    def s(self):
        return OnChangeStrategy()

    def test_save(self, s, mock):
        s.save(mock)
        mock.save.assert_called_once_with()

    def test_delete(self, s, mock):
        s.delete(mock)
        mock.delete.assert_called_once_with()


class TestBatchStrategy:
    """
    Test the batch save strategy.
    
    https://github.com/milesrichardson/ParsePy#batch-operations
    """

    @fixture
    def batcher(self):
        return Mock()
        
    @fixture
    def s(self, batcher):
        s = BatchStrategy()
        s.new_batcher = lambda: batcher
        return s
    
    def test_save_waits(self, s, mock):
        s.save(mock)
        mock.save.assert_not_called()
        
    def test_delete_waits(self, s, mock):
        s.delete(mock)
        mock.delete.assert_not_called()

    def test_save(self, s, mock, batcher):
        s.save(mock)
        s.batch()
        batcher.batch.assert_called_once_with([mock.save])

    def test_save(self, s, mock, batcher):
        s.save(mock)
        s.batch()
        batcher.batch.assert_called_once_with([mock.save])

    def test_delete(self, s, mock, batcher):
        s.delete(mock)
        s.batch()
        batcher.batch.assert_called_once_with([mock.delete])

    def test_delete_batch_is_deleted(self, s, mock, batcher):
        s.delete(mock)
        s.batch()
        batcher.reset_mock()
        s.batch()
        batcher.batch.assert_not_called()

    def test_save_batch_is_deleted(self, s, mock, batcher):
        s.save(mock)
        s.batch()
        batcher.reset_mock()
        s.batch()
        batcher.batch.assert_not_called()


