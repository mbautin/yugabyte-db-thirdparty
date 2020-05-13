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
from build_definitions.llvm import LLVMDependency


class LibCXXDependency(Dependency):
    def __init__(self):
        super(LibCXXDependency, self).__init__(
                'libcxx',
                LLVMDependency.VERSION,
                LLVMDependency.URL_PATTERN,
                BUILD_GROUP_INSTRUMENTED)

        self.copy_sources = False

    def build(self, builder):
        log_prefix = builder.log_prefix(self)
        prefix = os.path.join(builder.prefix, 'libcxx')

        remove_path('CMakeCache.txt')
        remove_path('CMakeFiles')

        llvm_src_path = os.path.join(builder.tp_src_dir, 'llvm-%s' % LLVMDependency.VERSION)

        common_cmake_args = [
            '-DLLVM_PATH=%s' % llvm_src_path,
            '-DCMAKE_CXX_FLAGS={}'.format(" ".join(builder.ld_flags)),
            '-DCMAKE_INSTALL_PREFIX={}'.format(prefix),
        ]

        if builder.build_type == BUILD_TYPE_ASAN:
            common_cmake_args.append("-DLLVM_USE_SANITIZER=Address;Undefined")

        if builder.build_type == BUILD_TYPE_TSAN:
            common_cmake_args.append("-DLLVM_USE_SANITIZER=Thread")

        libcxxabi_libcxx_includes = os.path.join(llvm_src_path, 'libcxx', 'include')
        libcxxabi_cmake_args = common_cmake_args + [
            '-DLIBCXXABI_LIBCXX_INCLUDES=%s' % libcxxabi_libcxx_includes
        ]
        builder.build_with_cmake(
                self, libcxxabi_cmake_args, use_ninja='auto', src_dir='libcxxabi',
                install=['install-libcxxabi'])

        # As per https://libcxx.llvm.org/docs/BuildingLibcxx.html
        libcxx_cxx_abi_include_paths = os.path.join(llvm_src_path, 'libcxxabi', 'include')
        libcxx_cmake_args = common_cmake_args + [
            '-DLIBCXX_CXX_ABI=libcxxabi',
            '-DLIBCXX_CXX_ABI_INCLUDE_PATHS=%s' % libcxx_cxx_abi_include_paths
        ]
        builder.build_with_cmake(
                self, libcxx_cmake_args, use_ninja='auto', src_dir='libcxx',
                install=['install-libcxx'])

    def should_build(self, builder):
        return builder.building_with_clang()
