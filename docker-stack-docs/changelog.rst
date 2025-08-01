 .. Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

 ..   http://www.apache.org/licenses/LICENSE-2.0

 .. Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.

Dockerfile Changelog
====================

The ``Dockerfile`` does not strictly follow the `SemVer <https://semver.org/>`_ approach of
Apache Airflow when it comes to features and backwards compatibility. While Airflow code strictly
follows it, the ``Dockerfile`` is really a way to give users a conveniently packaged Airflow
using standard container approach, so occasionally there are some changes in the building process
or in the entrypoint of the image that require slight adaptation of how it is used or built.

The Changelog below describes the changes introduced in each version of the docker images released by
the Airflow team.

:note: The Changelog below concerns only the convenience production images released at
       `Airflow DockerHub <https://hub.docker.com/r/apache/airflow>`_ . The images that are released
       there are usually built using the ``Dockerfile`` released together with Airflow. However, you are
       free to take latest released ``Dockerfile`` from Airflow and use it to build an image for
       any Airflow version from the ``Airflow 2`` line. There is no guarantee that it will work, but if it does,
       then you can use latest features from that image to build images for previous Airflow versions.

Airflow 3.0.2
~~~~~~~~~~~~~

  * The ``git`` binary was added to the image by default which is needed for the git provider to work.

Airflow 3.0.1
~~~~~~~~~~~~~

  * The ``ARM`` image is not experimental any more - we are running the ARM tests regularly in our CI. The
    ``MySQL`` support for `ARM` images however is still experimental.

Airflow 3.0
~~~~~~~~~~~

  * The ``virtualenv`` package is no longer installed in the reference container. Airflow 3 and standard
    provider relies on ``venv`` module from Python standard library.
  * There is no ``pipx`` and ``mssql-cli`` installed in the image by default. We recommend to use
    ``uv tool`` instead of ``pipx`` and ``mssql-cli`` is not used in the image by default as we do not
    have mssql metadata support any more.
  * The ``INSTALL_PACKAGES_FROM_CONTEXT`` arg changed to ``INSTALL_DISTRIBUTIONS_FROM_CONTEXT``
  * The parameter ``UPGRADE_INVALIDATION_STRING`` is renamed to ``UPGRADE_RANDOM_INDICATOR_STRING``

Airflow 2.10
~~~~~~~~~~~~
  * The image does not support Debian-Bullseye(11) anymore. The image is based on Debian-Bookworm (12).

Airflow 2.9
~~~~~~~~~~~

  * The "latest" image (i.e. default Airflow image when ``apache/airflow`` is used or
    ``apache/airflow:slim-latest``) uses now the newest supported Python version. Previously it was using
    the "default" Python version which was Python 3.8 as of Airflow 2.8. With Airflow reference images
    released for Airflow 2.9.0, the images are going to use Python 3.12 as this is the latest supported
    version for Airflow 2.9 line. Users can use Python 3.8 by using ``apache/airflow:2.9.0-python3.8`` and
    ``apache/airflow:slim-2.9.0-python-3.8`` images respectively so while the change is potentially
    breaking, it is very easy to switch to the previous behaviour.

  * The ``PIP_USER`` flag is removed and replaced by ``VIRTUAL_ENV`` pointing to ``~/.local`` where Airflow
    is installed. This has the effect that the Airflow installation is treated as a regular virtual environment,
    but unlike a regular virtualenv, the ``~/.local`` directory is seen as ``system level`` and when the
    worker creates dynamically the virtualenv with ``--system-site-packages`` flag, the Airflow installation and all
    packages there are also present in the new virtualenv. When you do not use the flag, they are not
    copied there which is a backwards-compatible behaviour with having ``PIP_USER`` set.

  * The image contains latest ``uv`` binary (latest at the moment of release) - which is a new faster
    replacement for ``pip``. While the image is still using ``pip`` by default, you can use ``uv``
    to install packages and - experimentally - you can also build custom images with
    ``--arg AIRFLOW_USE_UV=true`` which will us ``uv`` to perform the installation. This is an experimental
    support, as ``uv`` is very fast but also a very new feature in the Python ecosystem.

  * Constraints used to install the image are available in "${HOME}/constraints.txt" now - you can use them
    to install additional packages in the image without having to find out which constraints you should use.

  * The image adds ``libev`` library to the image as it is required by cassandra driver for Python 3.12, also
    ``libev`` will be used in other Python versions as a more robust and faster way for cassandra driver
    to handle events.

