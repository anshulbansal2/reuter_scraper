# log buckets. It's basically a label for grouping of the generated logs.
# This will help us in log categorization and quick root cause identification.
# Always use generic bucket that covers a large portion use cases.


def enum(enum_type, **named):
    enums = dict(named)
    groups = dict((v, k) for k, v in enums.items())
    enums['values'] = groups
    return type(enum_type or 'Enum', (), enums)


REAUTER_SCRAPER = enum(
    'reuter_scraper',
    master='master',
    ISIN_fetcher='ISIN_fetcher',
    ISIN_producer='ISIN_producer',
    reuter_login='reuter_login',
    recommendation_estimates='recommendation_estimates'
)




