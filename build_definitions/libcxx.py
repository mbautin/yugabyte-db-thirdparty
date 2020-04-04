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
import multiprocessing
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_definitions import *
import build_definitions.llvm

class LibCXXDependency(Dependency):
    def __init__(self):
        LLVMDependency = build_definitions.llvm.LLVMDependency
        super(LibCXXDependency, self).__init__(
                'libcxx',
                LLVMDependency.VERSION,
                LLVMDependency.URL_PATTERN,
                BUILD_GROUP_INSTRUMENTED)

        url_prefix = "http://releases.llvm.org/{0}/"
        self.copy_sources = False

    def build(self, builder):
        log_prefix = builder.log_prefix(self)
        prefix = os.path.join(builder.prefix, 'libcxx')

        remove_path('CMakeCache.txt')
        remove_path('CMakeFiles')

        args = [
            'cmake',
            os.path.join(builder.source_path(self), 'llvm'),
            '-DCMAKE_BUILD_TYPE=Release',
            '-DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra"',
            '-DLLVM_TARGETS_TO_BUILD=X86',
            '-DLLVM_ENABLE_RTTI=ON',
            '-DLLVM_ENABLE_PROJECTS="libcxx;libcxxabi',
            '-DCMAKE_CXX_FLAGS={}'.format(" ".join(builder.ld_flags)),
            '-DCMAKE_INSTALL_PREFIX={}'.format(prefix)
        ]
        if builder.build_type == BUILD_TYPE_ASAN:
            args.append("-DLLVM_USE_SANITIZER=Address;Undefined")
        elif builder.build_type == BUILD_TYPE_TSAN:
            args.append("-DLLVM_USE_SANITIZER=Thread")
        builder.build_with_cmake(
                self, args, use_ninja='auto', src_dir='libcxx',
                install=['install-cxxabi', 'install-libcxx'])

    def should_build(self, builder):
        return builder.building_with_clang()
