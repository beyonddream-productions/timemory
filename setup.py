#!/usr/bin/env python

import os
import re
import sys
import sysconfig
import platform
import subprocess

from distutils.version import LooseVersion
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools import Command
from setuptools.command.test import test as TestCommand


# ---------------------------------------------------------------------------- #
class CMakeExtension(Extension):

    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


# ---------------------------------------------------------------------------- #
class CMakeBuild(build_ext, Command):

    cmake_version = '2.7.12'
    build_type = 'Release'
    use_mpi = 'ON'
    timemory_exceptions = 'OFF'
    build_examples = 'ON'
    cxx_standard = 11
    mpicc = ''
    mpicxx = ''
    cmake_prefix_path = ''
    cmake_include_path = ''
    cmake_library_path = ''

    def init_cmake(self):
        """
        Ensure cmake is in PATH
        """
        try:
            out = subprocess.check_output(['cmake', '--version'])
            CMakeBuild.cmake_version = LooseVersion(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1))
        except OSError:
            # if fail, try the module
            import cmake
            try:
                if not cmake.CMAKE_BIN_DIR in sys.path:
                    sys.path.append(cmake.CMAKE_BIN_DIR)
                if platform.system() != "Windows":
                    curr_path = os.environ['PATH']
                    if not cmake.CMAKE_BIN_DIR in curr_path:
                        os.environ['PATH'] = "{}:{}".format(curr_path, cmake.CMAKE_BIN_DIR)

                CMakeBuild.cmake_version = cmake.sys.version.split(' ')[0]
            except:
                print ('Error putting cmake in path')
                raise RuntimeError(
                    "CMake must be installed to build the following extensions: " +
                        ", ".join(e.name for e in self.extensions))


    # run
    def run(self):
        self.init_cmake()

        if CMakeBuild.cmake_version < '3.1.3':
            raise RuntimeError("CMake >= 3.1.3 is required")

        print ('Using CMake version {}...'.format(CMakeBuild.cmake_version))

        for ext in self.extensions:
            self.build_extension(ext)


    # build extension
    def build_extension(self, ext):
        self.init_cmake()

        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DPYTHON_EXECUTABLE=' + sys.executable,
                      '-DSETUP_PY=ON',
                      '-DCMAKE_INSTALL_PREFIX=' + extdir,
                      ]

        _valid_type = False
        for _type in [ 'Release', 'Debug', 'RelWithDebInfo', 'MinSizeRel' ]:
            if _type == self.build_type:
                _valid_type = True
                break

        if not _valid_type:
            self.build_type = 'Release'

        cmake_args += [ '-DCMAKE_BUILD_TYPE={}'.format(self.build_type) ]
        cmake_args += [ '-DUSE_MPI={}'.format(str.upper(self.use_mpi)) ]

        if platform.system() != "Windows":
            cmake_args += [ '-DBUILD_EXAMPLES={}'.format(str.upper(self.build_examples)) ]

        _cxxstd = int(self.cxx_standard)
        if _cxxstd < 14 and platform.system() != "Windows":
            _cxxstd = 14

        if _cxxstd == 11 or _cxxstd == 14 or _cxxstd == 17:
            cmake_args += [ '-DCMAKE_CXX_STANDARD={}'.format(self.cxx_standard) ]

        def valid_string(_str):
            if len(_str) > 0 and _str != '""' and _str != "''":
                return True

        if valid_string(self.mpicc):
            cmake_args += [ '-DMPI_C_COMPILER={}'.format(self.mpicc) ]

        if valid_string(self.mpicxx):
            cmake_args += [ '-DMPI_CXX_COMPILER={}'.format(self.mpicxx) ]

        if valid_string(self.cmake_prefix_path):
            cmake_args += [ '-DCMAKE_PREFIX_PATH={}'.format(self.cmake_prefix_path) ]

        if valid_string(self.cmake_library_path):
            cmake_args += [ '-DCMAKE_LIBRARY_PATH={}'.format(self.cmake_library_path) ]

        if valid_string(self.cmake_include_path):
            cmake_args += [ '-DCMAKE_INCLUDE_PATH={}'.format(self.cmake_include_path) ]

        cmake_args += [ '-DTIMEMORY_EXCEPTIONS={}'.format(str.upper(self.timemory_exceptions)) ]

        build_args = [ '--config', self.build_type ]
        install_args = [ '--config', self.build_type ]
        if platform.system() == "Windows":
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--target', 'ALL_BUILD', '--', '/m' ]
            install_args += ['--target', 'INSTALL', '--', '/m' ]
        else:
            build_args += [ '--', '-j4' ]
            install_args += [ '--target', 'install' ]

        env = os.environ.copy()
        env['CXXFLAGS'] = '{}'.format(
            env.get('CXXFLAGS', ''))

        # make directory if not exist
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # set to absolute path
        self.build_temp=os.path.abspath(self.build_temp)

        # print the CMake args
        print('CMake args: {}'.format(cmake_args))
        # print the build_args
        print('Build args: {}'.format(build_args))
        # print the install args
        print('Install args: {}'.format(install_args))

        # configure the project
        subprocess.check_call(['cmake'] + cmake_args + [ ext.sourcedir ],
                              cwd=self.build_temp, env=env)

        # build the project
        subprocess.check_call(['cmake', '--build', self.build_temp] + build_args,
                              cwd=self.build_temp, env=env)

        # install the CMake build
        subprocess.check_call(['cmake', '--build', self.build_temp] + install_args,
                              cwd=self.build_temp, env=env)

        print()  # Add an empty line for cleaner output


