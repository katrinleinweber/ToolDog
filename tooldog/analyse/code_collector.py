#!/usr/bin/env python3

import logging
import os
import urllib.parse
import urllib.request
import tarfile

from .utils import *

LOGGER = logging.getLogger(__name__)

class CodeCollector(object):
    """
    Class to download source code from a https://bio.tools entry 
    """

    ZIP_NAME = "tool.zip"
    TAR_NAME = "tool.tar"
    TMP_NAME = "tmp"

    def __init__(self, biotool):
        """
        :param biotool: Biotool object
        :type biotool: :class:`tooldog.biotool_model.Biotool`
        """
        self.biotool = biotool

    def _make_tar(self, file_path, tarname):
        with tarfile.open(tarname, mode='w') as archive:
            archive.add(file_path, arcname=self.ZIP_NAME)

    def _get_from_repository(self, url):
        """
        Get source code from a repository link

        :param url: url of the repository
        :type url: STRING
        """
        # Here we deal with repository, have to use regex to test the url and
        # use appropriate strategy to get the code depending the type of repository
        if "github.com" in url.url:
            return self._get_from_github(url.url)
        else:
            LOGGER.warn(url + ' points to unknown repo.')
            raise Exception('Unknown repo type.')

    def _get_from_github(self, url):
        print(url)
        try:
            zip_url = os.path.join(url, "archive/master.zip")
            print(zip_url)
            response = urllib.request.urlopen(zip_url)
            data = response.read()

            LOGGER.info('Writing data to zip file...')
            current_path = os.path.realpath(os.getcwd())
            zip_path = os.path.join(current_path, self.TMP_NAME, self.ZIP_NAME)
            tar_path = os.path.join(current_path, self.TMP_NAME, self.TAR_NAME)

            write_to_file(zip_path, data, 'wb')

            LOGGER.info('Making tar...')
            self._make_tar(zip_path, tar_path)

            return "zip", tar_path
        except:
            LOGGER.warn(url + ' points to unknown repo.')
            raise Exception('Unknown repo type.')

    def _get_from_source_code(self, url):
        """
        Get source code from a source code link

        :param url: url of the source code
        :type url: STRING
        """
        return None

    def get_source(self):
        """
        Retrieve source code of the tool using links provided in https://bio.tools
        """
        links = self.biotool.informations.links
        for link in links:
            link_type = link.type.lower().translate(str.maketrans(' ','_'))
            try:
                source_code = getattr(self, '_get_from_{}'.format(link_type))(link)
            except AttributeError:
                LOGGER.warn(link_type + ' link type is not processed yet by ToolDog.')
            if source_code is not None:
                # For the moment, consider that if a source code has been found,
                # we just leave the loop.
                break
        return source_code
