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
        self.patches = ['llvm-disable-hwasan.patch']
        self.patch_strip = 1

    def build(self, builder):
        prefix = builder.get_prefix('llvm10')

        python_executable = which('python3')
        if not os.path.exists(python_executable):
            fatal("Could not find Python -- needed to build LLVM.")

        cxx_flags = builder.compiler_flags + builder.cxx_flags + builder.ld_flags
        if '-g' in cxx_flags:
            cxx_flags.remove('-g')

        # For multi-stage builds see
        # - https://llvm.org/docs/AdvancedBuilds.html
        # - https://bit.ly/2As8Imx

        cxx_flags += ['-Wno-pedantic']
        llvm_enable_projects = [
                'clang',
                'compiler-rt',
                'libunwind',
                'libcxx',
                'libcxxabi'
            ]
        clang_bootstrap_targets = [
                'install-compiler-rt',
                'install-libcxxabi',
                'install-libcxx',
                'install-clang',
                'install-clang-headers'
        ]
        all_stage_args = [
            'CMAKE_BUILD_TYPE=Release',
            'CLANG_DEFAULT_CXX_STDLIB=libc++',
            'CLANG_DEFAULT_RTLIB=compiler-rt',
            'LIBCXXABI_USE_LLVM_UNWINDER=ON',
            'LLVM_TARGETS_TO_BUILD=X86',
            'LLVM_ENABLE_RTTI=ON',
            'LLVM_INCLUDE_TESTS=OFF',
            'CMAKE_CXX_FLAGS={}'.format(" ".join(cxx_flags)),
        ]
        cmake_args = [
            '-DCMAKE_INSTALL_PREFIX={}'.format(prefix),
            '-DCLANG_ENABLE_BOOTSTRAP=ON',
            '-DLLVM_ENABLE_PROJECTS={}'.format(';'.join(llvm_enable_projects)),
            '-DPYTHON_EXECUTABLE={}'.format(python_executable),
            '-DCLANG_BOOTSTRAP_TARGETS={}'.format(';'.join(clang_bootstrap_targets))
        ] + [
            '-D{}'.format(arg) for arg in all_stage_args
        ] + [
             '-DBOOTSTRAP_{}'.format(arg) for arg in all_stage_args
        ]
        builder.build_with_cmake(self,
                                 cmake_args,
                                 use_ninja='auto',
                                 src_dir='llvm',
                                 extra_build_tool_args=['stage2'])

        link_path = os.path.join(builder.tp_dir, 'clang-toolchain')
        remove_path(link_path)
        list_dest = os.path.relpath(prefix, builder.tp_dir)
        log("Link {} => {}".format(link_path, list_dest))
        os.symlink(list_dest, link_path)

    def should_build(self, builder):
        return builder.will_need_clang()