Airflow 2.8
~~~~~~~~~~~
* 2.8.3

  * The ``gosu`` binary was removed from the image. This is a potentially breaking change for users who relied on
    ``gosu`` to change the user in the container. The ``gosu`` binary was removed because it was a source of
    security vulnerabilities as it was linked against older Go standard libraries.

  * The ``smtp`` provider is now included in the list of providers installed by default in the image.

* 2.8.1

  * Fixed a discrepancy in MySQL client libraries. In 2.8.0 if not specify ``INSTALL_MYSQL_CLIENT_TYPE`` build arg
    during build custom X86 image by default packages would be compiled by using **MariaDB** libraries,
    however **MySQL** libraries were installed in the final image.

* 2.8.0

  * Add ``libxmlsec1`` and ``libxmlsec1-dev`` libraries to dev PROD image and ``libxmlsec1`` library to runtime PROD
    image as it is required by ``python3-saml`` library.

  * The image is based on ``Debian Bookworm`` in 2.8.0 rather than ``Debian Bullseye``. This might cause some
    problems when building custom images. You are advised to make sure your system level dependencies are
    working with ``Debian Bookworm``. While all reference images of Airflow 2.8.0 are built on ``Debian Bookworm``,
    it is still possible to build deprecated custom ``Debian Bullseye`` based image in 2.8.0 following the

  * By default the images now have "MariaDB" client installed. Previous images had "MySQL" client installed.
    The MariaDB client is a drop-in replacement for "MySQL" one and is compatible with MySQL. This might
    be a breaking change for users who used MySQL client in their images, however those should be very
    specific cases and vast majority of users should not see any difference. Users can still use
    MySQL client by setting ``INSTALL_MYSQL_CLIENT_TYPE=mysql`` build arg and build the custom X86 image.
    The ARM image always uses MariaDB client, this argument is ignored. The "mysql" apt repository is
    removed from the /etc/apt/sources.list.d/ and if you want to install anything from this repository when
    extending the images, you need to manually add the right key and repository in your Dockerfile,
    following the instructions in `A Quick Guide to Using the MySQL APT repository <https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/>`_.

Airflow 2.7
~~~~~~~~~~~

* 2.7.3

  * Add experimental feature for select type of MySQL Client libraries during the build custom image via ``INSTALL_MYSQL_CLIENT_TYPE``
    build arg. ``mysql`` for install MySQL client libraries from `Oracle APT repository <https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/>`_,
    ``mariadb`` for install MariaDB client libraries from `MariaDB repository <https://mariadb.com/kb/en/mariadb-package-repository-setup-and-usage/#mariadb-repository>`_.
    The selection of MySQL Client libraries only available on AMD64 (x86_64) for ARM docker image it will always install
    MariaDB client.

  * Docker CLI version in the image is bumped to 24.0.6 version.

  * PIP caching for local builds has been enabled to speed up local custom image building

* 2.7.0

  * As of now, Python 3.7 is no longer supported by the Python community. Therefore, to use Airflow 2.7.0, you must ensure your Python version is
    either 3.8, 3.9, 3.10, or 3.11.

Airflow 2.6
~~~~~~~~~~~~~

* 2.6.3

  * Add ``libgeos-dev`` library to runtime PROD image as it is required by BigQuery library on ARM image


* 2.6.0

  * Snowflake provider installed by default

  * The ARM experimental image adds support for MySQL via MariaDB client libraries.

Airflow 2.5
~~~~~~~~~~~

* 2.5.1

  * The ARM experimental image adds support for MSSQL

* 2.5.0

  * The docker CLI binary is now added to the images by default (available on PATH). Version 20.10.9 is used.

Airflow 2.4
~~~~~~~~~~~

* 2.4.0

  * You can specify additional ``pip install`` flags when you build the image via ``ADDITIONAL_PIP_INSTALL_FLAGS``
    build arg.
  * Support for ``Debian Buster`` was dropped, including the possibility of building customized images as
    ``Debian Buster`` reached end of life.

Airflow 2.3
~~~~~~~~~~~

* 2.3.0

  * Airflow 2.3 ``Dockerfile`` is now better optimized for caching and "standalone" which means that you
    can copy **just** the ``Dockerfile`` to any folder and start building custom images. This,
    however, requires `Buildkit <https://docs.docker.com/develop/develop-images/build_enhancements/>`_
    to build the image because we started using features that are only available in ``Buildkit``.
    This can be done by setting ``DOCKER_BUILDKIT=1`` as an environment variable
    or by installing `the buildx plugin <https://docs.docker.com/buildx/working-with-buildx/>`_
    and running ``docker buildx build`` command.
  * MySQL is experimentally supported on ARM through MariaDB client library
  * Add Python 3.10 support
  * Switch to ``Debian Bullseye`` based images. ``Debian Buster`` is deprecated and only available for
    customized image building.
  * Add Multi-Platform support (AMD64/ARM64) in order to accommodate MacOS M1 users
  * Build parameters which control if packages and Airflow should be installed from context file were
    unified
  * The ``INSTALL_FROM_PYPI`` arg was removed - it is automatically detected now.
  * The ``INSTALL_FROM_DOCKER_CONTEXT_FILES`` arg changed to ``INSTALL_PACKAGES_FROM_CONTEXT``

