
def batches(iterable, n=10):
    """divide a single list into a list of lists of size n """
    batchLen = len(iterable)
    for ndx in range(0, batchLen, n):
        yield list(iterable[ndx:min(ndx + n, batchLen)])


class SocialStatements:

    def __init__(self, logger, engine=None):
        self.users = []
        self.engine = engine
        self.logger = logger
        self.relations = []

    user_schema = {
        "table_name": "user",
        "options": {
            "primary_key": ["name"]
        },
        "columns": {
            "name": "text",
            "uploads": "int",
            "subscribers": "int",
            "video_views": "bigint",
            "country": "text",
            "channel_type": "text",
            "user_created": "date",
            "total_grade": "text",
            "subscriber_rank": "int",
            "video_view_rank": "int",
            "socialblade_rank": "int",
            "views_for_he_last_30_days": "int",
            "subscribers_for_he_last_30_days": "int",
            "estimated_monthly_earnings": "text",
            "estimated_yearly_earnings": "text",
            "youtube_url": "text",
            "facebook_url": "text",
            "twitter_url": "text",
            "instagram_url": "text",
            "google_plus_url": "text",
            "date": "date"
        }
    }

    def save(self, batch_size=50, users=None, relations=None):
        """Write these social statements to the data engine in the appropriate manner."""
        self.users = users
        self.relations = relations
        if self.users:
            self.logger.info('about to send {} user statements to the data engine'.format(len(self.users)))
            self._write_batches(self.engine, self.logger, self.user_schema, self.users, batch_size)
        else:
            self.logger.debug('skipping user ingest, no records in these social statements')

    @staticmethod
    def _write_batches(engine, logger, schema, data, batch_size=40):
        for rows in batches(data, batch_size):
            logger.info('Rows: {}'.format(rows))
            res = engine.save(schema, list(rows)).result()
            logger.info(res)
