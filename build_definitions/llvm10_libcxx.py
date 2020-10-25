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

from build_definitions import BUILD_TYPE_ASAN, BUILD_TYPE_TSAN
from build_definitions.llvm10_part import Llvm10PartDependencyBase

from yugabyte_db_thirdparty.util import replace_string_in_file

from yugabyte_db_thirdparty.build_definition_helpers import *  # noqa


LIBCXX_LLVM_VERSION = '10.0.1'


class Llvm10LibCxxDependencyBase(Llvm10PartDependencyBase):
    def __init__(self, name: str) -> None:
        super(Llvm10LibCxxDependencyBase, self).__init__(
            name=name,
            build_group=BUILD_GROUP_INSTRUMENTED)

    def postprocess_ninja_build_file(
            self,
            builder: BuilderInterface,
            ninja_build_file_path: str) -> None:
        super().postprocess_ninja_build_file(builder, ninja_build_file_path)
        if builder.build_type not in [BUILD_TYPE_ASAN, BUILD_TYPE_TSAN]:
            return

        removed_string = '-lstdc++'
        num_lines_modified = replace_string_in_file(
            path=ninja_build_file_path,
            str_to_replace=removed_string,
            str_to_replace_with='')
        log("Modified %d lines in file %s: removed '%s'",
            num_lines_modified, os.path.abspath(ninja_build_file_path), removed_string)

    def get_additional_ld_flags(self, builder: BuilderInterface) -> List[str]:
        if builder.build_type in [BUILD_TYPE_ASAN, BUILD_TYPE_TSAN]:
            # We need to link with these libraries in ASAN because otherwise libc++ CMake
            # configuration step fails and some C standard library functions cannot be found.
            # However, we then remove -lstdc++ from the generated build.ninja file (see
            # postprocess_ninja_build_file). The other libraries (-ldl, -lpthread, and -lm) are OK
            # to keep.
            return ['-ldl', '-lpthread', '-lm', '-lstdc++']

        return []

    def get_install_prefix(self, builder: BuilderInterface) -> str:
        return os.path.join(builder.prefix, 'libcxx')

    def build(self, builder: BuilderInterface) -> None:
        llvm_src_path = builder.get_source_path(self)

        args = [
            '-DCMAKE_BUILD_TYPE=Release',
            '-DBUILD_SHARED_LIBS=ON',
            '-DLLVM_PATH=%s' % llvm_src_path,
        ]

        builder.build_with_cmake(
            self,
            extra_args=args,
            src_subdir_name=self.get_source_dir_name(),
            use_ninja_if_available=True)

    def get_source_dir_name(self) -> str:
        raise NotImplementedError()


class Llvm10LibCxxAbiDependency(Llvm10LibCxxDependencyBase):
    def __init__(self) -> None:
        super(Llvm10LibCxxAbiDependency, self).__init__('libcxxabi10')

    def get_source_dir_name(self) -> str:
        return 'libcxxabi'

    def get_additional_cmake_args(self, builder: BuilderInterface) -> List[str]:
        llvm_src_path = builder.get_source_path(self)
        return [
            '-DLIBCXXABI_LIBCXX_PATH=%s' % os.path.join(llvm_src_path, 'libcxx'),
            '-DLIBCXXABI_USE_COMPILER_RT=ON',
            '-DLIBCXXABI_USE_LLVM_UNWINDER=ON',
            '-DLIBCXXABI_ENABLE_RTTI=ON',
        ]

    def build(self, builder: BuilderInterface) -> None:
        super().build(builder)
        src_include_path = os.path.join(builder.get_source_path(self), 'libcxxabi', 'include')
        # Put C++ ABI headers together with libc++ headers.
        dest_include_path = os.path.join(self.get_install_prefix(builder), 'include', 'c++', 'v1')
        mkdir_if_missing(dest_include_path)
        for header_name in ['cxxabi.h', '__cxxabi_config.h']:
            copy_file_and_log(
                os.path.join(src_include_path, header_name),
                os.path.join(dest_include_path, header_name))


class Llvm10LibCxxDependency(Llvm10LibCxxDependencyBase):
    def __init__(self) -> None:
        super(Llvm10LibCxxDependency, self).__init__('libcxx10')

    def get_source_dir_name(self) -> str:
        return 'libcxx'

    def get_additional_cmake_args(self, builder: BuilderInterface) -> List[str]:
        return [
            '-DLIBCXX_USE_COMPILER_RT=ON',
            '-DLIBCXX_ENABLE_RTTI=ON',
        ]
