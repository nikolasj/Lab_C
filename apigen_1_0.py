# -*- coding: utf-8 -*-

#
# (c) Positive Technologies, 2015

import sys
import re
import time
import xml.etree.ElementTree

import requests

# TODO: fix it
# requests.packages.urllib3.disable_warnings()

OPT_LOGIN = None
OPT_PASS = None
OPT_TC_URL = None
OPT_DEFAULT_DELAY_SEC = None

PARAMSPEC_HIDEN_ANY = '''<type rawValue="text display='hidden' validationMode='any'"/>'''
PARAMSPEC_HIDEN_NOT_EMPTY = '''<type rawValue="text display='hidden' validationMode='not_empty'"/>'''


# SOME INFO:
#
# for custom checkout dir use next code:
#
#    apigen.configuration_setValue( conf_builds_develop_crossbuild, 'settings', 'checkoutDirectory', conf_builds_develop_crossbuild[ 'conf_id' ] )
#


def _replace_newline_codes(value):
    return value.replace('\r', '&#xD;').replace('\n', '&#xA;')


def _replace_cdata_field(value):
    result = value
    patterns = [
        ('\r', '&#xD;',),
        ('\n', '&#xA;',),
        ('"', '&quot;',),
    ]

    for item in patterns:
        result = result.replace(item[0], item[1])

    return result


def set_teamcity(tc_url, login, passwd):
    global OPT_LOGIN, OPT_PASS, OPT_TC_URL, OPT_DEFAULT_DELAY_SEC
# устанавливаем глобально логин, пароль, тимсити урл
    OPT_LOGIN = login
    OPT_PASS = passwd
    OPT_TC_URL = tc_url
    OPT_DEFAULT_DELAY_SEC = 2


def rest_delay():
    time.sleep(OPT_DEFAULT_DELAY_SEC) # заснуть на 2 сек


def get_object_id(object_name, parent_id=''):
    object_name = re.sub('[^A-Za-z0-9]', '', object_name) # правила для множества строк. Соответствует ли эта страка шаблону [^A-Za-z0-9], если нет заменяет на ''

    if object_name and ('_Root' == parent_id):
        parent_id = ''

    if not object_name:
        object_name = 'id'

    return '{}{}{}'.format(
        parent_id,
        '_' if parent_id else '',
        object_name[0].upper() + object_name[1:].lower(),
    ) #ExtLibs_Luabridge


def generate_project_id(data_dict, short_name=None):
    value = get_object_id(
        data_dict['project_name'] if short_name is None  else short_name,
        data_dict['parent_id'],
    )

    data_dict['project_id'] = value

    return value


def generate_vcs_id(data_dict, short_name=None):
    value = get_object_id(
        data_dict['vcs_name'] if short_name is None  else short_name,
        data_dict['project_id'],  # really here we use "project_id" and not "parent_id"
    )

    data_dict['vcs_id'] = value

    return value


def generate_template_id(data_dict):
    value = get_object_id(
        data_dict['template_short_name'],
        data_dict['project_id'],
    )

    data_dict['template_id'] = value

    return value


def generate_conf_id(data_dict): # conf_crossbuild
    value = get_object_id(
        data_dict['conf_short_name'], # 'cross'
        data_dict['project_id'], # ExtLibs_Luabridge
    )

    data_dict['conf_id'] = value #? ExtLibs_Luabridge_Cross

    return value # ExtLibs_Luabridge_Cross


def add_auth_to_url(url_str, login_str, pass_str):
    i = url_str.find('//')

    if i == -1:
        raise Exception("Can't detect http(s):// part of url: {}".format(url_str))

    return '{}//{}:{}@{}'.format(
        url_str[: i],
        login_str,
        pass_str,
        url_str[i + 2:],
    ) # https://nyusev:password@teamcity.ptsecurity.ru/httpAuth/app/rest/projects'


