# Copyright 2016 Fiberhome
# All Rights Reserved.
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

"""
Memory monitor based on compute driver to retrieve memory used
information of the host
"""

from oslo_utils import timeutils
from oslo_utils import units

from nova.compute.monitors import base
import nova.conf
from nova import objects
from nova.objects import fields

CONF = nova.conf.CONF


class ComputeDriverMemoryMonitor(base.MonitorBase):
    """Memory monitor based on compute driver

    The class inherits from the base class for resource monitors,
    and implements the essential methods to get metric names and their real
    values for Memory utilization.

    The compute manager could load the monitors to retrieve the metrics
    of the devices on compute nodes and know their resource information
    periodically.
    """

    def __init__(self, compute_manager):
        super(ComputeDriverMemoryMonitor, self).__init__(compute_manager)
        self.source = CONF.compute_driver
        self._data = {}

    def get_metric_names(self):
        return set([
            fields.MonitorMetricType.MEMORY_USED,
        ])

    def populate_metrics(self, metric_list):
        self._update_data()
        for name in self.get_metric_names():
            metric_object = objects.MonitorMetric()
            metric_object.name = name
            metric_object.value = self._data[name]
            metric_object.timestamp = self._data["timestamp"]
            metric_object.source = self.source
            metric_list.objects.append(metric_object)

    def _update_data(self):
        self._data = {}
        self._data["timestamp"] = timeutils.utcnow()
        self._data["memory.used"] = self._get_memory_used()

    def _get_memory_used(self):
        with open('/proc/meminfo') as fp:
            m = fp.read().split()
        idx0 = m.index('MemTotal:')
        idx1 = m.index('MemFree:')
        idx2 = m.index('Buffers:')
        idx3 = m.index('Cached:')
        avail = (int(m[idx1 + 1]) + int(m[idx2 + 1]) + int(m[idx3 + 1]))
        total = int(m[idx0 + 1])
        return (total - avail) / units.Ki
