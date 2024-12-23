import os
import json
import shutil
from subprocess import PIPE,run
import sys

GAME_DIR_PATTERN="game"
COMPILE_COMMAND=["go","build"]

def find_game_paths(source_dir):
    game_paths=[]

    for root,dirs,files in os.walk(source_dir):
        
        for dir in dirs:
            if GAME_DIR_PATTERN in dir.lower():
                game_paths.append(os.path.join(source_dir,dir))

        break

    return game_paths


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_name_from_paths(paths):
    names=[]
    for path in paths:
        _,dir_name=os.path.split(path)
        name=dir_name.replace(GAME_DIR_PATTERN,"")
        names.append(name)

    return names

def copy_and_overwrite(src,dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src,dest)

def make_json_file(path,game_dirs):
    data={
        "gameName":game_dirs,
        "noOfGames":len(game_dirs)
    }
    with open(path,"w") as f:
        json.dump(data,f)


def compile_game(path):
    code_file_name=None

    for root,dirs,files in os.walk(path):
        for file in files:
            if file.endswith(".go"):
                code_file_name=file
                break
        break

    if code_file_name is None:
        return
    
    command=COMPILE_COMMAND+[code_file_name]
    print("running command:",command)

    run_command(command,path)

def run_command(command,path):
    pwd=os.getcwd()
    os.chdir(path)

    result=run(command,stdout=PIPE,stderr=PIPE,universal_newlines=True)

    print("compile result:",result.stdout)

    os.chdir(pwd)

def main(source_dir,target_dir):
    pwd=os.getcwd()
    source=os.path.join(pwd,source_dir)
    target=os.path.join(pwd,target_dir)

    game_paths=find_game_paths(source)
    new_game_dirs=get_name_from_paths(game_paths)

    create_dir(target)

    for src,dest in zip(game_paths,new_game_dirs):
        dest_path=os.path.join(target,dest)
        copy_and_overwrite(src,dest_path)
        compile_game(dest_path)
    
    json_path=os.path.join(target,"game_data.json")
    make_json_file(json_path,new_game_dirs)


if __name__ == "__main__":
    args=sys.argv
    if len(args)!=3:
        raise Exception("Usage: python get_game_data.py <game_name> <game_id>")
        sys.exit(1)
    source_dir,target_dir=args[1:]
    main(source_dir,target_dir)