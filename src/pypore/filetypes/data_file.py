"""
Created on Jan 28, 2014

@author: `@parkin1`_
"""

import tables as tb


class DataFile(tb.file.File):
    """
    PyTables HDF5 database storing raw data.
    Inherits from tables.file.File, so you can interact with this
    just as you would a PyTables File object. However, this contains
    some extra convenience methods for storing/reading data. Note that 
    DataFile allows you to interact
    with this PyTables file in the usual PyTables file manner, so you
    can potentially mangle the data from the original DataFile
    format.
    
    Automatically adds matrix
    /data
    
    Must be instantiated by calling :py:func:`pypore.dataFile.open_file`
    
    >>> import pypore.dataFile as dF
    >>> database = dF.open_file(tests,mode='w')
    >>> # Now do stuff with the DataFile
    >>> # ...
    >>> # Close and remove the DataFile
    >>> database.close()
    >>> os.remove(tests)
    """

    def clean_database(self):
        """
        Removes /events and then re-initializes the /events group. Note
        that any references to any table/matrix in this group will
        be broken and need to be refreshed.
        
        >>> h5 = open_file(tests,mode='a')
        >>> table = h5.get_event_table()
        >>> h5.clean_database() // table is now refers to deleted table
        >>> table = h5.get_event_table() // table now refers to live table
        """
        # remove the events group
        self.root._f_remove(recursive=True)

        self.initialize_database()

    @classmethod
    def _convert_to_event_database(cls, tables_object):
        """
        Converts a PyTables object's __class__ field to DataFile so
        you can use the object as an DataFile object.
        """
        tables_object.__class__ = DataFile

    def get_data_length(self):
        """
        Note this will flush the table so the data is correct.
        :returns: The number of rows in the data matrix.
        """
        self.root.data.flush()
        return self.root.data.nrows

    def get_sample_rate(self):
        """
        :returns: The sample rate at root.events.eventTable.attrs.sampleRate
        """
        return self.root.attrs.sampleRate

    def initialize_database(self, **kargs):
        """
        Initializes the EventDatabase.  Adds a group 'events' with
        table 'eventsTable' and matrices 'rawData', 'levels', and 'levelLengths'.
        
        :param kargs: Can pass in 'maxEventLength': Maximum number of data points for an event to be added.
        """

        filters = tb.Filters(complib='blosc', complevel=4)
        shape = (kargs['nPoints'],)
        a = tb.FloatAtom()
        if not 'data' in self.root:
            self.createCArray(self.root, 'data', a, shape=shape, title='Data', filters=filters)

        # set the attributes
        self.root.data.attrs.sampleRate = kargs['sampleRate']


def open_file(*args, **kargs):
    """
    Opens a :py:class:`DataFile`, which is a subclass of :py:class:`tables.file.File` and can be treated as such.

    :param args: Arguments that get passed to :py:func:`tables.openFile`.
    :param kargs: Arguments that get passed to :py:func:`tables.openFile`. Should additionally include:

        - nPoints: Number of points that should be in the array.
        - sampleRate: Sample rate of the data.

    :returns: :py:class:`pypore.filetypes.data_file.DataFile` -- an already opened
        :py:class:`pypore.filetypes.data_file.DataFile`.

    >>> import pypore.dataFile as dF
    >>> dF.open_file(tests', mode='w')
    """
    f = tb.openFile(*args, **kargs)
    DataFile._convert_to_event_database(f)
    if 'mode' in kargs:
        mode = kargs['mode']
        if 'w' in mode or 'a' in mode:
            f.initialize_database(**kargs)
    return f