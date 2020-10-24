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

from yugabyte_db_thirdparty.build_definition_helpers import *  # noqa


class ProtobufDependency(Dependency):
    def __init__(self) -> None:
        super(ProtobufDependency, self).__init__(
            'protobuf', '3.5.1',
            'https://github.com/google/protobuf/releases/download/v{0}/protobuf-cpp-{0}.tar.gz',
            BUILD_GROUP_INSTRUMENTED)
        self.copy_sources = True

    def build(self, builder: BuilderInterface) -> None:
        log_prefix = builder.log_prefix(self)
        builder.build_with_configure(
            log_prefix=log_prefix,
            extra_args=['--with-pic', '--enable-shared', '--enable-static'],
            run_autogen=True
        )
