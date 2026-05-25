# -*- coding: utf-8 -*-
#
#   Copyright 2026 Karellen, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import textwrap

from pybuilder.core import (use_plugin, init, Author)

use_plugin("pypi:karellen_pyb_plugin", ">=0.0.1")
use_plugin("python.coveralls")
use_plugin("filter_resources")

name = "textual-vision"
version = "0.0.1.dev"

summary = "Turbo Vision UI framework architecture for Textual"
authors = [Author("Karellen, Inc.", "supervisor@karellen.co")]
maintainers = [Author("Arcadiy Ivanov", "arcadiy@karellen.co")]

url = "https://github.com/karellen/textual-vision"
urls = {
    "Bug Tracker": "https://github.com/karellen/textual-vision/issues",
    "Source Code": "https://github.com/karellen/textual-vision/",
    "Documentation": "https://github.com/karellen/textual-vision/"
}
license = "Apache-2.0"

requires_python = ">=3.10"

default_task = ["analyze", "publish"]


@init
def set_properties(project):
    project.depends_on("textual", ">=3.0")

    project.set_property("coverage_break_build", False)
    project.set_property("cram_fail_if_no_tests", False)

    project.set_property("integrationtest_inherit_environment", True)

    project.set_property("copy_resources_target", "$dir_dist/textual_vision")
    project.get_property("copy_resources_glob").append("LICENSE")
    project.set_property("filter_resources_target", "$dir_dist")
    project.get_property("filter_resources_glob").append("textual_vision/__init__.py")
    project.include_file("textual_vision", "LICENSE")

    project.set_property("distutils_upload_sign", False)
    project.set_property("distutils_upload_sign_identity", None)
    project.set_property("distutils_upload_repository_key", None)
    project.set_property("distutils_setup_keywords", ["textual", "turbo-vision", "tui",
                                                      "terminal", "ui", "framework",
                                                      "desktop", "window", "dialog", "menu"])

    project.set_property("distutils_classifiers", [
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Intended Audience :: Developers",
        "Development Status :: 1 - Planning"
    ])

    project.set_property('pybuilder_header_plugin_break_build', False)
    project.set_property("pybuilder_header_plugin_expected_header",
                         textwrap.dedent("""\
                         # -*- coding: utf-8 -*-
                         #
                         #   Copyright 2026 Karellen, Inc.
                         #
                         #   Licensed under the Apache License, Version 2.0 (the "License");
                         #   you may not use this file except in compliance with the License.
                         #   You may obtain a copy of the License at
                         #
                         #       http://www.apache.org/licenses/LICENSE-2.0
                         #
                         #   Unless required by applicable law or agreed to in writing, software
                         #   distributed under the License is distributed on an "AS IS" BASIS,
                         #   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
                         #   See the License for the specific language governing permissions and
                         #   limitations under the License.
                         #
                         """))
