import logging
from typing import Tuple
from typing import Union
from typing import Iterator

import pendulum
from furl import furl
# from django.conf import settings

from providers.io.osf.harvester import OSFHarvester

logger = logging.getLogger(__name__)


class PsyarxivHarvester(OSFHarvester):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # temporary harvest URL until preprint branding is complete
        # self.url = '{}v2/preprint_providers/psyarxiv/preprints/'.format(settings.OSF_API_URL)

    def do_harvest(self, start_date: pendulum.Pendulum, end_date: pendulum.Pendulum) -> Iterator[Tuple[str, Union[str, dict, bytes]]]:

        url = furl(self.url)

        url.args['page[size]'] = 100
        url.args['filter[tags]'] = 'psyarxiv'  # temporary - remove with proper preprint harvest
        url.args['embed'] = 'affiliated_institutions'  # temporary - remove with proper preprint harvest
        url.args['filter[date_modified][gt]'] = start_date.date().isoformat()
        url.args['filter[date_modified][lt]'] = end_date.date().isoformat()

        return self.fetch_records(url)
