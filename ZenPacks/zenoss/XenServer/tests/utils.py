##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


def add_contained(obj, relname, target):
    '''
    Add and return obj to containing relname on target.
    '''
    rel = getattr(obj, relname)
    rel._setObject(target.id, target)
    return rel._getOb(target.id)


def add_noncontained(obj, relname, target):
    '''
    Add obj to non-containing relname on target.
    '''
    rel = getattr(obj, relname)
    rel.addRelation(target)