def add_vsc_root(data_dict):
    print('add vcs-root [{vcs_name}]'.format(**data_dict)) # LuaBridge

    data_xml = '''<vcs-root id="{vcs_id}" name="{vcs_name}" vcsName="jetbrains.git" status="FINISHED" lastChecked="0" href="/httpAuth/app/rest/vcs-roots/id:{vcs_id}">
    <project id="{project_id}" name="{project_name}" parentProjectId="{parent_id}" href="/httpAuth/app/rest/projects/id:{project_id}" webUrl="https://teamcity.ptsecurity.ru/project.html?projectId={project_id}"/>
    <properties>
        <property name="agentCleanFilesPolicy" value="ALL_UNTRACKED"/>
        <property name="agentCleanPolicy" value="ON_BRANCH_CHANGE"/>
        <property name="authMethod" value="TEAMCITY_SSH_KEY"/>
        <property name="branch" value="{branch}"/>
        <property name="ignoreKnownHosts" value="true"/>
        <property name="submoduleCheckout" value="CHECKOUT"/>
        <property name="teamcity:branchSpec" value="{branch_spec}"/>
        <property name="teamcitySshKey" value="{deploy_key}"/>
        <property name="url" value="{git_url}"/>
        <property name="usernameStyle" value="USERID"/>
    </properties>
    <vcsRootInstances href="/httpAuth/app/rest/vcs-root-instances?locator=vcsRoot:(id:{vcs_id})"/>
</vcs-root>'''.format(**data_dict)

    rest_delay() # sleep 2 sec

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/vcs-roots', OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    try:

        r.raise_for_status()

    except Exception as e:
        print(e)
        print(r.text)
        sys.exit(1)


def vsc_root_exists(data_dict):
    print('check vsc_root exists [{vcs_name}]'.format(**data_dict))

    result = True

    # rest_delay()

    r = requests.get(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/vcs-roots/{vcs_id}'.format(**data_dict), OPT_LOGIN, OPT_PASS),
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    if 404 == r.status_code:

        result = False

    else:

        r.raise_for_status()

    return result


def copy_project(data_dict):
    print('copy project [{project_name}] from [{copy_from_project_id}]'.format(**data_dict))

    data_xml = '''<newProjectDescription name='{project_name}' id='{project_id}' copyAllAssociatedSettings='true'>
    <parentProject locator='id:{parent_id}'/>
    <sourceProject locator='id:{copy_from_project_id}'/>
</newProjectDescription>'''.format(**data_dict)

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects', OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def add_project(data_dict):
    print('add project [{project_name}]'.format(**data_dict)) #? add project [LuaBridge] | [Builds]

    data_xml = '''<newProjectDescription name='{project_name}' id='{project_id}' copyAllAssociatedSettings='true'>
    <parentProject locator='id:{parent_id}'/>
</newProjectDescription>'''.format(**data_dict) # LuaBridge  ExtLibs_Luabridge ExtLibs | Builds  ExtLibs_Luabridge_Builds  ExtLibs_Luabridge

    rest_delay() # sleep 2 sec

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects', OPT_LOGIN, OPT_PASS), # https://nyusev:password@teamcity.ptsecurity.ru/httpAuth/app/rest/projects'
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status() # проверка успешности запроса

    if 'project_desc' in data_dict: # если есть project_desc добавляется project_desctiption
        project_setDescription(data_dict, data_dict['project_desc'])


def project_exists(data_dict):
    print('check project exists [{project_name}]'.format(**data_dict))

    result = True

    r = requests.get(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects/{project_id}'.format(**data_dict), OPT_LOGIN,
                        OPT_PASS),
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    if 404 == r.status_code:

        result = False

    else:

        r.raise_for_status()

    return result


def add_template(data_dict):
    print('add template [{template_name}]'.format(**data_dict))

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects/{project_id}/templates'.format(**data_dict),
                        OPT_LOGIN, OPT_PASS),
        data=data_dict['template_short_name'],
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()

    template_setId(data_dict, data_dict['template_id'])

    template_setName(data_dict, data_dict['template_name'])


