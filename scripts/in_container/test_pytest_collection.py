#!/usr/bin/env python
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

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml
from rich.console import Console

AIRFLOW_SOURCES_ROOT = Path(__file__).parents[2].resolve()
AIRFLOW_PROVIDERS_ROOT = AIRFLOW_SOURCES_ROOT / "airflow" / "providers"
console = Console(width=400, color_system="standard")


def remove_packages_missing_on_arm():
    console.print("[bright_blue]Removing packages missing on ARM.")
    provider_dependencies = json.loads(
        (AIRFLOW_SOURCES_ROOT / "generated" / "provider_dependencies.json").read_text()
    )
    all_dependencies_to_remove = []
    for provider in provider_dependencies:
        for dependency in provider_dependencies[provider]["deps"]:
            if 'platform_machine != "aarch64"' in dependency:
                all_dependencies_to_remove.append(re.split(r"[~<>=;]", dependency)[0])
    console.print(
        "\n[bright_blue]Uninstalling ARM-incompatible libraries "
        + " ".join(all_dependencies_to_remove)
        + "\n"
    )
    subprocess.run(["pip", "uninstall", "-y"] + all_dependencies_to_remove)


def get_suspended_providers_folders() -> list[str]:
    """
    Returns a list of suspended providers folders that should be
    skipped when running tests (without any prefix - for example apache/beam, yandex, google etc.).
    """
    suspended_providers = []
    for provider_path in AIRFLOW_PROVIDERS_ROOT.glob("**/provider.yaml"):
        provider_yaml = yaml.safe_load(provider_path.read_text())
        if provider_yaml.get("suspended"):
            suspended_providers.append(
                provider_path.parent.relative_to(AIRFLOW_SOURCES_ROOT)
                .as_posix()
                .replace("airflow/providers/", "")
            )
    return suspended_providers


if __name__ == "__main__":
    arm = False
    if len(sys.argv) > 1 and sys.argv[1].lower() == "arm":
        arm = True
        remove_packages_missing_on_arm()
    suspended_providers = get_suspended_providers_folders()
    cmd = [
        "pytest",
        *[f"--ignore=tests/providers/{provider}" for provider in suspended_providers],
        *[f"--ignore=tests/system/providers/{provider}" for provider in suspended_providers],
        *[f"--ignore=tests/integration/providers/{provider}" for provider in suspended_providers],
        "--collect-only",
        "-qqqq",
        "--disable-warnings",
        "tests",
    ]
    console.print(f"Running command {cmd}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        console.print("\n[red]Test collection failed.")
        if arm:
            console.print(
                "[yellow]You should wrap the failing imports in try/except/skip clauses\n"
                "See similar examples as skipped tests right above.\n"
            )
        else:
            console.print("[yellow]Please add missing packages\n")
        exit(result.returncode)
