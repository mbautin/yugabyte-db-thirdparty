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
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_definitions import *

class LLVMDependency(Dependency):
    VERSION = '10.0.0'
    URL_PATTERN = 'https://github.com/llvm/llvm-project/archive/llvmorg-{0}.tar.gz'

    # https://github.com/llvm/llvm-project/archive/llvmorg-10.0.0.tar.gz
    def __init__(self):
        super(LLVMDependency, self).__init__(
                'llvm',
                LLVMDependency.VERSION,
                LLVMDependency.URL_PATTERN,
                BUILD_GROUP_COMMON)
        self.copy_sources = False

    def build(self, builder):
        prefix = builder.get_prefix('llvm10')

        python_executable = which('python3')
        if not os.path.exists(python_executable):
            fatal("Could not find Python -- needed to build LLVM.")

        cxx_flags = builder.compiler_flags + builder.cxx_flags + builder.ld_flags
        if '-g' in cxx_flags:
            cxx_flags.remove('-g')

        cxx_flags += ['-Wno-pedantic']
        builder.build_with_cmake(self,
                                 ['-DCMAKE_BUILD_TYPE=Release',
                                  '-DCMAKE_INSTALL_PREFIX={}'.format(prefix),
                                  '-DLLVM_ENABLE_PROJECTS=clang;clang-tools-extra;compiler-rt',
                                  '-DLLVM_INCLUDE_TESTS=OFF',
                                  '-DLLVM_TARGETS_TO_BUILD=X86',
                                  '-DLLVM_ENABLE_RTTI=ON',
                                  '-DCMAKE_CXX_FLAGS={}'.format(" ".join(cxx_flags)),
                                  '-DPYTHON_EXECUTABLE={}'.format(python_executable)
                                 ],
                                 use_ninja='auto',
                                 src_dir='llvm')

        link_path = os.path.join(builder.tp_dir, 'clang-toolchain')
        remove_path(link_path)
        list_dest = os.path.relpath(prefix, builder.tp_dir)
        log("Link {} => {}".format(link_path, list_dest))
        os.symlink(list_dest, link_path)

    def should_build(self, builder):
        return builder.will_need_clang()
