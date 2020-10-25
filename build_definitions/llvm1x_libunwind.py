# Copyright (c) Yugabyte, Inc.
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
import subprocess
import shutil

from yugabyte_db_thirdparty.build_definition_helpers import *  # noqa
from build_definitions.llvm1x_part import Llvm10PartDependencyBase


class Llvm10LibUnwindDependency(Llvm10PartDependencyBase):
    def __init__(self, version: str) -> None:
        super(Llvm10LibUnwindDependency, self).__init__(
            name='llvm1x_libunwind',
            version=version,
            build_group=BUILD_GROUP_COMMON)

    def build(self, builder: BuilderInterface) -> None:
        src_subdir_name = 'libunwind'
        builder.build_with_cmake(
            self,
            extra_args=[
                '-DCMAKE_BUILD_TYPE=Release',
                '-DBUILD_SHARED_LIBS=ON',
                '-DLIBUNWIND_USE_COMPILER_RT=ON',
                '-DLLVM_PATH=%s' % builder.get_source_path(self),
            ],
            src_subdir_name=src_subdir_name)
        src_include_path = os.path.join(builder.get_source_path(self), src_subdir_name, 'include')
        dest_include_path = os.path.join(builder.prefix, 'include')
        for header_name in ['libunwind.h', 'unwind.h', '__libunwind_config.h']:
            copy_file_and_log(
                os.path.join(src_include_path, header_name),
                os.path.join(dest_include_path, header_name))
