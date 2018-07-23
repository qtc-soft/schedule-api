from asyncpgsa import create_pool, compile_query
from asyncpg.pool import Pool
from sqlalchemy.dialects.postgresql.base import PGDialect


# metaclass Singleton
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# Singleton DB Connection instance (postgresql)
class DBManager(metaclass=Singleton):
    __slots__ = ('_pool', '_config')

    def __init__(self):
        # connections pool
        self._pool = None
        # config for connection to DB
        self._config = {}

    # set settings for db-connections
    def set_settings(self, config: dict):
        self._config = dict(
            user=config.get('user'),
            password=config.get('password'),
            database=config.get('database'),
            host=config.get('host'),
            port=config.get('port'),
            min_size=5,
            max_size=10,
        )

    # initial connections-pool
    async def init_pool(self):
        # dsn for connections
        dsn = 'postgresql://%s:%s@%s:%s/%s' % \
              (self._config['user'], self._config['password'], self._config['host'],
               self._config['port'], self._config['database'])
        # create pool
        self._pool = await create_pool(
            dsn=dsn,
            min_size=self._config.get('min_size', 5),
            max_size=self._config.get('max_size', 10),
            dialect=PGDialect()
        )

    # get connections-pool
    async def get_pool(self) -> Pool:
        if not self._pool:
            await self.init_pool()
        return self._pool

    # execute query
    async def query_execute(self, query):
        query_string, params = compile_query(query)
        async with (await self.get_pool()).acquire() as conn:
            return await conn.execute(query_string, *params)

    # execute query and return one row
    async def query_fetchrow(self, query):
        query_string, params = compile_query(query)
        async with (await self.get_pool()).acquire() as conn:
            return await conn.fetchrow(query_string, *params)

    # execute query and return all rows
    async def query_fetch(self, query):
        query_string, params = compile_query(query)
        async with (await self.get_pool()).acquire() as conn:
            return await conn.fetch(query_string, *params)

    # execute query and return column[0]
    async def query_fetchval(self, query, column=0):
        """ return a value in the first row. """
        query_string, params = compile_query(query)
        async with (await self.get_pool()).acquire() as conn:
            return await conn.fetchval(query_string, *params, column=column)

    # handler to graceful terminate application
    async def on_shutdown(self, app=None) -> None:
        await self.shutdown()

    # close connections-pool
    async def shutdown(self):
        # close db pool
        if self._pool:
            await self._pool.close()