def template_exists(data_dict):
    print('check template exists [{template_name}]'.format(**data_dict))

    result = True

    # rest_delay()

    r = requests.get(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/projects/{project_id}/templates/id:{template_id}'.format(**data_dict),
            OPT_LOGIN, OPT_PASS),
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    if 404 == r.status_code:

        result = False

    else:

        r.raise_for_status()

    return result


def configuration_exists(data_dict):
    print('check configuration exists [{conf_name}]'.format(**data_dict))

    result = True

    # rest_delay()

    r = requests.get(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/projects/{project_id}/buildTypes/id:{conf_id}'.format(**data_dict),
            OPT_LOGIN, OPT_PASS),
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    if 404 == r.status_code:

        result = False

    else:

        r.raise_for_status()

    return result


def add_configuration(conf_dict):
    print('add configuration [{conf_name}]'.format(**conf_dict))# CrossBuild | Build Windows

    rest_delay()# sleep 2 sec

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects/{project_id}/buildTypes'.format(**conf_dict), # ExtLibs_Luabridge https://teamcity.ptsecurity.ru/httpAuth/app/rest/projects/ExtLibs_Luabridge/buildTypes |https://teamcity.ptsecurity.ru/httpAuth/app/rest/projects/ExtLibs_Luabridge/buildTypes
                        OPT_LOGIN, OPT_PASS),
        data=conf_dict['conf_short_name'],# cross
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()

    configuration_setId(conf_dict, conf_dict['conf_id']) # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/id | # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Win/id

    configuration_setName(conf_dict, conf_dict['conf_name'])  # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/name | # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Win/name
    configuration_setDescription(conf_dict, conf_dict['conf_desc'])  # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/description | https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Win/description


def copy_configuration(conf_dict):
    data_xml = '''<newBuildTypeDescription name='{conf_name}' sourceBuildTypeLocator='id:{copy_from_conf_id}' copyAllAssociatedSettings='true' shareVCSRoots='false'/>'''.format(
        **conf_dict)

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects/{project_id}/buildTypes'.format(**conf_dict),
                        OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def configuration_setParameterSpec(data_dict, var_name, value, spec):
    print('project [{}] set parameter (with spec) [{}] = value [{!r}]'.format(
        data_dict['conf_id'],
        var_name,
        value,
    ))

    data_xml = '''<property name="{var_name}" value="{value}" own="true">{spec}</property>'''.format(
        **locals()
    )

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/app/rest/buildTypes/id:{conf_id}/parameters/'.format(**data_dict), OPT_LOGIN,
                        OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def template_attach_vcs(template_dict, data_dict, checkout_rules=''):
    print('template [{}] attach vcs [{}]'.format(
        template_dict['template_name'],
        data_dict['vcs_name'],
    ))

    current_data_dict = dict(data_dict)
    current_data_dict.update({
        'checkout_rules': _replace_newline_codes(checkout_rules),
    })

    data_xml = '''<vcs-root-entry id="{vcs_id}">
    <vcs-root id="{vcs_id}" name="{vcs_name}" href="/httpAuth/app/rest/vcs-roots/id:{vcs_id}"/>
    <checkout-rules>{checkout_rules}</checkout-rules>
</vcs-root-entry>'''.format(**current_data_dict)

    rest_delay()

    r = requests.post(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{template_id}/vcs-root-entries/'.format(**template_dict),
            OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def configuration_attach_vcs(conf_dict, data_dict, checkout_rules=''):
    print('configuration [{}] attach vcs [{}]'.format(
        conf_dict['conf_name'], # CrossBuild | Build Windows
        data_dict['vcs_name'],  # LuaBridge | LuaBridge | LuaBridge
    ))

    current_data_dict = dict(data_dict) #?
    current_data_dict.update({'checkout_rules': checkout_rules}) # | ?для Build Windows +:. => %source_dir%

    data_xml = '''<vcs-root-entry id="{vcs_id}">
    <vcs-root id="{vcs_id}" name="{vcs_name}" href="/httpAuth/app/rest/vcs-roots/id:{vcs_id}"/>
    <checkout-rules>{checkout_rules}</checkout-rules>
</vcs-root-entry>'''.format(**current_data_dict)  # ExtLibs_Luabridge_Luabridge  LuaBridge  +:. => %source_dir%

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{conf_id}/vcs-root-entries/'.format(**conf_dict),
                        OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )  # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Cross/vcs-root-entries https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Win/vcs-root-entries

    r.raise_for_status()


