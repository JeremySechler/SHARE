from queue import Empty
import logging
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings

from elasticsearch import Elasticsearch

from raven.contrib.django.raven_compat.models import client

from share.search.indexing import ESIndexer


logger = logging.getLogger(__name__)


class SearchIndexerDaemon(threading.Thread):

    @classmethod
    def spawn(cls, *args, **kwargs):
        inst = cls(*args, **kwargs)
        runner = threading.Thread(target=inst.run)
        runner.daemon = True
        runner.start()
        return inst

    def __init__(self, celery_app, queue_name, indexes, url=None):
        super(self).__init__(daemon=True)  # It's fine to kill this thread whenever if need be

        self._initialized = False
        self.celery_app = celery_app

        self.rabbit_connection = None
        self.rabbit_queue = None
        self.rabbit_queue_name = queue_name

        self.es_client = None
        self.es_indexes = indexes
        self.es_url = url or settings.ELASTICSEARCH_URL

        self.connection_errors = ()
        self.keep_running = threading.Event()

    def initialize(self):
        logger.info('Initializing %r', self)

        logger.debug('Connecting to Elasticsearch cluster at "%s"', self.es_url)
        try:
            self.es_client = Elasticsearch(
                self.es_url,
                retry_on_timeout=True,
                timeout=settings.ELASTICSEARCH_TIMEOUT,
                # sniff before doing anything
                sniff_on_start=True,
                # refresh nodes after a node fails to respond
                sniff_on_connection_fail=True,
                # and also every 60 seconds
                sniffer_timeout=60
            )
        except Exception as e:
            client.captureException()
            raise RuntimeError('Unable to connect to Elasticsearch cluster at "{}"'.format(self.es_url)) from e

        logger.debug('Creating queue "%s" in RabbitMQ', self.rabbit_queue_name)
        try:
            self.rabbit_connection = self.celery_app.pool.acquire(block=True)
            self.rabbit_queue = self.rabbit_connection.SimpleQueue(self.rabbit_queue_name, **settings.ELASTIC_QUEUE_SETTINGS)
        except Exception as e:
            client.captureException()
            raise RuntimeError('Unable to create queue "{}"'.format(self.rabbit_queue_name)) from e

        self.connection_errors = self.rabbit_connection.connection_errors
        logger.debug('connection_errors set to %r', self.connection_errors)

        # TODO
        # Set an upper bound to avoid fetching everything in the queue
        logger.info('Setting prefetch_count to %d', self.max_size * 1.1)
        self.rabbit_queue.consumer.qos(prefetch_count=int(self.max_size * 1.1), apply_global=True)

        logger.debug('%r successfully initiialized', self)
        self._initialized = True

    def start(self):
        self.initialize()
        return super(self).start()

    def stop(self):
        logger.info('Stopping %r', self)
        self._running.clear()
        return self.join()

    def run(self):
        futures = []
        with ThreadPoolExecutor(max_workers=5) as pool:
            while self._running.is_set():
                messages = self._read_messages(max_size=500, timeout=10)
                if not messages:
                    continue
                futures.append(pool.submit(self._index, messages))
                # TODO Check errors/resolve futures

    def _index(self, messages):
        try:
            pass
            # construct stream
            # pipe to bulk index helper
        except self.connection_errors as e:
            pass
        except Exception as e:
            pass


        # try:
        #     self._run(queue)
        # except KeyboardInterrupt:
        #     logger.warning('Recieved Interrupt. Exiting...')
        #     return
        # except Exception as e:
        #     client.captureException()
        #     logger.exception('Encountered an unexpected error')

        #     if self.messages:
        #         try:
        #             self.flush()
        #         except Exception:
        #             client.captureException()
        #             logger.exception('%d messages could not be flushed', len(self.messages))

        #     raise e
        # finally:
        #     try:
        #         queue.close()
        #         connection.close()
        #     except Exception as e:
        #         logger.exception('Failed to clean up broker connection')


    # def flush(self):
    #     logger.info('Flushing %d messages', len(self.messages))

    #     ESIndexer(self.client, self.index, *self.messages).index(critical=self.connection_errors)

    #     self.messages.clear()
    #     self.last_flush = time.time()

    #     logger.debug('Successfully flushed messages')

    # def _run(self, queue):
    #     self._running.set()
    #     self.last_flush = time.time()

    #     while self._running.is_set():
    #         try:
    #             message = queue.get(timeout=self.timeout)
    #             self.messages.append(message)
    #         except Empty:
    #             pass

    #         if not self.messages:
    #             continue

    #         if time.time() - self.last_flush >= self.flush_interval:
    #             logger.debug('Time since last flush (%.2f sec) has exceeded flush_interval (%.2f sec) . Flushing...', time.time() - self.last_flush, self.flush_interval)
    #             self.flush()
    #         elif len(self.messages) >= self.max_size:
    #             logger.debug('Buffer has exceeded max_size. Flushing...')
    #             self.flush()

    #     logger.info('Exiting...')
