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


class LibUnwindDependency(Dependency):
    def __init__(self) -> None:
        super(LibUnwindDependency, self).__init__(
            name='libunwind',
            version='1.1a',
            url_pattern=None,
            build_group=BUILD_GROUP_COMMON)
        self.copy_sources = True

    def build(self, builder: BuilderInterface) -> None:
        # Disable minidebuginfo, which depends on liblzma, until/unless we decide to
        # add liblzma to thirdparty.
        log_prefix = builder.log_prefix(self)
        builder.build_with_configure(
            log_prefix=log_prefix,
            extra_args=['--with-pic', '--disable-minidebuginfo']
        )
