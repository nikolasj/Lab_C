import sys
import subprocess

def main( project_name, git_url_official, branch_external_git):
    print("Diff! " + project_name)
    print("----------------------------------")
    subprocess.call(
        'cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git pull --no-edit ' + git_url_official + branch_external_git,
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | touch Changes.txt', shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout ' + branch_external_git, shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git diff ' + branch_external_git + '^ >> ' + project_name + 'Changes.txt', shell=True)
    print("----------------------------------")
    print("Diff Finish! " + project_name)