Airflow 2.2
~~~~~~~~~~~

* 2.2.4
  * Add support for both ``.piprc`` and ``pip.conf`` customizations
  * Add ArtifactHub labels for better discovery of the images
  * Update default Python image to be 3.7
  * Build images with ``Buildkit`` (optional)
  * Fix building the image on Azure with ``text file busy`` error

* 2.2.3
  * No changes

* 2.2.2
  * No changes

* 2.2.1
  * Workaround the problem with ``libstdcpp`` TLS error

* 2.2.0
  * Remove AIRFLOW_GID (5000) from Airflow images (potentially breaking change for users using it)
  * Added warnings for Quick-start docker compose
  * Fix warm shutdown for celery worker (signal propagation)
  * Add Oauth libraries to PROD images
  * Add Python 3.9 support

Airflow 2.1
~~~~~~~~~~~

* MySQL changed the keys to sign their packages on 17 Feb 2022. This caused all released images
  to fail when being extended. As result, on 18 Feb 2021 we re-released all
  the ``2.2`` and ``2.1`` images with latest versions of ``Dockerfile``
  containing the new signing key.

  There were subtle changes in the behaviour of some 2.1 images due to that (more details below)
  Detailed `issue here <https://github.com/apache/airflow/issues/20911>`_

:note: that the changes below were valid before image refreshing on 18 Feb 2022.
  Since all the images were refreshed on 18 Feb with the same ``Dockerfile``
  as 2.1.4, the changes 2.1.1 -> 2.1.3 are
  effectively applied to all the images in 2.1.* line.
  The images refreshed have also those fixes added:

* All 2.1.* image versions refreshed on 18 Feb 2022 have those fixes applied:
  * Fix building the image on Azure with ``text file busy`` error
  * Workaround the problem with ``libstdcpp`` TLS error
  * Remove AIRFLOW_GID (5000) from Airflow images (potentially breaking change for users using it)
  * Added warnings for Quick-start docker compose
  * Add Oauth libraries to PROD images

Original image Changelog (before the refresh on 18 Feb 2022):

* 2.1.4
   * Workaround the problem with ``libstdcpp`` TLS error
   * fixed detection of port number in connection URL
   * Improve warnings for quick-start-docker compose
   * Fix warm shutdown for celery worker (signal propagation)

* 2.1.3
   * fixed auto-creation of user to use non-deprecated ``create user`` rather than ``user_create``
   * remove waiting for celery backend for ``worker`` and ``flower`` commands rather than ``scheduler`` and ``celery`` only
   * remove deprecated ``airflow upgradedb`` command from Airflow 1.10 in case upgrade is requested
   * Add Python 3.9 support

* 2.1.2
   * No changes

* 2.1.1
   * Fix failure of lack of default commands (failed when no commands were passed)
   * Added ``_PIP_ADDITIONAL_REQUIREMENTS`` development feature

* 2.1.0
   * Unset default ``PIP_USER`` variable - which caused PythonVirtualEnv to fail

Airflow 2.0
~~~~~~~~~~~

* MySQL changed the keys to sign their packages on 17 Feb 2022. This caused all released images
  to fail when being extended. As result, on 18 Feb 2021 we re-released all
  the ``2.2`` and ``2.1`` images with latest versions of ``Dockerfile``
  containing the new signing key.

  There were no changes in the behaviour of 2.0.2 image due to that
  Detailed `issue here <https://github.com/apache/airflow/issues/20911>`_ .
  Only 2.0.2 image was regenerated, as 2.0.1 and 2.0.0 versions are hardly used and it is unlikely someone
  would like to extend those images. Extending 2.0.1 and 2.0.0 images will lead to failures of "missing key".

* 2.0.2
   * Set correct PYTHONPATH for ``root`` user. Allows to run the image as root
   * Warn if the deprecated 5000 group ID was used for airflow user when running the image
     (should be 0 for the OpenShift compatibility). Fails if the group 5000 was used with any other user
     (it would not work anyway but with cryptic errors)
   * Set umask as 002 by default, so that you can actually change the user id used to run the image
     (required for OpenShift compatibility)
   * Skip checking the DB and celery backend if CONNECTION_CHECK_MAX_COUNT is equal to 0

