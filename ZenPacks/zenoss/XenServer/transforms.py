##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from ZenPacks.zenoss.XenServer.utils import BaseComponent


def get_component_id(dmd, xenapi_uuid):
    '''
    Return the Zenoss component ID for a XenServer component given its
    XenAPI UUID.

    Returns the given xenapi_uuid if no XenServer component can be found.
    '''
    component = BaseComponent.findByUUID(dmd, xenapi_uuid)
    if component:
        return component.id

    return xenapi_uuid
