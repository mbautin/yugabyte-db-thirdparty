#
# Copyright (c) YugaByte, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations
# under the License.
#

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_definitions import *

class ProtobufDependency(Dependency):
    def __init__(self):
        super(ProtobufDependency, self).__init__(
                'protobuf', '3.5.1',
                'https://github.com/google/protobuf/releases/download/v{0}/protobuf-cpp-{0}.tar.gz',
                BUILD_GROUP_INSTRUMENTED)
        self.copy_sources = True
        # Based on
        # https://github.com/acozzette/protobuf/commit/61f5dca4711bb03bcef1ed8d9c62debcdb033af2
        # TODO: just upgrade protobuf.
        self.patches = ['protobuf-remove_check_for_sched_yield.patch']
        self.patch_strip = 1

    def build(self, builder):
        log_prefix = builder.log_prefix(self)
        builder.build_with_configure(
                log_prefix,
                ['--with-pic', '--enable-shared', '--enable-static'],
                autoconf=True)
