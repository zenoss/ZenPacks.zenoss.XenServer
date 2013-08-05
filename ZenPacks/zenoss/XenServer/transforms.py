##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from ZenPacks.zenoss.XenServer.utils import findComponentByUUID


def get_component_id(dmd, xapi_uuid):
    '''
    Return the Zenoss component ID for a XenServer component given its
    XAPI ref.

    Returns the given xapi_uuid if no XenServer component can be found.
    '''
    component = findComponentByUUID(dmd, xapi_uuid)
    if component:
        return component.id

    return xapi_uuid
