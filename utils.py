import os
import subprocess
import json
from pathlib import Path

def get_config_file(filename, script_location=None):
    config=None
    config_path=None

    if script_location is None:
        script_location = Path(__file__).resolve().parent        

    # If the filename is an absolute path, use it as is
    path = Path(filename)
    if path.is_absolute():
        if os.path.exists(filename):
            config_path = filename
    else:
        home_dir  = str(Path.home())
        home_path = f'{home_dir}/{filename}'
        if os.path.exists (home_path):
            config_path = home_path
        else:
            tool_path = f'{script_location}/{filename}'
            if os.path.exists(tool_path):
                config_path = tool_path

    if config_path is not None:
        config = json.load(open(config_path, 'r'))

    return config

def call_job_script(config,
                    script_file,
                    default_temp_file='C:/Temp/razor.json',
                    no_command=False):

    iray_config = config['iray_config']
    if iray_config['use_temp_config']:
        temp_path = iray_config['temp_config_path']
    else:
        temp_path = default_temp_file

    print (f'Writing configuration to {temp_path}')
    print (f'Config is \n {json.dumps(config, indent=2)}')

    with open(temp_path, 'w') as f:
        f.write (json.dumps(config, indent=2))
        f.flush()

    exec_generic_command (script_file, None, no_command)

def exec_generic_command(script_file:str, script_vars:dict, no_command:bool=False):

    daz_root = "c:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe"
    
    if no_command == False:
        mark_args="";        
        if script_vars is not None:
            mark_args += f'{json.dumps(script_vars)}'
            #for x in script_args:
            #    mark_args += f'-scriptArg "{x}" '

        
        print (f'Executing script file: {script_file} MA={mark_args}')
        process = subprocess.Popen (f'"{daz_root}" -scriptArg \'{mark_args}\' {script_file}',
                                    shell=False)

    else:
        print (f'No-command is in effect. No script op run')
