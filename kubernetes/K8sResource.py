#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.md', which is part of this source code package.
#

from kubernetes.utils import HttpRequest
from kubernetes.models.v1.BaseUrls import BaseUrls
from kubernetes.models.v1.BaseModel import BaseModel
from kubernetes.models.v1.DeleteOptions import DeleteOptions
from kubernetes.K8sConfig import K8sConfig
from kubernetes.K8sExceptions import *
import json

VALID_K8s_RESCOURCES = [
    'Node'
]


class K8sResource(object):

    def __init__(self, config=None, name=None, obj_type=None):
        super(K8sResource, self).__init__()

        if config is not None and not isinstance(config, K8sConfig):
            raise SyntaxError('K8sObject: config: [ {0} ] must be of type K8sConfig.'.format(config.__class__.__name__))
        if config is None:
            config = K8sConfig()
        self.config = config

        if name is None:
            raise SyntaxError('K8sObject: name: [ {0} ] cannot be None.'.format(name))
        if not isinstance(name, str):
            raise SyntaxError('K8sObject: name: [ {0} ] must be a string.'.format(name.__class__.__name__))

        if obj_type is None or not isinstance(obj_type, str):
            raise SyntaxError('K8sObject: obj_type: [ {0} ] must be a string.'.format(obj_type.__class__.__name__))

        if obj_type not in VALID_K8s_RESCOURCES:
            valid = ", ".join(VALID_K8s_RESCOURCES)
            raise SyntaxError('K8sObject: obj_type: [ {0} ] must be in: [ {1} ]'.format(obj_type, valid))

        self.obj_type = obj_type
        self.name = name
        self.model = BaseModel()

        try:
            urls = BaseUrls(api_version=self.config.version, namespace=self.config.namespace)
            self.base_url = urls.get_base_url(object_type=obj_type)
        except:
            raise Exception('Could not set BaseUrl for type: [ {0} ]'.format(obj_type))

    def __str__(self):
        return "[ {0} ] named [ {1} ]. Model: [ {2} ]".format(self.obj_type, self.name, self.model.get())

    def __eq__(self, other):
        # see https://github.com/kubernetes/kubernetes/blob/release-1.3/docs/design/identifiers.md
        if isinstance(other, self.__class__):
            # Uniquely name (via a name) an object across space.
            return self.config.namespace == other.config.namespace \
                   and self.name == other.name
        return NotImplemented

    # ------------------------------------------------------------------------------------- representations

    def as_dict(self):
        return self.model.get()

    def as_json(self):
        return json.dumps(self.model.get())

    # ------------------------------------------------------------------------------------- remote API calls

    def request(self, method='GET', host=None, url=None, auth=None, cert=None,
                data=None, token=None, ca_cert=None, ca_cert_data=None):

        host = self.config.api_host if host is None else host
        url = self.base_url if url is None else url
        auth = self.config.auth if auth is None else auth
        cert = self.config.cert if cert is None else cert
        token = self.config.token if token is None else token
        ca_cert = self.config.ca_cert if ca_cert is None else ca_cert
        ca_cert_data = self.config.ca_cert_data if ca_cert_data is None else ca_cert_data

        r = HttpRequest(
            method=method,
            host=host,
            url=url,
            auth=auth,
            cert=cert,
            ca_cert=ca_cert,
            ca_cert_data=ca_cert_data,
            data=data,
            token=token
        )

        try:
            return r.send()
        except IOError as err:
            raise BadRequestException('K8sObject: IOError: {0}'.format(err))

    def list(self):
        state = self.request(method='GET')
        if not state.get('status'):
            raise Exception('K8sObject: Could not fetch list of objects of type: [ {0} ]'.format(self.obj_type))
        return state.get('data', dict()).get('items', list())

    def get_model(self):
        if self.name is None:
            raise SyntaxError('K8sObject: name: [ {0} ] must be set to fetch the object.'.format(self.name))

        url = '{base}/{name}'.format(base=self.base_url, name=self.name)
        state = self.request(method='GET', url=url)

        if not state.get('success'):
            status = state.get('status', '')
            reason = state.get('data', dict()).get('message', None)
            message = 'K8sObject: GET [ {0}:{1} ] failed: HTTP {2} : {3} '.format(self.obj_type, self.name, status, reason)
            raise NotFoundException(message)

        model = state.get('data')
        return model
