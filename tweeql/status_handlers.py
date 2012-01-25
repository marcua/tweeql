from tweeql.exceptions import DbException
from tweeql.field_descriptor import ReturnType
from tweeql.exceptions import SettingsException
from tweeql.settings_loader import get_settings
from sqlalchemy import create_engine, Table, Column, Integer, Unicode, Float, DateTime, MetaData
from sqlalchemy.exc import ArgumentError, InterfaceError

settings = get_settings()

class StatusHandler(object):
    def __init__(self, batch_size):
        self.batch_size = batch_size
    def handle_statuses(self, statuses):
        raise NotImplementedError()
    def set_tuple_descriptor(self, descriptor):
        self.tuple_descriptor = descriptor

class PrintStatusHandler(StatusHandler):
    def __init__(self, batch_size, delimiter = u"|"):
        super(PrintStatusHandler, self).__init__(batch_size)
        self.delimiter = delimiter

    def handle_statuses(self, statuses):
        td = self.tuple_descriptor
        for status in statuses:
            vals = (unicode(val) for (alias, val) in status.as_iterable_visible_pairs())
            print self.delimiter.join(vals) + "\n"

class DbInsertStatusHandler(StatusHandler):
    engine = None

    def __init__(self, batch_size, tablename):
        super(DbInsertStatusHandler, self).__init__(batch_size)
        if DbInsertStatusHandler.engine == None:
            try:
                dburi = settings.DATABASE_URI
                dbconfig = None
                try:
                    dbconfig = settings.DATABASE_CONFIG
                except AttributeError:
                    pass
                kwargs = {'echo': False}
                if not dburi.startswith("sqlite"):
                    kwargs['pool_size'] = 1                    
                if dbconfig != None:
                    kwargs['connect_args'] = dbconfig
                DbInsertStatusHandler.engine = create_engine(dburi, **kwargs)
            except AttributeError, e:
                raise e
                raise SettingsException("To put results INTO a TABLE, please specify a DATABASE_URI in settings.py") 
            except ArgumentError, e:
                raise DbException(e)
        self.tablename = tablename

    def set_tuple_descriptor(self, descriptor):
        StatusHandler.set_tuple_descriptor(self, descriptor)
        metadata = MetaData()
        columns = []
        for alias in descriptor.aliases:
            desc = descriptor.get_descriptor(alias)
            if desc.visible:
                columns.append(self.db_col(alias, descriptor))
        columns.insert(0, Column('__id', Integer, primary_key=True))
        self.table = Table(self.tablename, metadata, *columns)
        try:
            metadata.create_all(bind=DbInsertStatusHandler.engine)
        except InterfaceError:
            raise SettingsException("Unable to connect to database.  Did you configure the connection properly?  Check DATABASE_URI and DATABASE_CONFIG in settings.py") 


        test = metadata.tables[self.tablename]
        self.verify_table()
   
    def db_col(self, alias, descriptor):
        return_type = descriptor.get_descriptor(alias).return_type
        type_val = None
        if return_type == ReturnType.INTEGER:
            type_val = Integer
        elif return_type == ReturnType.FLOAT:
            type_val = Float
        elif return_type == ReturnType.STRING:
            type_val = Unicode
        elif return_type == ReturnType.DATETIME:
            type_val = DateTime
        else:
            raise DbException("Unknown field return type: %s" % (return_type))
        return Column(alias, type_val)

    def verify_table(self):
        """
            Makes sure the table's schema is not different from the one in the database.
            This might happen if you try to load a query into a table which already
            exists and has a different schema.
        """
        metadata = MetaData()
        metadata.reflect(bind = DbInsertStatusHandler.engine)
        mine = str(self.table.columns)
        verified = str(metadata.tables[self.tablename].columns)
        if mine != verified:
            raise DbException("Table '%s' in the database has schema %s whereas the query's schema is %s" % (self.tablename, verified, mine)) 
 
    def handle_statuses(self, statuses):
        #from datetime import datetime
        #now = datetime.now()
        #print "handle called ", now 
        dicts = [dict(status.as_iterable_visible_pairs()) for status in statuses]
        conn = DbInsertStatusHandler.engine.connect()
        conn.execute(self.table.insert(), dicts)
        conn.close()
        #print "handle started ", now, " ended ", datetime.now()
