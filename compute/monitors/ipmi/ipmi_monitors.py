# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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
BMC info monitor to retrieve BMC information of this host
"""
from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_utils import timeutils

from nova.compute.monitors import base
import nova.conf
from nova import objects
from nova.objects import fields

LOG = logging.getLogger(__name__)
CONF = nova.conf.CONF


class IPMIMonitor(base.MonitorBase):
    """IPMI monitor."""

    def __init__(self, compute_manager):
        super(IPMIMonitor, self).__init__(compute_manager)
        self.bmc_json = {}
        self.source = CONF.compute_driver
        self._data = {}

    def get_metric_names(self):
        return set([
            fields.MonitorMetricType.IPMI_BMC,
            fields.MonitorMetricType.IPMI_USER,
            fields.MonitorMetricType.IPMI_PASSWORD,
        ])

    def populate_metrics(self, metric_list):
        self._update_data()
        for name in self.get_metric_names():
            metric_object = objects.StringMonitorMetric()
            metric_object.name = name
            metric_object.value = self._data[name]
            metric_object.timestamp = self._data["timestamp"]
            metric_object.source = self.source
            metric_list.objects.append(metric_object)

    def _get_bmc(self, **kwargs):
        """Return bmc of this host."""
        return self.bmc_json.get('bmc', '')

    def _get_user(self, **kwargs):
        """Return bmc user of this host."""
        return self.bmc_json.get('user', '')

    def _get_password(self, **kwargs):
        """Return bmc password of this host."""
        return self.bmc_json.get('password', '')

    def _update_data(self):
        try:
            with open('/etc/nova/bmc.json', 'r') as json_file:
                self.bmc_json = jsonutils.load(json_file)

        except Exception as ex:
            LOG.warning('Read bmc info error:%s', ex)
        self._data = {}
        self._data["timestamp"] = timeutils.utcnow()
        self._data["bmc"] = self._get_bmc()
        self._data["user"] = self._get_user()
        self._data["password"] = self._get_password()
