import sys
import subprocess
import datetime
import GitCloneProject

def last_changed( project_name, git_url, branch, git_external, branch_external,login, passwd ):
    # Record was last changed in a branch to a file
    print("Start! " + project_name)
    print("----------------------------------")
    subprocess.call('mkdir /home/cm/' + project_name + '/', shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/; echo "one" | git clone ' + 'https://' + login + ':' + passwd + git_url,
                    shell=True)
    subprocess.call('cd /home/cm/test_git/;echo "one" | touch ' + project_name + 'DateLastChange.txt',
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout ' + branch,
                    shell=True)
    subprocess.call(
        'cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git log -1 ' + branch + ' >> /home/cm/test_git/' + project_name + 'DateLastChange.txt',
        shell=True)
        # ----------------------------------------------------------------------------------------
    subprocess.call('cd /home/cm/test_git/;echo "one" | touch ' + project_name + 'DateLastChangeExternalGit.txt',
                    shell=True)
    subprocess.call('cd /home/cm/test_git/;echo "one" | touch ' + project_name + 'Changes.txt', shell=True)   
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git pull --no-edit ' + git_external + ' ' + branch_external, shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout ' + branch_external,
                    shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git log -1 ' + branch + ' >> /home/cm/test_git/' + project_name + 'DateLastChangeExternalGit.txt',
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout ' + branch_external,
                    shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git diff ' + branch_external + '^ >> /home/cm/test_git/' + project_name + 'Changes.txt', shell=True)
    date_file(project_name)
    print("----------------------------------")
    print("Finish! " + project_name)
    date_file(project_name)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | rm -rf .git*', shell=True)
    subprocess.call('rm -R /home/cm/' + project_name ,shell=True)
    subprocess.call('rm /home/cm/test_git/' + project_name + 'DateLastChange.txt', shell=True)
    subprocess.call('rm /home/cm/test_git/' + project_name + 'DateLastChangeExternalGit.txt', shell=True)

def date_file( project_name):
    name_file_read = project_name + 'DateLastChange.txt'
    date = ""
    f = open(name_file_read, 'r')
    for line in f:
        str = line.split(' ')
        if str[0] == "Date:":
            date = str[5] + ' ' + str[4] + ' ' + str[7]
            #print(date)
    f.close()
    name_file_write = project_name + 'AnalisChange.txt'
    name_file_external_git = project_name + 'DateLastChangeExternalGit.txt'
    date_external_git = ""
    fe = open(name_file_external_git, 'r')
    for line in fe:
        str = line.split(' ')
        if str[0] == "Date:":
            date_external_git = str[5] + ' ' + str[4] + ' ' + str[7]
            #print(date)
    fe.close()
    #date_external_git = '20 Oct 2013'
    if compare_date(date,date_external_git):
        w = open(name_file_write, 'w')
        w.write('GitLab - ' + date + '\n')
        w.write('External git - ' + date_external_git + '\n')
        w.write('Check changes!!!')
        w.close()
    else:
        w = open(name_file_write, 'w')
        w.write(project_name + ' had no changes!!!')
        w.close()
        subprocess.call('rm /home/cm/test_git/' + project_name + 'Changes.txt', shell=True)
    subprocess.call('rm /home/cm/test_git/' + project_name + 'AnalisChange.txt', shell=True)

def compare_date(date_gitlab,date_external_git):
    temp_date_gitlab = date_gitlab.split(' ')
    temp_date_external_git = date_external_git.split(' ')
    if temp_date_external_git[1] == 'Jul':
        temp_date_external_git[1] = '7'
    if temp_date_gitlab[1] == 'Jun':
        temp_date_gitlab[1] = '6'
    if temp_date_external_git[2] > temp_date_gitlab[2]:
        return True
    if temp_date_external_git[2] == temp_date_gitlab[2] and temp_date_external_git[1] > temp_date_gitlab[1]:
        return True
    if temp_date_external_git[2] == temp_date_gitlab[2] and temp_date_external_git[1] == temp_date_gitlab[1] and temp_date_external_git[0] > temp_date_gitlab[0]:
        return True
    #print(temp_date_external_git[2])
    #print(temp_date_gitlab[2])
    #print(temp_date_external_git[1])
    #print(temp_date_gitlab[1])
    #print(temp_date_external_git[0])
    #print(temp_date_gitlab[0])
    return False
