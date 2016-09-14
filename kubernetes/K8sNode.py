#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.md', which is part of this source code package.
#


from kubernetes.K8sResource import K8sResource
from kubernetes.models.v1.Node import Node


class K8sNode(K8sResource):

    def __init__(self, config=None, name=None):

        if name is None:
            name = 'default'

        super(K8sNode, self).__init__(
            config=config, name=name, obj_type='Node')

        self.model = Node()