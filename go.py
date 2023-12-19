# chcp 65001

import requests
import gitlab
import os
import sys
from base64 import b64encode

print(sys.stdout.encoding)

# GitLab 設定
gitlab_url = "https://git.abc.com"  # 輸入你的 GitLab 網址
# project_id = "1794"  # 輸入你的專案 ID
private_token = "xxx"  # 輸入你的 GitLab 帳號的 private token

# 連接到 GitLab
gl = gitlab.Gitlab(gitlab_url, private_token)

# 取得我有權限的 Project
print('我有權限的 Project :')
projects = []
for peojects in gl.projects.list():
    # print(peojects.attributes['name'], peojects.attributes['id'], peojects.attributes['permissions'])
    permission = peojects.attributes['permissions']['project_access']
    if permission != None:
        if permission['access_level'] == 40:
            projects.append(peojects.attributes['id'])
            print(peojects.attributes['name'], ':', peojects.attributes['id'] )

print(projects)

errorList = []

for project_id in projects:
    print(f'*** Project id : {project_id}')

    # 取得專案
    project = gl.projects.get(project_id)

    # 取得檔案清單
    try:
        files = project.repository_tree(all=True, recursive=True)
    except Exception as error:
        print(f'*** Project Error : {project_id} get tree error.')
        print(error)
        continue
    
    # print(files)

    # 修改檔案名稱
    for file in files:
        file_path = file["path"]

        file_name, file_extension = os.path.splitext(file_path)
        base_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)

        new_file_path = f"{dir_name}/(機密等級=一般文件) {base_name}"
        
        if file_extension.lower() in ['.doc', '.docx', '.ppt', '.pptx', '.xlsx', '.pdf', '.zip', '.7z'] and '機密等級' not in base_name:

            try:

                # 取得檔案內容
                file_content = b64encode(project.files.get(file_path, ref='master').decode()).decode('utf-8')

                # 創建新檔案
                project.files.create({
                    'file_path': new_file_path,
                    'branch': 'master',
                    'content': file_content,
                    'encoding': 'base64',
                    'commit_message': f"Rename file: {file_path} to {new_file_path}"
                })

                # 刪除舊檔案
                project.files.delete(
                    file_path=file_path,
                    branch='master',
                    commit_message=f"Rename file: {file_path} to {new_file_path}"
                )

                print(f"==> Successful : {project_id} {file_path} rename to {new_file_path}")

            except Exception as error:
                errorList.append(f'{project_id} : {file_path}')
                print(f'==> Error      : {project_id} {file_path} rename error.')
                print(error)

        else:
            print(f'==> Skipped    : {project_id} {file_path}')

print('\n')
print('errorList :', errorList)
print('\tDone.\t')
