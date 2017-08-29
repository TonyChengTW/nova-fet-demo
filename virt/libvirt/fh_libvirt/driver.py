# Copyright 2016 fiberhome.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging
from oslo_utils import strutils

from nova.compute import task_states
from nova import exception
from nova.virt.libvirt import driver as libvirt_driver
from nova.virt.libvirt import utils as libvirt_utils

LOG = logging.getLogger(__name__)


class FHLibvirtDriver(libvirt_driver.LibvirtDriver):
    def __init__(self, virtapi, read_only=False):
        super(FHLibvirtDriver, self).__init__(virtapi, read_only)

    def _try_fetch_image_cache(self, image, fetch_func, context, filename,
                               image_id, instance, size,
                               fallback_from_host=None):
        flattenStr = instance.metadata.get('flatten')
        flatten = strutils.bool_from_string(flattenStr)

        try:
            if (instance.task_state == task_states.SPAWNING or
                  instance.task_state == task_states.REBUILD_SPAWNING)\
                  and image.SUPPORTS_CLONE:
                def fh_clone_fallback_to_fetch(*args, **kwargs):
                    try:
                        image.clone(context, image_id)
                        if kwargs['flatten'] is True:
                            image.flatten()
                    except exception.ImageUnacceptable:
                        kwargs.pop('flatten')
                        libvirt_utils.fetch_image(*args, **kwargs)
                fetch_func = fh_clone_fallback_to_fetch

                image.cache(fetch_func=fetch_func,
                            context=context,
                            filename=filename,
                            image_id=image_id,
                            size=size,
                            flatten=flatten)
            else:
                image.cache(fetch_func=fetch_func,
                            context=context,
                            filename=filename,
                            image_id=image_id,
                            size=size)
        except exception.ImageNotFound:
            if not fallback_from_host:
                raise
            LOG.debug("Image %(image_id)s doesn't exist anymore "
                      "on image service, attempting to copy "
                      "image from %(host)s",
                      {'image_id': image_id, 'host': fallback_from_host},
                      instance=instance)

            def copy_from_host(target, max_size):
                libvirt_utils.copy_image(src=target,
                                         dest=target,
                                         host=fallback_from_host,
                                         receive=True)
            image.cache(fetch_func=copy_from_host,
                        filename=filename)
