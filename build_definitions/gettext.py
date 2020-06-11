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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from build_definitions import *

class GetTextDependency(Dependency):
    def __init__(self):
        super(GetTextDependency, self).__init__(
                'gettext', '0.20.2',
                'https://github.com/yugabyte/gettext/archive/v{0}.tar.gz',
                BUILD_GROUP_COMMON)
        self.copy_sources = True

    def build(self, builder):
        # Arguments based on:
        # https://github.com/Homebrew/homebrew-core/blob/master/Formula/gettext.rb
        configure_args=[
            "--disable-dependency-tracking",
            "--disable-silent-rules",
            "--disable-debug",
            "--with-included-gettext",
            # Work around a gnulib issue with macOS Catalina
            "gl_cv_func_ftello_works=yes",
            "--with-included-glib",
            "--with-included-libcroco",
            "--with-included-libunistring",
            "--without-emacs",
            "--without-lispdir",
            "--disable-java",
            "--disable-csharp",
            # Don't use VCS systems to create these archives
            "--without-git",
            "--without-cvs",
            "--without-xz"
        ]
        builder.build_with_configure(
            builder.log_prefix(self), 
            extra_args=configure_args,
            autogen=True)

            
