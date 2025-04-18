# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import os
import re
import shutil
import sys
from glob import glob
from subprocess import run

from rich.console import Console

from sphinx_exts.docs_build.code_utils import (
    AIRFLOW_CONTENT_ROOT_PATH,
    ALL_PROVIDER_YAMLS,
    ALL_PROVIDER_YAMLS_WITH_SUSPENDED,
    CONSOLE_WIDTH,
    GENERATED_APIS_PATH,
    GENERATED_PATH,
    PROCESS_TIMEOUT,
)
from sphinx_exts.docs_build.errors import DocBuildError, parse_sphinx_warnings
from sphinx_exts.docs_build.spelling_checks import SpellingError, parse_spelling_warnings

console = Console(force_terminal=True, color_system="standard", width=CONSOLE_WIDTH)


class AirflowDocsBuilder:
    """Documentation builder for Airflow."""

    def __init__(self, package_name: str):
        self.package_name = package_name
        self.is_provider = False
        self.is_airflow = False
        self.is_chart = False
        self.is_docker_stack = False
        self.is_providers_summary = False
        if self.package_name.startswith("apache-airflow-providers-"):
            self.package_id = self.package_name.split("apache-airflow-providers-", 1)[1].replace("-", ".")
            self.provider_path = (AIRFLOW_CONTENT_ROOT_PATH / "providers").joinpath(
                *self.package_id.split(".")
            )
            self.is_provider = True
        if self.package_name == "apache-airflow":
            self.is_airflow = True
        if self.package_name == "helm-chart":
            self.is_chart = True
        if self.package_name == "docker-stack":
            self.is_docker_stack = True
        if self.package_name == "apache-airflow-providers":
            self.is_providers_summary = True

    @property
    def _doctree_dir(self) -> str:
        return f"{GENERATED_PATH}/_doctrees/docs/{self.package_name}"

    @property
    def _inventory_cache_dir(self) -> str:
        return f"{GENERATED_PATH}/_inventory_cache"

    @property
    def is_versioned(self):
        """Is current documentation package versioned?"""
        # Disable versioning. This documentation does not apply to any released product and we can update
        # it as needed, i.e. with each new package of providers.
        return self.package_name not in ("apache-airflow-providers", "docker-stack")

    @property
    def _build_dir(self) -> str:
        if self.is_versioned:
            version = "stable"
            return f"{GENERATED_PATH}/_build/docs/{self.package_name}/{version}"
        else:
            return f"{GENERATED_PATH}/_build/docs/{self.package_name}"

    @property
    def log_spelling_filename(self) -> str:
        """Log from spelling job."""
        return os.path.join(self._build_dir, f"output-spelling-{self.package_name}.log")

    @property
    def log_spelling_output_dir(self) -> str:
        """Results from spelling job."""
        return os.path.join(self._build_dir, f"output-spelling-results-{self.package_name}")

    @property
    def log_build_filename(self) -> str:
        """Log from build job."""
        return os.path.join(self._build_dir, f"output-build-{self.package_name}.log")

    @property
    def log_build_warning_filename(self) -> str:
        """Warnings from build job."""
        return os.path.join(self._build_dir, f"warning-build-{self.package_name}.log")

    @property
    def _src_dir(self) -> str:
        if self.package_name == "helm-chart":
            return (AIRFLOW_CONTENT_ROOT_PATH / "chart" / "docs").as_posix()
        elif self.package_name == "apache-airflow":
            return (AIRFLOW_CONTENT_ROOT_PATH / "airflow-core" / "docs").as_posix()
        elif self.package_name == "docker-stack":
            return (AIRFLOW_CONTENT_ROOT_PATH / "docker-stack-docs").as_posix()
        elif self.package_name == "apache-airflow-providers":
            return (AIRFLOW_CONTENT_ROOT_PATH / "providers-summary-docs").as_posix()
        elif self.package_name.startswith("apache-airflow-providers-"):
            package_paths = self.package_name[len("apache-airflow-providers-") :].split("-")
            return ((AIRFLOW_CONTENT_ROOT_PATH / "providers").joinpath(*package_paths) / "docs").as_posix()
        else:
            console.print(f"[red]Unknown package name: {self.package_name}")
            sys.exit(1)

    @property
    def _api_dir(self):
        return GENERATED_APIS_PATH / self.package_name

    def clean_files(self) -> None:
        """Cleanup all artifacts generated by previous builds."""
        api_dir = os.path.join(self._api_dir, "_api")
        shutil.rmtree(api_dir, ignore_errors=True)
        shutil.rmtree(self._build_dir, ignore_errors=True)
        os.makedirs(api_dir, exist_ok=True)
        os.makedirs(self._build_dir, exist_ok=True)

    def check_spelling(self, verbose: bool) -> tuple[list[SpellingError], list[DocBuildError]]:
        """
        Checks spelling

        :param verbose: whether to show output while running
        :return: list of errors
        """
        spelling_errors = []
        build_errors = []
        os.makedirs(self._build_dir, exist_ok=True)
        shutil.rmtree(self.log_spelling_output_dir, ignore_errors=True)
        os.makedirs(self.log_spelling_output_dir, exist_ok=True)

        build_cmd = [
            "sphinx-build",
            "-W",  # turn warnings into errors
            "--color",  # do emit colored output
            "-T",  # show full traceback on exception
            "-b",  # builder to use
            "spelling",
            "-d",  # path for the cached environment and doctree files
            self._doctree_dir,
            # documentation source files
            self._src_dir,
            self.log_spelling_output_dir,
        ]

        env = os.environ.copy()
        env["AIRFLOW_PACKAGE_NAME"] = self.package_name
        if verbose:
            console.print(
                f"[bright_blue]{self.package_name:60}:[/] The output is hidden until an error occurs."
            )
        with open(self.log_spelling_filename, "w") as output:
            completed_proc = run(
                build_cmd,
                cwd=AIRFLOW_CONTENT_ROOT_PATH,
                env=env,
                stdout=output if not verbose else None,
                stderr=output if not verbose else None,
                timeout=PROCESS_TIMEOUT,
            )
        if completed_proc.returncode != 0:
            spelling_errors.append(
                SpellingError(
                    file_path=None,
                    line_no=None,
                    spelling=None,
                    suggestion=None,
                    context_line=None,
                    message=(
                        f"Sphinx spellcheck returned non-zero exit status: {completed_proc.returncode}."
                    ),
                )
            )
            spelling_warning_text = ""
            for filepath in glob(f"{self.log_spelling_output_dir}/**/*.spelling", recursive=True):
                with open(filepath) as spelling_file:
                    spelling_warning_text += spelling_file.read()
            spelling_errors.extend(parse_spelling_warnings(spelling_warning_text, self._src_dir))
            if os.path.isfile(self.log_spelling_filename):
                with open(self.log_spelling_filename) as warning_file:
                    warning_text = warning_file.read()
                # Remove 7-bit C1 ANSI escape sequences
                warning_text = re.sub(r"\x1B[@-_][0-?]*[ -/]*[@-~]", "", warning_text)
                build_errors.extend(parse_sphinx_warnings(warning_text, self._src_dir))
            console.print(
                f"[bright_blue]{self.package_name:60}:[/] [red]Finished spell-checking with errors[/]"
            )
        else:
            if spelling_errors:
                console.print(
                    f"[bright_blue]{self.package_name:60}:[/] [yellow]Finished spell-checking with warnings[/]"
                )
            else:
                console.print(
                    f"[bright_blue]{self.package_name:60}:[/] [green]Finished spell-checking successfully[/]"
                )
        return spelling_errors, build_errors

    def build_sphinx_docs(self, verbose: bool) -> list[DocBuildError]:
        """
        Build Sphinx documentation.

        :param verbose: whether to show output while running
        :return: list of errors
        """
        build_errors = []
        os.makedirs(self._build_dir, exist_ok=True)
        build_cmd = [
            "sphinx-build",
            "-T",  # show full traceback on exception
            "--color",  # do emit colored output
            "-b",  # builder to use
            "html",
            "-d",  # path for the cached environment and doctree files
            self._doctree_dir,
            "-w",  # write warnings (and errors) to given file
            self.log_build_warning_filename,
            # documentation source files
            self._src_dir,
            self._build_dir,  # path to output directory
        ]
        env = os.environ.copy()
        env["AIRFLOW_PACKAGE_NAME"] = self.package_name
        if verbose:
            console.print(
                f"[bright_blue]{self.package_name:60}:[/] Running sphinx. "
                f"The output is hidden until an error occurs."
            )
        with open(self.log_build_filename, "w") as output:
            completed_proc = run(
                build_cmd,
                cwd=AIRFLOW_CONTENT_ROOT_PATH,
                env=env,
                stdout=output if not verbose else None,
                stderr=output if not verbose else None,
                timeout=PROCESS_TIMEOUT,
            )
        if completed_proc.returncode != 0:
            build_errors.append(
                DocBuildError(
                    file_path=None,
                    line_no=None,
                    message=f"Sphinx returned non-zero exit status: {completed_proc.returncode}.",
                )
            )
        if os.path.isfile(self.log_build_warning_filename):
            with open(self.log_build_warning_filename) as warning_file:
                warning_text = warning_file.read()
            # Remove 7-bit C1 ANSI escape sequences
            warning_text = re.sub(r"\x1B[@-_][0-?]*[ -/]*[@-~]", "", warning_text)
            build_errors.extend(parse_sphinx_warnings(warning_text, self._src_dir))
        if build_errors:
            console.print(
                f"[bright_blue]{self.package_name:60}:[/] [red]Finished docs building with errors[/]"
            )
        else:
            console.print(
                f"[bright_blue]{self.package_name:60}:[/] [green]Finished docs building successfully[/]"
            )
        return build_errors


def get_available_providers_distributions(include_suspended: bool = False):
    """Get list of all available providers packages to build."""
    return [
        provider["package-name"]
        for provider in (ALL_PROVIDER_YAMLS_WITH_SUSPENDED if include_suspended else ALL_PROVIDER_YAMLS)
    ]


def get_available_packages(include_suspended: bool = False):
    """Get list of all available packages to build."""
    provider_names = get_available_providers_distributions(include_suspended=include_suspended)
    return [
        "apache-airflow",
        *provider_names,
        "apache-airflow-providers",
        "helm-chart",
        "docker-stack",
    ]
