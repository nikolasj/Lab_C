import os
import sys
import subprocess
import datetime
from jinja2 import Environment, FileSystemLoader

j2_env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))

def last_changed(project_name, git_url, branch, git_external, branch_external, login, passwd):
    """
    Specifies the last modified date gitlab and external repository.
    """
    print("--------------------------")
    print("--  Start! {}  --".format(project_name))
    print("--------------------------")

    """
    Determine the date of the last change gitlab
    echo "one" is necessary for the proper operation of the conveyor
    """
    subprocess.call('mkdir /home/cm/' + project_name + '/', shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/; echo "one" | git clone ' + 'https://' +
        login + ':' + passwd + git_url, shell=True)
    subprocess.call('cd /home/cm/test_git/;echo "one" | touch ' + project_name + 'DateLastChange.txt',
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout ' + branch,
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git log -1 ' + branch +
        ' >> /home/cm/test_git/' + project_name + 'DateLastChange.txt', shell=True)
    subprocess.call('cd /home/cm/test_git/;echo "one" | touch ' + project_name + 'DateLastChangeExternalGit.txt',
                    shell=True)
    subprocess.call('cd /home/cm/test_git/;echo "one" | touch ' + project_name + 'Changes.txt', shell=True)

    """Determine the date of the last external repository"""
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git pull --no-edit ' +
        git_external + ' ' + branch_external, shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout ' + branch_external,
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git log -1 ' + branch +
        ' >> /home/cm/test_git/' + project_name + 'DateLastChangeExternalGit.txt',
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout ' + branch_external,
                    shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git diff ' + branch_external +
        '^ >> /home/cm/test_git/' + project_name + 'Changes.txt', shell=True)
    

    date_file(project_name)

    print("--------------------------")
    print("--  Finish! {}  --".format(project_name))
    print("--------------------------")

    """ Removing unnecessary files and folders"""
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | rm -rf .git*', shell=True)
    subprocess.call('rm -R /home/cm/' + project_name ,shell=True)
    subprocess.call('rm /home/cm/test_git/' + project_name + 'DateLastChange.txt', shell=True)
    subprocess.call('rm /home/cm/test_git/' + project_name + 'DateLastChangeExternalGit.txt', shell=True)



def date_file(project_name):
    """
    The method that checks the date of recent changes.
    From log files come from the last modified date and compared.
    If the changes are relevant, then a new file where the recorded changes.
    """
    name_file_gitlab = '/home/cm/test_git/' + project_name + 'DateLastChange.txt'
    date_gitlab = ""
    name_file_change = '/home/cm/test_git/' + project_name + 'AnalisChange.txt'
    name_file_external_git = '/home/cm/test_git/' + project_name + 'DateLastChangeExternalGit.txt'
    date_external_git = ""
    name_file_changes = '/home/cm/test_git/' + project_name + 'Changes.txt'

    """ Determine the date of the last change githab"""
    f_gitlab = open(name_file_gitlab, 'r')
    for line in f_gitlab:
        str = line.split(' ')
        if str[0] == "Date:":
            date_gitlab = str[5] + ' ' + str[4] + ' ' + str[7]
    f_gitlab.close()

    data = ""
    f_changes = open(name_file_changes, 'r')
    for line in f_changes:
        data = line
    f_changes.close()

    """ Determine the date of the last change external repository"""
    fe = open(name_file_external_git, 'r')
    for line in fe:
        str = line.split(' ')
        if str[0] == "Date:":
            date_external_git = str[5] + ' ' + str[4] + ' ' + str[7]
    fe.close()

    """ Comparison of the two dates."""
    if compare_date(date_gitlab, date_external_git):
        w = open(name_file_change, 'w')
        w.write('GitLab - ' + date_gitlab + '\n')
        w.write('External git - ' + date_external_git + '\n')
        w.write('Check changes!!!')
        w.close()
        html_generate_changes(project_name, data)
        html_generate(project_name, date_gitlab, date_external_git) 
    else:
        w = open(name_file_change, 'w')
        w.write(project_name + ' had no changes!!!')
        w.close()
        subprocess.call('rm /home/cm/test_git/' + project_name + 'Changes.txt', shell=True)   
    subprocess.call('rm /home/cm/test_git/' + project_name + 'AnalisChange.txt', shell=True)



def compare_date(date_gitlab, date_external_git):
    """
    Function to compare two dates
    """
    d_gitlab = datetime.datetime.strptime(date_gitlab, "%d %b %Y")
    date_external_repo = datetime.datetime.strptime(date_external_git, "%d %b %Y")
    if date_external_repo > d_gitlab:
        return True
    return False


def html_generate(project_name, date_gitlab, date_external_git):
    """
    Function to generate the html file.
    """
    template = j2_env.get_template('html_template')
    #html_links = {'Main Page':'http://xgu.ru', 'Jinja':'http://xgu.ru/wiki/Jinja2'}
    data = {'title': project_name, 'header_1': project_name,'header_2': date_gitlab, 'header_3': date_external_git}
    name_file ='/home/cm/test_git/' + project_name + ".html"
    with open(name_file, "w") as f:
        f.write(template.render(data))

def html_generate_changes(project_name, data):
    
    template = j2_env.get_template('html_template_changes')
    #html_links = {'Main Page':'http://xgu.ru', 'Jinja':'http://xgu.ru/wiki/Jinja2'}
    data2 = {'title': project_name, 'header_1': project_name,'header_2': data}
    name_file ='/home/cm/test_git/' + project_name + "Changes.html"
    with open(name_file, "w") as f:
        f.write(template.render(data2))        