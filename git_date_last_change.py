#!/usr/bin/env python
# Script to clone all the github repos that a user is watching

import subprocess
import sys
import GitChange

def main(user_login, user_password):

    data = [

        ('LuaBridge', '@gitlab.ptsecurity.ru/extlibs/LuaBridge.git',  'master'),
        # ('luajit-2.0','@gitlab.ptsecurity.ru/extlibs/luajit-2.0.git', 'https://github.com/LuaDist/luajit.git master'       ),
        ]

    for item in data:
        GitChange.last_changed(
            item[0],
            item[1],
            item[2],
            user_login,
            user_password,
        )

    # for item in data:
    #     GitChange.date_file(
    #         item[0],
    #     )

if __name__ == '__main__':
    main(
        sys.argv[ 1 ], # user login
        sys.argv[ 2 ], # user passwd
    )
