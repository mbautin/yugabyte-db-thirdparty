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
from build_definitions.llvm10_part import Llvm10PartDependencyBase


class Llvm10CompilerRtDependency(Llvm10PartDependencyBase):
    def __init__(self) -> None:
        super(Llvm10CompilerRtDependency, self).__init__(
            name='llvm10_compiler_rt',
            build_group=BUILD_GROUP_INSTRUMENTED)

    def build(self, builder: BuilderInterface) -> None:
        src_subdir_name = 'compiler-rt'
        builder.build_with_cmake(
            self,
            extra_args=[
                f'-DLLVM_CONFIG_PATH={builder.get_llvm_config_path()}',
                '-DCMAKE_BUILD_TYPE=Release',
                '-DBUILD_SHARED_LIBS=ON',
                '-DLLVM_PATH=%s' % builder.get_source_path(self),
                '-DCMAKE_INSTALL_PREFIX={}'.format(builder.prefix),
                '-DCOMPILER_RT_BUILD_SANITIZERS=ON',
                '-DCOMPILER_RT_BUILD_XRAY=OFF',
                '-DCOMPILER_RT_USE_LIBCXX=ON',
                '-DSANITIZER_CXX_ABI=libc++',
                # All sanitizers except hwasan (which does not compile for some libunwind-related reasons).
                '-DCOMPILER_RT_SANITIZERS_TO_BUILD=asan;dfsan;msan;tsan;safestack;cfi;scudo;ubsan_minimal;gwp_asan'
            ],
            src_subdir_name=src_subdir_name)

    def get_install_prefix(self, builder: BuilderInterface) -> str:
        return os.path.join(builder.prefix, 'compiler-rt')
