import time
from datetime import timedelta
from bs4 import BeautifulSoup
from tornado import httpclient, gen, ioloop, queues

rootURL = ''
concurrency = 1

# fetch followers from a root user
@gen.coroutine
def get_links_from_url(url):
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(url)
        print('fetched -> ' + url)
        html = response.body if isinstance(response.body, str) else response.body.decode()
        soup = BeautifulSoup(html)
        urls = [follower.select('.follow-list-name a')[0]['href'] for follower in soup.select('.follow-list-item')]
    except Exception as e:
        print('Exception: %s %s' % (e, url))
        raise gen.Return([])
    raise gen.Return(urls)


@gen.coroutine
def main():
    q = queues.Queue()
    start = time.time()
    fetching, fetched = set(), set()

    @gen.coroutine
    def fetch_url():
        current_url = yield q.get()
        try:
            if current_url in fetching:
                return

            print('fetching %s' % current_url)
            fetching.add(current_url)
            urls = yield get_links_from_url(current_url)
            fetched.add(current_url)

            for new_url in urls:
                # Only follow links beneath the base URL
                yield q.put(new_url)

        finally:
            q.task_done()

    @gen.coroutine
    def worker():
        while True:
            yield fetch_url()

    q.put(rootURL)

    # Start workers, then wait for the work queue to be empty.
    for _ in range(concurrency):
        worker()
    yield q.join(timeout=timedelta(seconds=300))
    assert fetching == fetched
    print('Done in %d seconds, fetched %s URLs.' % (
        time.time() - start, len(fetched)))

if __name__ == '__main__':
    import logging
    logging.basicConfig()
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)