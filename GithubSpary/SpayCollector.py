import time
from datetime import timedelta
from bs4 import BeautifulSoup
from tornado import httpclient, gen, ioloop, queues
from GithubSpary import DBAccessor

baseURL = 'https://github.com'
rootURL = '/es'
concurrency = 10
queueSize = 10000


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


# fetch current user's followers from a root user
@gen.coroutine
def get_followers_url(url):
    url += '/followers'
    soup = yield get_soup(url)
    urls = [follower.select('.follow-list-name a')[0]['href'] for follower in soup.select('.follow-list-item')]
    raise gen.Return(urls)


def get_text(element):
    return element[0].get_text() if len(element) > 0 else None

# fetch current user's email
@gen.coroutine
def get_info(url):
    soup = yield get_soup(url)
    res_full_name = soup.select('[itemprop=name]')
    res_email = soup.select('.email')
    res_location = soup.select('[itemprop=homeLocation]')
    full_name = get_text(res_full_name)
    if full_name is None:
        res_full_name = soup.select('[itemprop=additionalName]')
        full_name = get_text(res_full_name)
    email = get_text(res_email)
    location = get_text(res_location)
    raise gen.Return((full_name, email, location))


@gen.coroutine
def main():
    q = queues.Queue()
    start = time.time()
    fetched = DBAccessor.get_all_user_path()

    @gen.coroutine
    def fetch_url():

        suffix = yield q.get()
        current_url = baseURL + suffix

        try:
            if suffix not in fetched:

                user = suffix[1::]
                full_name, email, location = yield get_info(current_url)

                print user, email, location, len(fetched), q.qsize()
                DBAccessor.insert_info(user, full_name, email, location)

                urls = yield get_followers_url(current_url)
                fetched.add(current_url)

                for new_url in urls:
                    if new_url not in fetched and q.qsize() < queueSize:
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
    yield q.join(timeout=timedelta(seconds=2000))
    print('Done in %d seconds, fetched %s URLs.' % (
        time.time() - start, len(fetched)))


if __name__ == '__main__':
    import logging
    logging.basicConfig()
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)
    DBAccessor.close_db()
