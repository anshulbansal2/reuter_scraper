from itertools import islice


def get_chunks(iterable, n):
    '''
    Iterates over an iterable in batches of n
    '''
    iterable = iter(iterable)
    while True:
        x = list(islice(iterable, n))
        if not x:
            return
        yield x
