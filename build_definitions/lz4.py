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


class LZ4Dependency(Dependency):
    def __init__(self) -> None:
        super(LZ4Dependency, self).__init__(
            name='lz4',
            version='r130',
            url_pattern='https://github.com/lz4/lz4/archive/{0}.tar.gz',
            build_group=BUILD_GROUP_COMMON)
        self.copy_sources = False
        self.patch_version = 1
        self.patch_strip = 1
        self.patches = ['lz4-0001-Fix-cmake-build-to-use-gnu-flags-on-clang.patch']

    def build(self, builder: BuilderInterface) -> None:
        builder.build_with_cmake(
            self,
            ['-DCMAKE_BUILD_TYPE=release',
             '-DBUILD_TOOLS=0',
             '-DCMAKE_INSTALL_PREFIX:PATH={}'.format(builder.prefix)],
            src_subdir_name='cmake_unofficial')