* 2.0.1
   * Avoid reverse IP lookup when checking DB availability. This helped to solve long delays on misconfigured
     docker engines
   * Add auto-detection of redis and amqp broker ports
   * Fixed detection of all user/password combinations in URLs - helps in auto-detecting ports and testing
     connectivity
   * Add possibility to create Admin user automatically when entering the image
   * Automatically create system user when different user than ``airflow`` is used. Needed for OpenShift
     compatibility
   * Allows to exec to ``bash`` or ``python`` if specified as parameters
   * Remove ``airflow`` command if it is specified as first parameter of the ``run`` command

* 2.0.0
   * Initial release of the image based on Debian Buster


Changes after publishing the images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Occasionally our images need to be regenerated using newer ``Dockerfiles`` or constraints.
This happens when an issue is found or a breaking change is released by our dependencies
that invalidates the already released image, and regenerating the image makes it usable again.
While we cannot assure 100% backwards compatibility when it happens, we at least document it
here so that users affected can find the reason for the changes.

+--------------+---------------------+-----------------------------------------+------------------------+------------------------------------------------+
| Date         | Affected images     | Potentially breaking change             | Reason                 | Link to Pull Request / Issue                   |
+==============+=====================+=========================================+========================+================================================+
| 19 July 2025 | 3.0.3               | * The ``standard`` provider             | Sensor skipping issue  | https://github.com/apache/airflow/pull/53455   |
|              |                     |   upgraded from 1.4.0 to 1.4.1          |                        |                                                |
+--------------+---------------------+-----------------------------------------+------------------------+------------------------------------------------+
| 24 Jun 2025  | 3.0.2               | * The ``fab`` provider                  | FAB provider user      | https://github.com/apache/airflow/issues/51854 |
|              |                     |   upgraded from 2.2.0 to 2.2.1          | creation did not work  |                                                |
|              |                     |                                         |                        |                                                |
|              |                     | * ``common.messaging`` provider         | importing SQS message  | https://github.com/apache/airflow/issues/51770 |
|              |                     |   upgraded from 1.0.2 to 1.0.3          | failed with circular   |                                                |
|              |                     |                                         | import                 |                                                |
|              |                     |                                         |                        |                                                |
|              |                     | * git binary is added to the image      | git bundle need it     | https://github.com/apache/airflow/pull/51580   |
+--------------+---------------------+-----------------------------------------+------------------------+------------------------------------------------+
| 02 Aug 2024  | 2.9.3               | * The ``apache-airflow-providers-fab``  | FAB provider logout    | https://github.com/apache/airflow/issues/40922 |
|              |                     |   upgraded from 1.2.1 to 1.2.2          | did not work for 2.9.3 |                                                |
+--------------+---------------------+-----------------------------------------+------------------------+------------------------------------------------+
| 12 Mar 2024  | 2.8.3               | * The image was refreshed with new      | Both dependencies      | https://github.com/apache/airflow/pull/37748   |
|              |                     |   dependencies (pandas < 2.2 and        | caused breaking        | https://github.com/apache/airflow/pull/37701   |
|              |                     |   SMTP provider 1.6.1                   | changes                |                                                |
+--------------+---------------------+-----------------------------------------+------------------------+------------------------------------------------+
| 16 Dec 2023  | All 2..\*           | * The AIRFLOW_GID 500 was removed       | MySQL repository is    | https://github.com/apache/airflow/issues/36231 |
|              |                     | * MySQL ``apt`` repository key changed. | removed after the      |                                                |
|              |                     |                                         | key expiry fiasco      |                                                |
+--------------+---------------------+-----------------------------------------+------------------------+------------------------------------------------+
| 17 June 2022 | 2.2.5               | * The ``Authlib`` library downgraded    | Flask App Builder      | https://github.com/apache/airflow/pull/24516   |
|              |                     |   from 1.0.1 to 0.15.5 version          | not compatible with    |                                                |
|              | 2.3.0-2.3.2         |                                         | Authlib >= 1.0.0       |                                                |
+--------------+---------------------+-----------------------------------------+------------------------+------------------------------------------------+
| 18 Jan 2022  | All 2.2.\*, 2.1.\*  | * The AIRFLOW_GID 500 was removed       | MySQL changed keys     | https://github.com/apache/airflow/pull/20912   |
|              |                     | * MySQL ``apt`` repository key changed. | to sign their packages |                                                |
|              |                     |                                         | on 17 Jan 2022         |                                                |
+--------------+---------------------+-----------------------------------------+------------------------+------------------------------------------------+
