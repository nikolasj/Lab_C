import sys
import subprocess
import datetime

def last_changed( project_name, git_url, branch,login, passwd):
    # Record was last changed in a branch to a file
    print("Start!")
    print("----------------------------------")
    subprocess.call('mkdir /home/cm/' + project_name + '/', shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/; echo "one" | git clone ' + 'https://' + login + ':' + passwd + git_url,
                    shell=True)
    #subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | touch ' + project_name + 'DateLastChange.txt', shell=True)
    subprocess.call('cd /home/cm/test_git/;echo "one" | touch ' + project_name + 'DateLastChange.txt',
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout ' + branch,
                    shell=True)
    subprocess.call(
        'cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git log -1 ' + branch + ' >> /home/cm/test_git/' + project_name + 'DateLastChange.txt',
        shell=True)
    print("----------------------------------")
    print("Finish!")
    date_file(project_name)
    subprocess.call(
        'cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | rm /home/cm/test_git/' + project_name + 'DateLastChange.txt',
        shell=True)

def date_file( project_name):
    name_file_read = project_name + 'DateLastChange.txt'
    date = ""
    f = open(name_file_read, 'r')
    for line in f:
        str = line.split(' ')
        if str[0] == "Date:":
            date = str[5] + ' ' + str[4] + ' ' + str[7]
            print(date)
    f.close()
    compare_date(date,'16 Jul 2016')
    name_file_write = project_name + 'AnalisChange.txt'
    if compare_date(date,'16 Jul 2016'):
        w = open(name_file_write, 'w')
        w.write('GitLab - ' + date + '\n')
        w.close()

def compare_date(date_gitlab,date_external_git):
    temp_date_gitlab = date_gitlab.split(' ')
    temp_date_external_git = date_external_git.split(' ')
    if temp_date_external_git[2] > temp_date_gitlab[2]:
        return True
    if temp_date_external_git[2] == temp_date_gitlab[2] and temp_date_external_git[1] > temp_date_gitlab[1]:
        return True
    if temp_date_external_git[2] == temp_date_gitlab[2] and temp_date_external_git[1] == temp_date_gitlab[1] and temp_date_external_git[0] > temp_date_gitlab[0]:
        return True
    # d_gitlab = datetime.datetime.strtime(date_gitlab,'%d.%m.%Y')
    # d_external_git = datetime.datetime.strtime(date_external_git,'%d.%m.%Y')
    # if d_gitlab < d_external_git:
    #     return True
    # return False

