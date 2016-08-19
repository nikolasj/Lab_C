#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import apigen


def add_linux_compiller(conf_dict, step_name, current_docker_image='%docker_image%', current_platform_toolset='gcc-4.9',
                        current_target_architecture='x86_64'):
    data_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <step name="{step_name}" type="PtRunnerExtLibsLinuxBuild_2_0">
        <properties count="5">
            <property name="current_docker_image" value="{current_docker_image}"/>
            <property name="current_non_ci_build" value="%non_ci_build%"/>
            <property name="current_platform_toolset" value="{current_platform_toolset}"/>
            <property name="current_target_architecture" value="{current_target_architecture}"/>
            <property name="teamcity.step.mode" value="default"/>
        </properties>
    </step>
    '''.format(**locals())

    apigen.add_build_step(conf_dict, 'PtRunnerExtLibsLinuxBuild_2_0', data_xml, )

# current_target_archetecture можно поменять на x86_64 step_name = visual studio 2012,2013
def add_windows_compiller(conf_dict, step_name, current_platform_toolset='vc110', current_target_architecture='x86',
                          current_target_os='win'):
    data_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <step name="{step_name}" type="PtRunnerExtLibsWindowsBuild">
        <properties count="5">
            <property name="current_non_ci_build" value="%non_ci_build%"/>
            <property name="current_platform_toolset" value="{current_platform_toolset}"/>
            <property name="current_target_architecture" value="{current_target_architecture}"/>
            <property name="current_target_os" value="{current_target_os}"/>
            <property name="teamcity.step.mode" value="default"/>
        </properties>
    </step>
    '''.format(**locals())

    apigen.add_build_step(conf_dict, 'PtRunnerExtLibsWindowsBuild', data_xml, )  # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/steps


def get_data_dicts(project_name, git_url, parent_id):
    """
    This function is used to generate the data dictionary, to be used in the API
    :param project_name:
    :param git_url:
    :param parent_id:
    :return:
    """
    project_root = {
        'parent_id': parent_id, # ExtLibs
        'project_id': apigen.get_object_id(project_name, parent_id), # ExtLibs_Luabridge
        'project_name': project_name, # LuaBridge
        'project_desc': '{} configurations group'.format(project_name),
    }

    project_builds = {
        'parent_id': project_root['project_id'], # ExtLibs_Luabridge
        'project_id': apigen.get_object_id('Builds', project_root['project_id']),# ExtLibs_Luabridge_Builds
        'project_name': 'Builds',
        'project_desc': 'Only build configurations must be here',
    }

    vcs_root = {
        'parent_id': parent_id,  # ExtLibs
        'project_id': project_root['project_id'],  # ExtLibs_Luabridge
        'project_name': project_root['project_name'],  # LuaBridge
        'vcs_id': apigen.get_object_id(project_root['project_name'], project_root['project_id']),  # ExtLibs_Luabridge_Luabridge
        'vcs_name': project_root['project_name'],  # LuaBridge
        'git_url': git_url,  # git@gitlab.ptsecurity.ru:extlibs/LuaBridge.git
        'deploy_key': 'server-ci-03.deploy.rsa',
        'branch': 'master',
        'branch_spec': 'refs/heads/(*)',
    }

    conf_devops_checkout = {
        'project_id': 'DevOpsTools',
        'conf_id': 'DevOpsTools_DevOpsToolsCheckOut',
        'conf_short_name': 'devops',
        'conf_name': 'DevOpsTools',
        'conf_desc': 'DevOpsTools',
        'template_id': '',
    }

    conf_crossbuild = {
        'project_id': project_root['project_id'],# ExtLibs_Luabridge
        'conf_id': None,#? ExtLibs_Luabridge_Cross после generate_conf_id
        'conf_short_name': 'cross',
        'conf_name': 'CrossBuild',
        'conf_desc': 'CrossBuild',
        'template_id': 'ExtLibs_CrossBuild',
    }

    apigen.generate_conf_id(conf_crossbuild)

    conf_builds_win = {
        'project_id': project_builds['project_id'], # ExtLibs_Luabridge
        'conf_id': None,#? ExtLibs_Luabridge_Win после generate_conf_id
        'conf_short_name': 'win',
        'conf_name': 'Build Windows',
        'conf_desc': 'Build Windows',
        'template_id': 'ExtLibs_WinCrossBuild',
    }

    apigen.generate_conf_id(conf_builds_win)

    conf_builds_linux = {
        'project_id': project_builds['project_id'],
        'conf_id': None,#? ExtLibs_Luabridge_Nix после generate_conf_id
        'conf_short_name': 'nix',
        'conf_name': 'Build Linux',
        'conf_desc': 'Build Linux',
        'template_id': 'ExtLibs_LinuxCrossBuild',
    }

    apigen.generate_conf_id(conf_builds_linux)

    return (
        project_root,
        project_builds,
        vcs_root,
        conf_devops_checkout,
        conf_crossbuild,
        conf_builds_win,
        conf_builds_linux,
    )


