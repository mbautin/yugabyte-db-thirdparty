#!/usr/bin/env bash
#
# Copyright (c) YugaByte, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.  See the License for the specific language governing permissions and limitations
# under the License.
#
set -euo pipefail
yb_thirdparty_repo_root=$( cd "${BASH_SOURCE%/*}" && pwd )
. "$yb_thirdparty_repo_root/yb-thirdparty-common.sh"

if [[ -n ${YB_THIRDPARTY_DIR:-} && $YB_THIRDPARTY_DIR != $yb_thirdparty_repo_root ]]; then
  echo >&2 "Warning: un-setting previously set YB_THIRDPARTY_DIR: $YB_THIRDPARTY_DIR"
fi

export YB_THIRDPARTY_DIR=$yb_thirdparty_repo_root
echo "YB_THIRDPARTY_DIR=${YB_THIRDPARTY_DIR:-undefined}"

if [[ -z ${YB_SRC_ROOT:-} ]]; then
  yb_src_root_candidate=$( cd "${BASH_SOURCE%/*}"/.. && pwd )
  if [[ -d $yb_src_root_candidate/build-support ]]; then
    YB_SRC_ROOT=$yb_src_root_candidate
  fi
fi

echo "YB_SRC_ROOT=${YB_SRC_ROOT:-undefined}"
if [[ -n ${YB_SRC_ROOT:-} ]]; then
  # TODO: re-test this path. This might not work. We should keep yugabyte-db-thirdparty scripts
  # separate from the main repo scripts.
  echo "Building YugabyteDB third-party dependencies inside a YugabyteDB source tree: " \
       "$YB_SRC_ROOT"
  . "$YB_SRC_ROOT/build-support/common-build-env.sh"
  detect_brew
  add_brew_bin_to_path
else
  echo "Building YugabyteDB in a stand-alone mode (not within a YugabyteDB source tree)."
  # Running outside of a YugabyteDB codebase -- this is a stand-alone thirdparty deps build.
  if [[ ! -d $YB_THIRDPARTY_DIR/venv ]]; then
    python3 -m venv "$YB_THIRDPARTY_DIR/venv"
  fi
  set +u
  . "$YB_THIRDPARTY_DIR/venv/bin/activate"
  set -u
  ( set -x; cd "$YB_THIRDPARTY_DIR" && pip3 install -r requirements.txt )
fi

echo "YB_LINUXBREW_DIR=${YB_LINUXBREW_DIR:-undefined}"
if [[ $OSTYPE == linux* && -n ${YB_LINUXBREW_DIR:-} ]]; then
  if [[ ! -d $YB_LINUXBREW_DIR ]]; then
    fatal "Directory specified by YB_LINUXBREW_DIR ('$YB_LINUXBREW_DIR') does not exist"
  fi
  export PATH=$YB_LINUXBREW_DIR/bin:$PATH
fi

echo "YB_CUSTOM_HOMEBREW_DIR=${YB_CUSTOM_HOMEBREW_DIR:-undefined}"

set -x
python3 "$YB_THIRDPARTY_DIR/yb_build_thirdparty_main.py" "$@" ${YB_BUILD_THIRDPARTY_EXTRA_ARGS:-}
