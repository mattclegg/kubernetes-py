#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.md', which is part of this source code package.
#


from kubernetes.K8sObject import K8sObject
from kubernetes.models.v1.Namespace import Namespace

from kubernetes.models.v1.BaseUrls import BaseUrls
from kubernetes.models.v1.Deployment import Deployment, API_VERSION as Deployment_API_VERSION


class K8sNamespace(K8sObject):

    def __init__(self, config=None, name=None):

        if name is None:
            name = 'default'

        super(K8sNamespace, self).__init__(
            config=config, name=name, obj_type='Namespace')

        self.model = Namespace()


    def get_deployments(self, namespace):

        state = self.request(method='GET', url=BaseUrls(
            api_version=Deployment_API_VERSION,
            namespace=namespace
        ).get_base_url(object_type='Deployment'))

        return state.get('data', dict()).get('items', list())
