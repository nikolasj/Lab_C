import sys
import subprocess

def main( project_name, git_url, git_url_official,login, passwd):
    print("Start!")
    print("----------------------------------")
    subprocess.call('mkdir /home/cm/' + project_name + '/', shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/; echo "one" | git clone ' + 'https://' + login + ':' + passwd + git_url,
                    shell=True)
    subprocess.call(
        'cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git pull --no-edit ' + git_url_official,
        shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | touch Changes.txt', shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git checkout master', shell=True)
    subprocess.call('cd /home/cm/' + project_name + '/' + project_name + '/;echo "one" | git diff master^ >> Changes.txt', shell=True)
    print("----------------------------------")
    print("Finish!")

