#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/apache2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#
from .model import Model, NamedArgument


class S2ND(Model):
    binary = "../../bin/s2nd"
    host = None
    port = None

    cert_path = NamedArgument(argument="--cert")
    key_path = NamedArgument(argument="--key")
    ocsp_path = NamedArgument(argument="--ocsp")
    ciphers = NamedArgument(argument="--ciphers", default="test_all")

    enter_fips_mode = NamedArgument(argument="--enter-fips-mode", flag=True)
    mutual_auth = NamedArgument(argument="--mutualAuth", flag=True)
    prefer_low_latency = NamedArgument(argument="--prefer-low-latency",
                                       flag=True)
    no_session_tickets = NamedArgument(argument="--no-session-ticket",
                                       flag=True)

    def __init__(self, host, port):
        super(S2ND, self).__init__()

        self.host = host
        self.port = port

    def get_run_cmd(self):
        return super(S2ND, self).get_run_cmd(self.host, self.port)
