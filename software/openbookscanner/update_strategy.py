from parse_rest.connection import ParseBatcher


class OnChangeStrategy:
    """When an object changes, it is saved asap."""
    
    def save(self, obj):
        """Save the object."""
        obj.save()
    
    def delete(self, obj):
        """Delete the object."""
        obj.delete()
    
    def __repr__(self):
        """String representation."""
        return self.__class__.__name__ + "()"


class BatchStrategy:
    """Store objects which want to be saved and save them later.
    """
    
    def __init__(self):
        """Create a new strategy.
        
        You may want to pass this to many a ParseUpdater.
        """
        self._batch = []
    
    def save(self, obj):
        """Save the object."""
        self._batch.append(obj.save)

    def delete(self, obj):
        """Delete the object."""
        self._batch.append(obj.delete)
    
    def batch(self):
        """Perform all the stored operations."""
        if self._batch:
            batcher = self.new_batcher()
            batcher.batch(self._batch)
            self._batch = []
     
    new_batcher = ParseBatcher
