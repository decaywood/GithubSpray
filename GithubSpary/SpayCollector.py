import time
from datetime import timedelta
from bs4 import BeautifulSoup
from tornado import httpclient, gen, ioloop, queues

baseURL = 'https://github.com'
rootURL = '/decaywood'
concurrency = 10


@gen.coroutine
def get_soup(url):
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(url)

        html = response.body if isinstance(response.body, str) else response.body.decode()
        soup = BeautifulSoup(html)

    except Exception as e:

        print('Exception: %s %s' % (e, url))
        raise gen.Return(BeautifulSoup())

    raise gen.Return(soup)


# fetch followers from a root user
@gen.coroutine
def get_followers_url(url):
    url += '/followers'
    soup = yield get_soup(url)
    urls = [follower.select('.follow-list-name a')[0]['href'] for follower in soup.select('.follow-list-item')]
    raise gen.Return(urls)


@gen.coroutine
def get_email(url):
    soup = yield get_soup(url)
    res = soup.select('.email')
    email = res[0].get_text() if len(res) > 0 else None
    raise gen.Return(email)

@gen.coroutine
def main():
    q = queues.Queue()
    start = time.time()
    fetching, fetched = set(), set()

    @gen.coroutine
    def fetch_url():

        suffix = yield q.get()
        current_url = baseURL + suffix

        try:
            if current_url not in fetching:

                fetching.add(current_url)
                email = yield get_email(current_url)
                urls = yield get_followers_url(current_url)
                print str(email) + '   ' + str(q.qsize())
                fetched.add(current_url)

                for new_url in urls:
                    if new_url not in fetched:
                        yield q.put(new_url)

        finally:
            q.task_done()

    @gen.coroutine
    def worker():
        while True:
            yield fetch_url()

    q.put(rootURL)

    print 'start working...'

    # Start workers, then wait for the work queue to be empty.
    for _ in range(concurrency):
        worker()
    yield q.join(timeout=timedelta(seconds=200))
    assert fetching == fetched
    print('Done in %d seconds, fetched %s URLs.' % (
        time.time() - start, len(fetched)))


if __name__ == '__main__':
    import logging

    logging.basicConfig()
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)
