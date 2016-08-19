#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) Positive Technologies, 2016
# Author: Nikolay Yusev

# Script to clone all the github repos that a user is watching

import subprocess
import sys
import GitChange

def main(user_login, user_password):

    data = [
        # ('ProjectName', 'gitlaburl', 'branch'),
        ('LuaBridge',     '@gitlab.ptsecurity.ru/extlibs/LuaBridge.git',     'master',    'https://github.com/vinniefalco/LuaBridge.git',    'master'),
        ('luajit-2.0',    '@gitlab.ptsecurity.ru/extlibs/luajit-2.0.git',    'master',    'https://github.com/LuaDist/luajit.git master',    'master'),
        ('zlib',          '@gitlab.ptsecurity.ru/extlibs/zlib.git',          'master',    'https://github.com/madler/zlib.git',              'master'),
        ('test_project',  '@gitlab.ptsecurity.ru/nyusev/test_project.git',   'master',    'https://github.com/nikolasj/test_project.git',    'master'),
        ]

    for item in data:
        GitChange.last_changed(
            item[0],
            item[1],
            item[2],
            item[3],
            item[4],
            user_login,
            user_password,
        )

if __name__ == '__main__':
    main(
        sys.argv[ 1 ], # user login
        sys.argv[ 2 ], # user passwd
    )