def configuration_attach_template(conf_dict):
    print('configuration [{conf_name}] attach template [{template_id}]'.format(**conf_dict))  # CrossBuild  ExtLibs_CrossBuild | Build Windows ExtLibs_WinCrossBuild

    rest_delay()

    r = requests.put(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{conf_id}/template'.format(**conf_dict), OPT_LOGIN,
                        OPT_PASS),
        data=conf_dict['template_id'],
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )  # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Cross/template | https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/ExtLibs_Luabridge_Win/template

    r.raise_for_status()


def project_parameter_exists(data_dict, var_name):
    print('project [{}] check parameter [{}] exists'.format(
        data_dict['project_id'],
        var_name,
    ))

    result = True
    r = requests.get(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/projects/{}/parameters/{}'.format(data_dict['project_id'], var_name),
            OPT_LOGIN, OPT_PASS),
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    if 404 == r.status_code:

        result = False

    else:

        r.raise_for_status()

    return result


def project_setParameter(data_dict, var_name, value): # ExtLibs, projectname, LuaBridge
    print('project [{}] set parameter [{}] = value [{!r}]'.format(
        data_dict['project_id'],
        var_name,
        value,
    ))

    rest_delay() # sleep 2 sec

    r = requests.put(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/projects/{}/parameters/{}'.format(data_dict['project_id'], var_name), # 'https://teamcity.ptsecurity.ru/httpAuth/app/rest/projects/ExtLibs/parameters/projectname '
            OPT_LOGIN, OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()


def project_setParameterSpec(data_dict, var_name, value, spec):
    print('project [{}] set parameter (with spec) [{}] = value [{!r}]'.format(
        data_dict['project_id'],
        var_name,
        value,
    ))

    data_xml = '''<property name="{var_name}" value="{value}" own="true">{spec}</property>'''.format(
        **locals()
    )

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects/{}/parameters/'.format(data_dict['project_id']),
                        OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def project_setName(data_dict, value):
    print('project [{}] set name [{}]'.format(
        data_dict['project_id'],
        value,
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects/{}/name'.format(data_dict['project_id']), OPT_LOGIN,
                        OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()


def project_setDescription(data_dict, value):
    print('project [{}] set description [{}]'.format(
        data_dict['project_id'],
        value,
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/projects/{}/description'.format(data_dict['project_id']),
                        OPT_LOGIN, OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()


def template_setId(conf_dict, value):
    print('template [{}] set id [{}]'.format(
        conf_dict['template_id'],
        value,
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/id'.format(conf_dict['template_id']),
                        OPT_LOGIN, OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()


def template_setName(conf_dict, value):
    print('template [{}] set name [{}]'.format(
        conf_dict['template_id'],
        value,
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/name'.format(conf_dict['template_id']),
                        OPT_LOGIN, OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()


def configuration_setId(conf_dict, value): # здесь можно поменять
    print('configuration [{}] set id [{}]'.format(
        conf_dict['conf_id'], #? ExtLibs_Luabridge_Cross | ExtLibs_Luabridge_Win
        value,#? ExtLibs_Luabridge_Cross | ExtLibs_Luabridge_Win
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/id'.format(conf_dict['conf_id']), OPT_LOGIN,
                        OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    ) # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/id

    r.raise_for_status()


def configuration_setName(conf_dict, value):
    print('configuration [{}] set name [{}]'.format(
        conf_dict['conf_id'],
        value,
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/name'.format(conf_dict['conf_id']), OPT_LOGIN,
                        OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )# https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/name

    r.raise_for_status()


def configuration_setDescription(conf_dict, value):
    print('configuration [{}] set description [{}]'.format(
        conf_dict['conf_id'],
        value,
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/description'.format(conf_dict['conf_id']),
                        OPT_LOGIN, OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    ) # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/description

    r.raise_for_status()


def template_setValue(data_dict, type_str, var_name, value):
    print('template [{}] set [{}] = value [{!r}]'.format(
        data_dict['template_name'],
        var_name,
        value,
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/{}/{}'.format(data_dict['template_id'], type_str,
                                                                            var_name), OPT_LOGIN, OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()


def template_setParameterSpec(data_dict, var_name, value, spec):
    print('template [{}] set parameter (with spec) [{}] = value [{!r}]'.format(
        data_dict['template_id'],
        var_name,
        value,
    ))

    data_xml = '''<property name="{var_name}" value="{value}" own="true">{spec}</property>'''.format(
        **locals()
    )

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/parameters/'.format(data_dict['template_id']),
                        OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def configuration_setValue(conf_dict, type_str, var_name, value):
    print('configuration [{}] set [{}] = value [{!r}]'.format(
        conf_dict['conf_name'],  # CrossBuild | Build Windows
        var_name,  # buildNumberCounter | crossbuild_runner_id
        value, # 100  | ExtLibs_Luabridge_Win
    ))

    rest_delay()

    r = requests.put(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/{}/{}'.format(conf_dict['conf_id'], type_str, var_name),
            OPT_LOGIN, OPT_PASS),
        data=value,
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )  # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/settings/buildNumberCounter | https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Win/parameters/crossbuild_runner_id

    r.raise_for_status()


def configuration_getValue(conf_dict, type_str, var_name):
    print(
        'configuration [{}] set [{}] = '.format(conf_dict['conf_id'], var_name),
        end='',
    )

    rest_delay()

    r = requests.put(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{}/{}/{}'.format(conf_dict['conf_id'], type_str, var_name),
            OPT_LOGIN, OPT_PASS),
        headers={'Content-Type': 'text/plain'},
        verify=False,
    )

    r.raise_for_status()

    value = r.text

    print('{!r}'.format(value))

    return value


def configuration_addSnapshotDependencies(conf_dict_a, conf_dict_b, run_if_failed='MAKE_FAILED_TO_START',
                                          run_if_start_failed='MAKE_FAILED_TO_START', run_on_same=False,
                                          take_started=False, take_successful=False):
    print('add snapshot-dependencies [{}]\n\t -> [{}]'.format(conf_dict_a['conf_id'], conf_dict_b['conf_id']))

    f_tostr = lambda x: 'true' if x else 'false'
    avalible_values = (
        'RUN_ADD_PROBLEM',
        'RUN',
        'MAKE_FAILED_TO_START',
        'CANCEL',
    )
    current_conf_dict_b = dict(conf_dict_b)
    current_conf_dict_b.update({
        'run_if_failed': run_if_failed.upper(),
        'run_if_start_failed': run_if_start_failed.upper(),
        'run_on_same': f_tostr(run_on_same),
        'take_started': f_tostr(take_started),
        'take_successful': f_tostr(take_successful),
    })

    if current_conf_dict_b['run_if_failed'] not in avalible_values:
        raise Exception(
            "ERROR: Unsupported value for key 'run_if_failed' [{}]".format(current_conf_dict_b['run_if_failed']))

    if current_conf_dict_b['run_if_start_failed'] not in avalible_values:
        raise Exception("ERROR: Unsupported value for key 'run_if_start_failed' [{}]".format(
            current_conf_dict_b['run_if_start_failed']))

    data_xml = '''<snapshot-dependency id="{conf_id}" type="snapshot_dependency">
    <properties>
        <property name="run-build-if-dependency-failed" value="{run_if_failed}"/>
        <property name="run-build-if-dependency-failed-to-start" value="{run_if_start_failed}"/>
        <property name="run-build-on-the-same-agent" value="{run_on_same}"/>
        <property name="take-started-build-with-same-revisions" value="{take_started}"/>
        <property name="take-successful-builds-only" value="{take_successful}"/>
    </properties>
    <source-buildType id="{conf_id}" name="{conf_name}" projectName="" projectId="{project_id}" href="/httpAuth/app/rest/buildTypes/id:{conf_id}" webUrl="https://teamcity.ptsecurity.ru/viewType.html?buildTypeId={conf_id}"/>
</snapshot-dependency>'''.format(**current_conf_dict_b)

    rest_delay()

    r = requests.post(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{conf_id}/snapshot-dependencies'.format(**conf_dict_a),
            OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def configuration_addArtifactDependencies(conf_dict_a, conf_dict_b, deps_id, path_rules, clean_dir):
    print('add artifact-dependencies [{}]\n\t -> [{}]'.format(conf_dict_a['conf_id'], conf_dict_b['conf_id']))

    f_tostr = lambda x: 'true' if x else 'false'
    current_conf_dict_b = dict(conf_dict_b)
    current_conf_dict_b.update({
        'deps_id': deps_id,
        'path_rules': path_rules,
        'clean_dir': f_tostr(clean_dir),
    })

    data_xml = '''<artifact-dependency id="{deps_id}" type="artifact_dependency">
    <properties count="4">
        <property name="cleanDestinationDirectory" value="{clean_dir}"/>
        <property name="pathRules" value="{path_rules}"/>
        <property name="revisionName" value="sameChainOrLastFinished"/>
        <property name="revisionValue" value="latest.sameChainOrLastFinished"/>
    </properties>
    <source-buildType id="{conf_id}" name="{conf_name}" description="" projectName="" projectId="{project_id}" href="/httpAuth/app/rest/buildTypes/id:{conf_id}" webUrl="https://teamcity.ptsecurity.ru/viewType.html?buildTypeId={conf_id}"/>
</artifact-dependency>'''.format(**current_conf_dict_b)

    rest_delay()

    r = requests.post(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{conf_id}/artifact-dependencies'.format(**conf_dict_a),
            OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


#
# quiet_period_mode - one of:
#   "DO_NOT_USE"
#   "USE_DEFAULT"
#   "USE_CUSTOM"
# quiet_period is not None only if quiet_period_mode is "USE_CUSTOM" and None other ways
# watch_changes_in_dependencies - Trigger a build on changes in snapshot dependencies
# per_checkin_triggering - Trigger a build on each check-in
# group_checkins_by_committer - Include several check-ins in a build if they are from the same committer. True only if
# branch_filter - use \r\n line separation
# trigger_rules - use \r\n line separation
def configuration_addVcsTrigger(conf_dict, quiet_period_mode, quiet_period, watch_changes_in_dependencies,
                                per_checkin_triggering, group_checkins_by_committer, branch_filter, trigger_rules):
    print('add vcs trigger to configuration [{}]'.format(
        conf_dict['conf_id'],
    ))

    branch_filter = _replace_newline_codes(branch_filter)
    trigger_rules = _replace_newline_codes(trigger_rules)
    extra_property_fields = ''
    avalible_values = (
        'DO_NOT_USE',
        'USE_DEFAULT',
        'USE_CUSTOM',
    )

    if quiet_period_mode not in avalible_values:
        raise Exception("ERROR: Unsupported value for key 'quiet_period_mode' [{}]".format(quiet_period_mode))

    if 'USE_CUSTOM' == quiet_period_mode:

        if quiet_period is None:
            raise Exception("ERROR: Unsupported value for key 'quiet_period' [{}]".format(quiet_period))

        extra_property_fields.append('\t\t<property name="quietPeriod" value="{}"/>\n'.format(quiet_period))

    elif quiet_period is not None:

        raise Exception(
            "ERROR: Unable to have value for key 'quiet_period' in quiet_period_mode=[{}]\n.".format(quiet_period_mode))

    if watch_changes_in_dependencies:
        extra_property_fields.append('\t\t<property name="watchChangesInDependencies" value="true"/>\n')

    if per_checkin_triggering:
        extra_property_fields.append('\t\t<property name="perCheckinTriggering" value="true"/>\n')

    if group_checkins_by_committer:

        if not per_checkin_triggering:
            raise Exception(
                "ERROR: Unable to set flag 'group_checkins_by_committer' if per_checkin_triggering=false\n.")

        extra_property_fields.append('\t\t<property name="groupCheckinsByCommitter" value="true"/>\n')

    data_xml = '''<trigger id="vcsTrigger" type="vcsTrigger">
    <properties count="3">
        <property name="branchFilter" value="{branch_filter}"/>
        <property name="quietPeriodMode" value="{quiet_period_mode}"/>
        <property name="triggerRules" value="{trigger_rules}"/>
        {extra_property_fields}
    </properties>
</trigger>'''.format(**locals())

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{conf_id}/triggers'.format(**conf_dict), OPT_LOGIN,
                        OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    try:

        r.raise_for_status()

    except Exception as e:
        print(e)
        print(r.text)
        sys.exit(1)


def configuration_getVcsTriggerRAW(conf_dict, out_filename):
    rest_delay()

    r = requests.get(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{conf_id}/triggers'.format(**conf_dict), OPT_LOGIN,
                        OPT_PASS),
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()

    with open(out_filename, 'wb') as fd:
        chunk_size = 1024
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)


def configuration_addFeatureVcsLabeling(conf_dict, data_dict, branch_filter, labeling_pattern):
    print("add build feature 'VcsLabeling' to configuration [{}]".format(
        conf_dict['conf_id'],
    ))

    current_data_dict = dict(data_dict)
    current_data_dict.update({
        'property_branch_filter': branch_filter,
        'property_labeling_pattern': labeling_pattern,
    })

    data_xml = '''<feature id="BUILD_EXT_4" type="VcsLabeling">
    <properties count="4">
        <property name="branchFilter" value="{property_branch_filter}"/>
        <property name="labelingPattern" value="{property_labeling_pattern}"/>
        <property name="successfulOnly" value="true"/>
        <property name="vcsRootId" value="{vcs_id}"/>
    </properties>
    </feature>'''.format(**current_data_dict)

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{conf_id}/features'.format(**conf_dict), OPT_LOGIN,
                        OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def configuration_addFeatureFreeDiskSpace(data_dict, size_value):
    print("add build feature 'FreeDiskSpace' to configuration [{}]".format(
        data_dict['conf_id'],
    ))

    data_xml = '''
        <feature id="jetbrains.agent.free.space" type="jetbrains.agent.free.space">
            <properties count="1">
                <property name="free-space-work" value="{size_value}"/>
            </properties>
        </feature>
    '''.format(size_value=size_value)

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{conf_id}/features'.format(**data_dict), OPT_LOGIN,
                        OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def template_addFeatureFreeDiskSpace(data_dict, size_value):
    print("add build feature 'FreeDiskSpace' to template [{}]".format(
        data_dict['template_id'],
    ))

    data_xml = '''
        <feature id="jetbrains.agent.free.space" type="jetbrains.agent.free.space">
            <properties count="1">
                <property name="free-space-work" value="{size_value}"/>
            </properties>
        </feature>
    '''.format(size_value=size_value)

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{template_id}/features'.format(**data_dict),
                        OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def template_addAgentRequirements(data_dict, desc, data_xml):
    print("add agent-requirements [{}] to template [{}]".format(
        desc,
        data_dict['template_id'],
    ))

    rest_delay()

    r = requests.post(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/buildTypes/{template_id}/agent-requirements'.format(**data_dict),
            OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def template_addAgentRequirementsOSName(data_dict, operation_value, value):
    data_xml = '''<agent-requirement id="teamcity.agent.jvm.os.name" type="{operation_value}">
    <properties count="2">
        <property name="property-name" value="teamcity.agent.jvm.os.name"/>
        <property name="property-value" value="{os_name}"/>
    </properties>
</agent-requirement>'''.format(
        operation_value=operation_value,
        os_name=value,
    )

    template_addAgentRequirements(
        data_dict,
        'os={}'.format(value),
        data_xml,
    )


def template_add_build_step(data_dict, step_desc, data_xml, cdata_list=None):
    print('template [{}] add build step [{}]'.format(data_dict['template_id'], step_desc))

    rest_delay()

    if cdata_list:

        for (i, x,) in enumerate(cdata_list):
            data_xml = data_xml.replace(
                'CDATA_{}'.format(i),
                _replace_cdata_field(x),
            )

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{template_id}/steps'.format(**data_dict),
                        OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def template_get_build_steps(data_dict):
    print('template [{}] get build steps'.format(data_dict['template_id']))

    result = []
    r = requests.get(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{template_id}/steps'.format(**data_dict),
                        OPT_LOGIN, OPT_PASS),
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()

    for item in xml.etree.ElementTree.fromstring(r.content):
        result.append(item)

    return result


def template_delete_build_step(data_dict, build_step):
    print('template [{}] delete build step {} [{}]'.format(
        data_dict['template_id'],
        build_step.attrib['id'],
        build_step.attrib['name'],
    ))

    current_data_dict = dict(data_dict)
    current_data_dict.update({
        'step_id': build_step.attrib['id'],
    })

    rest_delay()

    r = requests.delete(
        add_auth_to_url(
            OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{template_id}/steps/{step_id}'.format(**current_data_dict),
            OPT_LOGIN, OPT_PASS),
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    r.raise_for_status()


def configuration_add_build_step(data_dict, step_desc, data_xml):
    print('configuration [{}] add build step [{}]'.format(data_dict['conf_id'], step_desc))  # ExtLibs_Luabridge_Win PtRunnerExtLibsWindowsBuild  | ExtLibs_Luabridge_Nix PtRunnerExtLibsLinuxBuild_2_0

    rest_delay()

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildTypes/id:{conf_id}/steps'.format(**data_dict), OPT_LOGIN,
                        OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )  # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/steps

    r.raise_for_status()

# непонятно зачем, чтобы подчеркнуть  что-то?
def add_build_step(conf_dict, step_id, data_xml): # https://teamcity.ptsecurity.ru/httpAuth/app/rest/buildTypes/id:ExtLibs_Luabridge_Cross/steps
    configuration_add_build_step(conf_dict, step_id, data_xml)


def call_build():
    data_xml = '''
    <build branchName="{logicBuildBranch}">
        <triggeringOptions cleanSources="true"/>
        <buildType id="{buildConfID}"/>
        <agent locator="name:{agentName}"/>
    </build>
    '''.format(buildConfID='ExtLibs_Zlib_CrossBuild', logicBuildBranch='1.2.8-pm', agentName='SERVER-CI-11')

    r = requests.post(
        add_auth_to_url(OPT_TC_URL + '/httpAuth/app/rest/buildQueue', OPT_LOGIN, OPT_PASS),
        data=data_xml,
        headers={'Content-Type': 'application/xml'},
        verify=False,
    )

    try:
        r.raise_for_status()

    except requests.exceptions.HTTPError as e:

        print(r.text)

        raise e


