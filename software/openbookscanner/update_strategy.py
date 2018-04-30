from parse_rest.connection import ParseBatcher
import collections

class NoCallback:

    def __call__(self):
        """Nothing happens."""
    
    def __repr__(self):
        """String represenatation."""
        return self.__class__.__name__ + "()"


class OnChangeStrategy:
    """When an object changes, it is saved asap."""
    
    def save(self, obj, callback=NoCallback()):
        """Save the object."""
        obj.save()
        callback()
    
    def delete(self, obj, callback=NoCallback()):
        """Delete the object."""
        obj.delete()
        callback()
        
    def addToArray(self, obj, array_name, objects, callback=NoCallback()):
        """Add objects to a named array."""
        # from https://stackoverflow.com/a/1952481
        assert isinstance(objects, collections.Iterable) and not isinstance(objects, str), "Please pass a list of objects."
        obj.addToArray(array_name, objects)
        callback()
    
    def removeFromArray(self, obj, array_name, objects, callback=NoCallback()):
        """Remove objects from a named array."""
        # from https://stackoverflow.com/a/1952481
        assert isinstance(objects, collections.Iterable) and not isinstance(objects, str), "Please pass a list of objects."
        obj.removeFromArray(array_name, objects)
        callback()

    def __repr__(self):
        """String representation."""
        return self.__class__.__name__ + "()"


class BatchStrategy(OnChangeStrategy):
    """Store objects which want to be saved and save them later.
    
    https://github.com/milesrichardson/ParsePy#batch-operations
    """
    
    def __init__(self):
        """Create a new strategy.
        
        You may want to pass this to many a ParseUpdater.
        """
        super().__init__()
        self._batch = []
    
    def save(self, obj, callback=NoCallback()):
        """Save the object."""
        self._batch.append((obj.save, callback))

    def delete(self, obj, callback=NoCallback()):
        """Delete the object."""
        self._batch.append((obj.delete, callback))
    
    # TODO: implement batch requests for object add and remove.
#    def addToArray(self, obj, key, value): 
#        """Remove a value from the array under key."""
#        raise NotImplementedError("If we implement this, publishing can be much faster.")
    
    def batch(self):
        """Perform all the stored operations."""
        if self._batch:
            batcher = self.new_batcher()
            while self._batch:
                # can send 50 operations
                # http://docs.parseplatform.org/rest/guide/#batch-operations
                batch, callbacks = zip(*self._batch[:50])
                self._batch = self._batch[50:]
                batcher.batch(list(batch))
                for callback in callbacks:
                    callback()
     
    new_batcher = ParseBatcher