def main(tc_url, project_name, git_url, login, passwd, parent_id='ExtLibs', custom_checkout_dir=False):
    """

    :param tc_url:
    :param project_name:
    :param git_url:
    :param login:
    :param passwd:
    :param parent_id:
    :param custom_checkout_dir:
    :return:
    """

    # Installing tc_url, login, passwd globally for apigen_1_0.py
    apigen.set_teamcity(tc_url, login, passwd, )

    (
        project_root,
        project_builds,
        vcs_root,
        conf_devops_checkout,
        conf_crossbuild,
        conf_builds_win,
        conf_builds_linux,
    ) = get_data_dicts(project_name, git_url, parent_id)

    # Add project
    apigen.add_project(project_root)  # добавляем проект https://teamcity.ptsecurity.ru/httpAuth/app/rest/projects
    apigen.project_setParameter(project_root, 'projectname', project_root['project_name'])  # устанавливаем projectname=LuaBridge
    apigen.add_vsc_root(vcs_root)  # добавляем vcs_root https://teamcity.ptsecurity.ru/httpAuth/app/rest/vcs-roots
    apigen.add_project(project_builds)  # добавляем билды https://teamcity.ptsecurity.ru/httpAuth/app/rest/projects

    # Add CrossBuild configuration
    apigen.add_configuration(conf_crossbuild)  # добавляем  конфигурацию https://teamcity.ptsecurity.ru/httpAuth/app/rest/projects/ExtLibs_Luabridge/buildTypes
    apigen.configuration_attach_template(conf_crossbuild)  # прикрепляем CrossBuild https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Cross/template
    apigen.configuration_attach_vcs(conf_crossbuild, vcs_root) # прикрепляем vcs https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Cross/vcs-root-entries
    apigen.configuration_setValue(conf_crossbuild, 'settings', 'buildNumberCounter', '100')  # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/settings/buildNumberCounter

    if custom_checkout_dir:
        apigen.configuration_setValue(conf_crossbuild, 'settings', 'checkoutDirectory', conf_crossbuild['conf_id'])

    # Add Build Windows
    apigen.add_configuration(conf_builds_win)  # добавляем  конфигурацию https://teamcity.ptsecurity.ru/httpAuth/app/rest/projects/ExtLibs_Luabridge/buildTypes
    apigen.configuration_attach_template(conf_builds_win) # прикрепляем  ExtLibs_WinCrossBuild https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Win/template
    apigen.configuration_attach_vcs(conf_builds_win, vcs_root, '+:. => %source_dir%') # прикрепляем vcs https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Win/vcs-root-entries
    apigen.configuration_setValue(conf_builds_win, 'parameters', 'crossbuild_runner_id', conf_crossbuild['conf_id']) # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Win/parameters/ExtLibs_Luabridge_Cross
    add_windows_compiller(conf_builds_win, 'visual studio 2012', current_platform_toolset='vc110')
    add_windows_compiller(conf_builds_win, 'visual studio 2013', current_platform_toolset='vc120')

    # Add Build Linux
    apigen.add_configuration(conf_builds_linux)  # добавляем  конфигурацию https://teamcity.ptsecurity.ru/httpAuth/app/rest/projects/ExtLibs_Luabridge/buildTypes
    apigen.configuration_attach_template(conf_builds_linux)  # прикрепляем  ExtLibs_WinCrossBuild https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Nix/template
    apigen.configuration_attach_vcs(conf_builds_linux, vcs_root)  # прикрепляем vcs https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Nix/vcs-root-entries
    apigen.configuration_setValue(conf_builds_linux, 'parameters', 'crossbuild_runner_id', conf_crossbuild['conf_id']) # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Win/parameters/ExtLibs_Luabridge_Cross
    add_linux_compiller(conf_builds_linux, 'GCC 4.9', current_platform_toolset='gcc-4.9')

    apigen.configuration_addSnapshotDependencies(conf_crossbuild, conf_builds_win, 'MAKE_FAILED_TO_START',
                                                 'MAKE_FAILED_TO_START', False, False, False)
    apigen.configuration_addSnapshotDependencies(conf_crossbuild, conf_builds_linux, 'MAKE_FAILED_TO_START',
                                                 'MAKE_FAILED_TO_START', False, False, False)


if __name__ == '__main__':
    main(
        sys.argv[1],  # teamcity server url, i.e. "https://teamcity.ptsecurity.ru"
        sys.argv[2],  # project name, i.e. "zlib"
        sys.argv[3],  # vcs git url, i.e. "git@gitlab.ptsecurity.ru:extlibs/zlib.git"
        sys.argv[4],  # user login
        sys.argv[5],  # user passwd
    )

