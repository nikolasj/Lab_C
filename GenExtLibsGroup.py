#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Positive Technologies, 2016
# Author: DevOps

# This script generates a new project in Teamcity ExtLibs

import sys
import WorkflowExtlibsProject


def main(user_login, user_password):
    """
    In this method, set the parameters required for the generation of the project.
    Parameters are passed in WorkflowExtlibsProject.main.
    Note: All projects except the new must be commented out.
    """

    data = [

        # package name => git repo

        # ( 'libtelnet',     'git@gitlab.ptsecurity.ru:extlibs/libtelnet.git',  ),
        # ( 'zlib',          'git@gitlab.ptsecurity.ru:extlibs/zlib.git',       ),
        # ( 'curlpp',        'git@gitlab.ptsecurity.ru:extlibs/curlpp-lib.git', ),
        # ( 'python-cython', 'git@gitlab.ptsecurity.ru:extlibs/cython.git',     ),
        # ( 'redis',         'git@gitlab.ptsecurity.ru:extlibs/redis.git',      ),
        # ( 're2c',          'git@gitlab.ptsecurity.ru:extlibs/re2c.git',       ),
        # ( 'libssh2',       'git@gitlab.ptsecurity.ru:extlibs/libssh2.git',    ),
        # ( 'postgres',      'git@gitlab.ptsecurity.ru:extlibs/postgres.git',   ),
        # ( 'libvirt',       'git@gitlab.ptsecurity.ru:extlibs/libvirt.git',    ),
        # ( 'libgit2',       'git@gitlab.ptsecurity.ru:extlibs/libgit2.git',    ),
        # ( 'libbson',       'git@gitlab.ptsecurity.ru:extlibs/libbson.git',    ),
        # ( 'casablanca',    'git@gitlab.ptsecurity.ru:extlibs/casablanca.git', ),
        # ( 'soci',          'git@gitlab.ptsecurity.ru:extlibs/soci.git',       ),
        # ( 'opencv',        'git@gitlab.ptsecurity.ru:extlibs/opencv.git',     ),
        # ( 'wireshark',     'git@gitlab.ptsecurity.ru:extlibs/wireshark.git',  ),
        # ( 'ejdb',          'git@gitlab.ptsecurity.ru:extlibs/ejdb.git',       ),
        # ( 'hyperscan',     'git@gitlab.ptsecurity.ru:extlibs/HyperScan.git',  ),
        # ( 'ctpp',          'git@gitlab.ptsecurity.ru:extlibs/ctpp.git',       ),
        # ( 'gcc-mirror',    'git@gitlab.ptsecurity.ru:extlibs/gcc-mirror.git', ),
        # ( 'cdifflib',      'git@gitlab.ptsecurity.ru:extlibs/cdifflib.git',   ),
        # ( 'pycurl',        'git@gitlab.ptsecurity.ru:extlibs/pycurl.git',     ),
        # ( 'googlev8',      'git@gitlab.ptsecurity.ru:extlibs/googlev8.git',   ),
        # ( 'PyV8',          'git@gitlab.ptsecurity.ru:extlibs/PyV8.git',       ),
        # ( 'binpac',        'git@gitlab.ptsecurity.ru:extlibs/binpac.git',     ),
        # ( 'gsl',           'git@gitlab.ptsecurity.ru:extlibs/GSL.git',        ),
        # ( 'gsl-lite',      'git@gitlab.ptsecurity.ru:extlibs/gsl-lite.git',   ),
        # ( 'llvm',          'git@gitlab.ptsecurity.ru:extlibs/llvm.git',       ),
        # ( 'LuaBridge',     'git@gitlab.ptsecurity.ru:extlibs/LuaBridge.git',  ),
        # ( 'LuaJIT',        'git@gitlab.ptsecurity.ru:extlibs/luajit-2.0.git', ),
        # ( 'fmtlib',        'git@gitlab.ptsecurity.ru:extlibs/fmtlib.git',     ),
    ]


    for item in data:

        WorkflowExtlibsProject.main(
            'https://teamcity.ptsecurity.ru', # teamcity server url
            item[ 0 ],                        # project name
            item[ 1 ],                        # vcs git url
            user_login,                       # domain login
            user_password,                    # domain passwd
        )

if __name__ == '__main__':

    main(
        sys.argv[ 1 ], # user login
        sys.argv[ 2 ], # user passwd
    )