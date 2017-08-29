# Copyright (c) 2016 Fiberhome
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

from oslo_log import log as logging

from nova.scheduler import filters

LOG = logging.getLogger(__name__)


class HostAggregateFilter(filters.BaseHostFilter):
    """Filters Hosts by host aggregate.

    Only the resource scheduler policy will pass the rs_aggregate_id in
    filter properties, this request  will only select host in the aggregate.
    """

    run_filter_once_per_request = True

    def host_passes(self, host_state, spec_obj):
        aggregate_id = spec_obj.rs_aggregate_id

        if not aggregate_id:
            return True

        agg_ids = [x.id for x in host_state.aggregates]
        if aggregate_id in agg_ids:
            LOG.debug("%(host)s in %(aggregate)s."
                       % {'host': host_state.host,
                          'aggregate': aggregate_id})
            return True
        else:
            LOG.debug("%(host)s does not in %(aggregate)s."
                       % {'host': host_state.host,
                          'aggregate': aggregate_id})
            return False