# ---------------------------------------------------------------------------- #
class CatchTestCommand(TestCommand):
    """
    A custom test runner to execute both Python unittest tests and C++ Catch-
    lib tests.
    """

    cmake_version = '2.7.12'

    def init_cmake(self):
        """
        Ensure cmake is in PATH
        """
        try:
            out = subprocess.check_output(['cmake', '--version'])

        except OSError:
            # if fail, try the module
            import cmake
            try:
                if not cmake.CMAKE_BIN_DIR in sys.path:
                    sys.path.append(cmake.CMAKE_BIN_DIR)
                if platform.system() != "Windows":
                    curr_path = os.environ['PATH']
                    if not cmake.CMAKE_BIN_DIR in curr_path:
                        os.environ['PATH'] = "{}:{}".format(curr_path, cmake.CMAKE_BIN_DIR)

            except:
                print ('Error putting cmake in path')
                raise RuntimeError(
                    "CMake must be installed to test the following extensions: " +
                        ", ".join(e.name for e in self.extensions))


    def distutils_dir_name(self, dname):
        """Returns the name of a distutils build directory"""
        dir_name = "{dirname}.{platform}-{version[0]}.{version[1]}"
        return dir_name.format(dirname=dname,
                               platform=sysconfig.get_platform(),
                               version=sys.version_info)

    def run(self):
        import cmake
        self.init_cmake()
        print("\nRunning CMake/CTest tests...\n")
        # Run catch tests
        subprocess.check_call(['ctest', '--output-on-failure' ],
                cwd=os.path.join('build', self.distutils_dir_name('temp')))


# ---------------------------------------------------------------------------- #
def get_long_description():
    long_descript = ''
    try:
        long_descript = open('README.rst').read()
    except:
        long_descript = ''
    return long_descript


# ---------------------------------------------------------------------------- #
def get_short_description():
    brief_A = 'Python timing (wall, system, user, cpu, %cpu) + RSS memory (current, peak) measurement manager'
    brief_B = 'Written in high-perf C++ and made available to Python via PyBind11'
    return '{}. {}.'.format(brief_A, brief_B)


# ---------------------------------------------------------------------------- #
def get_keywords():
    return [ 'timing', 'memory', 'auto-timers', 'signal', 'c++', 'cxx', 'rss',
             'resident set size', 'cpu time', 'cpu utilization', 'wall clock',
             'system clock', 'user clock', 'pybind11' ]


# ---------------------------------------------------------------------------- #
def get_classifiers():
    return [
        # no longer beta
        'Development Status :: 5 - Production/Stable',
        # performance monitoring
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        # can be used for all of below
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
        # written in English
        'Natural Language :: English',
        # MIT license
        'License :: OSI Approved :: MIT License',
        # tested on these OSes
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',
        # written in C++, available to Python via PyBind11
        'Programming Language :: C++',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]


# ---------------------------------------------------------------------------- #
def get_name():
    return 'Jonathan R. Madsen'

# ---------------------------------------------------------------------------- #
def get_email():
    return 'jonrobm.programming@gmail.com'


# ---------------------------------------------------------------------------- #
# calls the setup and declare our 'my_cool_package'
setup(name='TiMemory',
    version='1.1.1',
    author=get_name(),
    author_email=get_email(),
    maintainer=get_name(),
    maintainer_email=get_email(),
    contact=get_name(),
    contact_email=get_email(),
    description=get_short_description(),
    long_description=get_long_description(),
    url='https://github.com/jrmadsen/TiMemory.git',
    license='MIT',
    # add extension module
    ext_modules=[CMakeExtension('timemory')],
    # add custom build_ext command
    cmdclass=dict(build_ext=CMakeBuild, test=CatchTestCommand),
    zip_safe=False,
    # extra
    install_requires=[ 'numpy', 'matplotlib', 'cmake' ],
    setup_requires=[ 'cmake', 'setuptools', 'disttools' ],
    provides=[ 'timemory' ],
    keywords=get_keywords(),
    classifiers=get_classifiers(),
    python_requires='>=2.6',
)
