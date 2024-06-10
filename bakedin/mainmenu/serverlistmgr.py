import json
import os
import platform
import sys

from logging import getLogger

if sys.version_info.major >= 3:
    # from urllib import request
    # urlretrieve = request.urlretrieve
    from urllib.request import urlopen
else:
    # from urllib import request  # noqa: F401  # type:ignore
    # urlretrieve = urllib.urlretrieve  # not in urllib2
    from urllib2 import urlopen

from voxboxor import mydirs

logger = getLogger(__name__)


class ServerListMgr:
    def __init__(self):
        self.servers = []
        self._domain = None
        self.downloaded_cb = None
        self._busy = False

    def set_masterserver_domain(self, domain):
        self._domain = domain
        url = self.get_url()
        path = self._list_path(url)
        if os.path.isfile(path):
            self._load_list(path)
        else:
            logger.warning("There is no cached {} for url {}"
                           .format(path, url))

    def get_url(self):
        url = self._domain
        if not url.lower().startswith("http"):
            if not url.lower().startswith("servers."):
                logger.warning("Prepending servers. automatically.")
                url = "servers." + url
            if "/" not in url:
                logger.warning("Appending list.json automatially.")
                url += "/list.json"
            url = "https://" + url
        return url

    def get_domain(self, url):
        domain = url.lower().replace("http://", "")
        domain = url.replace("https://", "")
        if domain.startswith("servers."):
            domain = domain[8:]
        slashI = domain.find("/")
        if slashI >= 0:
            domain = domain[:slashI]
        return domain

    def _list_path(self, url):
        name = self.get_domain(url) + ".json"
        return os.path.join(self._server_lists_dir(), name)

    def _server_lists_dir(self):
        return os.path.join(mydirs['cache'], "servers")

    def _clear_cache_file(self):
        if self._busy:
            return False
        path = self._list_path(self.get_url())
        if os.path.isfile(path):
            os.remove(path)
        return True

    def sync(self, refresh=True):
        if self._busy:
            return False
        if refresh:
            self._clear_cache_file()
        self._busy = True
        if not os.path.isdir(self._server_lists_dir()):
            os.makedirs(self._server_lists_dir())
        url = self.get_url()
        logger.warning("Checking {}".format(url))
        path = self._list_path(self._domain)
        used_cache = True
        if not os.path.isfile(path):
            used_cache = False
            response = urlopen(url)
            data_bytes = response.read()
            logger.warning("Finished reading response from server.")
            with open(path, "wb") as outs:
                outs.write(data_bytes)
        else:
            logger.warning("Using cached {}".format(path))
        self._load_list(path, used_cache=used_cache)
        return True

    def _load_list(self, path, used_cache=True):
        with open(path, 'r') as ins:
            self.data = json.load(ins)
        self.servers = self.data['list']
        if self.downloaded_cb:
            self.downloaded_cb({
                'status': "done",
                'used_cache': used_cache,
            })


serverlistmgr = ServerListMgr()
