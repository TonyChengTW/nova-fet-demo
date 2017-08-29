# Copyright 2013 Intel Corporation
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

"""Tests for Compute Driver CPU resource monitor."""

import __builtin__
import mock

from oslo_serialization import jsonutils

from nova.compute.monitors.ipmi import ipmi_monitors
from nova import objects
from nova import test


class IPMIMonitorTestCase(test.NoDBTestCase):
    def test_get_metric_names(self):
        monitor = ipmi_monitors.IPMIMonitor(object())
        names = monitor.get_metric_names()
        self.assertEqual(3, len(names))
        self.assertIn("bmc", names)
        self.assertIn("user", names)
        self.assertIn("password", names)

    @mock.patch.object(__builtin__, "open", create=True)
    def test_get_metrics(self, mock_open):
        mock_open.return_value = mock.mock_open(
            read_data=jsonutils.dumps({'bmc': '11.11.11.11',
                                       'user': 'user',
                                       'password': 'password'})).return_value
        metrics = objects.SMonitorMetricList()
        monitor = ipmi_monitors.IPMIMonitor(object())
        monitor.source = 'testsource'
        monitor.populate_metrics(metrics)
        names = monitor.get_metric_names()
        for metric in metrics.objects:
            self.assertIn(metric.name, names)

        # Some conversion to a dict to ease testing...
        metrics = {m.name: m.value for m in metrics.objects}

        self.assertEqual(metrics['bmc'], '11.11.11.11')
        self.assertEqual(metrics['user'], 'user')
        self.assertEqual(metrics['password'], 'password')

        mock_open.assert_called_once_with('/etc/nova/bmc.json', 'r')
