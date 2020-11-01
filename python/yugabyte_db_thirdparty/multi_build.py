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

import os
import concurrent.futures
import datetime
import yaml

from typing import List, Dict, Optional
from yugabyte_db_thirdparty.util import mkdir_if_missing, PushDir, log_and_run_cmd
from yugabyte_db_thirdparty.util import YB_THIRDPARTY_DIR
from yugabyte_db_thirdparty.custom_logging import log
from yugabyte_db_thirdparty.remote_build import copy_code_to


CIRCLECI_CONFIG_PATH = os.path.join(YB_THIRDPARTY_DIR, '.circleci', 'config.yml')

CENTOS7_DOCKER_IMAGE = 'yugabyteci/yb_build_infra_centos7:v2020-10-17T18_09_58'


class BuildResult:
    def __init__(self) -> None:
        pass


class BuildConfiguration:
    run_root_dir: str
    code_dir: str
    run_dir: str
    name: str
    docker_image: str
    args: List[str]

    def __init__(
            self,
            run_root_dir: str,
            code_dir: str,
            name: str,
            docker_image: str,
            args: List[str]) -> None:
        self.run_root_dir = run_root_dir
        self.code_dir = code_dir
        self.name = name
        self.docker_image = docker_image
        self.args = args

    def prepare(self) -> None:
        self.run_dir = os.path.join(self.run_root_dir, self.name)
        self.dockerfile_path = os.path.join(self.run_root_dir, f'Dockerfile-{self.name}')
        mkdir_if_missing(self.run_dir)
        immutable_code_dir_in_container = '/outside-of-container/yugabyte-db-thirdparty-immutables'
        rel_code_dir = os.path.relpath(
            os.path.abspath(self.code_dir),
            os.path.dirname(os.path.abspath(self.dockerfile_path)))

        copy_code_and_build_cmd_str = ' && '.join([
            'mkdir -p ~/code',
            f'cp -R "{immutable_code_dir_in_container}" ~/code/yugabyte-db-thirdparty',
            'cd ~/code/yugabyte-db-thirdparty',
            './build_thirdparty.sh',
        ])

        dockerfile_lines = [
            f'FROM {self.docker_image}',
            'USER yugabyteci',
            f'ADD "{rel_code_dir}" "{immutable_code_dir_in_container}"',
            'RUN ' + copy_code_and_build_cmd_str
        ]
        with open(self.dockerfile_path, 'w') as docker_file:
            docker_file.write('\n'.join(dockerfile_lines) + '\n')

    def build(self) -> BuildResult:
        with PushDir(self.run_dir):
            log_and_run_cmd(['docker', 'build', '--file', self.dockerfile_path, '.'])

        return BuildResult()


def build_configuration(configuration: BuildConfiguration) -> BuildResult:
    return configuration.build()


class MultiBuilder:
    configurations: List[BuildConfiguration]
    common_timestamp_str: str
    run_root_dir: str

    def __init__(self) -> None:
        self.common_timestamp_str = datetime.datetime.now().strftime('%Y-%m-%dT%H_%M_%S')
        dir_of_all_runs = os.path.join(
            os.path.expanduser('~'), 'yugabyte-db-thirdparty-multi-build')
        self.run_root_dir = os.path.join(dir_of_all_runs, self.common_timestamp_str)
        latest_link = os.path.join(dir_of_all_runs, 'latest')
        self.code_dir = os.path.join(self.run_root_dir, 'code', 'yugabyte-db-thirdparty')
        mkdir_if_missing(os.path.dirname(self.code_dir))
        if os.path.exists(latest_link):
            os.remove(latest_link)
        os.symlink(os.path.basename(self.run_root_dir), latest_link)
        copy_code_to(self.code_dir)

        with open(CIRCLECI_CONFIG_PATH) as circleci_conf_file:
            circleci_conf = yaml.load(circleci_conf_file)

        self.configurations = []

        for circleci_job in circleci_conf['workflows']['build-release']['jobs']:
            build_params = circleci_job['build']
            self.configurations.append(
                BuildConfiguration(
                    run_root_dir=self.run_root_dir,
                    code_dir=self.code_dir,
                    name=build_params['name'],
                    docker_image=build_params['docker_image'],
                    args=build_params.get('build_thirdparty_args', '').split()))

    def build(self) -> None:
        for configuration in self.configurations:
            configuration.prepare()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            for configuration in self.configurations:
                future_to_configuration = {
                    executor.submit(build_configuration, configuration): configuration
                    for configuration in self.configurations
                }
                for future in concurrent.futures.as_completed(future_to_configuration):
                    try:
                        result = future.result()
                    except Exception as exc:
                        print("Build generated an exception: %s" % exc)