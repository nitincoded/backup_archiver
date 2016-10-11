#!/usr/local/bin/python3

import os
import platform
import time
import datetime
import shutil
import sys

supported_platforms = ['Darwin', 'Windows', 'Linux']


def get_path_with_slash_at_end(path):
    return path if path[-1] == '/' else path+'/'


def get_file_list(path):
    child_files_and_dirs = os.listdir(path)
    child_files = [f for f in child_files_and_dirs if os.path.isfile(get_path_with_slash_at_end(path) + f)]
    
    retval = {}

    for f in child_files:
        mod_date = None
        if platform.system() == 'Darwin':
            mod_date = os.stat(get_path_with_slash_at_end(path) + f).st_birthtime
        elif platform.system() == 'Windows':
            mod_date = os.path.getctime(get_path_with_slash_at_end(path) + f)
        elif platform.system() == 'Linux':
            mod_date = os.path.getmtime(get_path_with_slash_at_end(path) + f)
        else:
            try:
                mod_date = os.stat(get_path_with_slash_at_end(path) + f).st_mtime
            except AttributeError:
                raise Exception('Unrecognized platform')
        retval[f] = datetime.date.fromtimestamp(mod_date) #time.ctime(mod_date)

    return retval


def list_for_copy(src, dest):
    src_child_files_and_dirs = os.listdir(src)
    src_child_files = [f for f in src_child_files_and_dirs if os.path.isfile(get_path_with_slash_at_end(src) + f)]
    dest_child_files_and_dirs = os.listdir(dest)
    dest_child_files = [f for f in dest_child_files_and_dirs if os.path.isfile(get_path_with_slash_at_end(dest) + f)]
    diff_files = [f for f in src_child_files if not f in dest_child_files]
    return diff_files


def list_for_delete(dest, retain_age):
    dest_child_files = get_file_list(dest)
    retval = []
    for k, v in dest_child_files.items():
        if v < datetime.date.today() - datetime.timedelta(days=retain_age):
            retval.append(k)
    return retval


def copy_files(src, dest, files):
    for f in files:
        shutil.copyfile(get_path_with_slash_at_end(src)+f, get_path_with_slash_at_end(dest)+f)


def delete_files(dest, files):
    for f in files:
        os.remove(get_path_with_slash_at_end(dest)+f)


def help_text():
    print('''
        Help
        ./backupArchiver.sh --help

        Archive the backups
        ./backupArchiver.sh --src=/copy_from_here/ --dest=/copy_to_here/ [--aging={src|dest|both|none} --age=n]
        ''')


def process_args(sargv):
    HELP_CMD_ARR = ['--help', '-h']
    SRC_CMD = '--src='
    DEST_CMD = '--dest='
    AGING_CMD = '--aging='
    AGE_CMD = '--age='

    if sargv[1] in HELP_CMD_ARR:
        # print('Help')
        help_text()
    elif sargv[1][0:len(SRC_CMD)] == SRC_CMD and sargv[2][0:len(DEST_CMD)] == DEST_CMD:
        src_loc = sargv[1][len(SRC_CMD):]
        dest_loc = sargv[2][len(DEST_CMD):]
        aging = 'none'
        age = -1

        # print('--')
        # print(len(sargv)>4, str(len(sargv)))
        # print(sargv[3][:len(AGING_CMD)] == AGING_CMD, '%r' % sargv[3][:len(AGING_CMD)], '%r' % AGING_CMD, len(sargv[3][:len(AGING_CMD)]))
        # print(sargv[4][:len(AGE_CMD)] == AGE_CMD, '%r' % sargv[4][:len(AGE_CMD)], '%r' % AGE_CMD, len(sargv[4][:len(AGE_CMD)]))
        # print('--')

        if len(sargv)>4 and sargv[3][:len(AGING_CMD)] == AGING_CMD and sargv[4][:len(AGE_CMD)] == AGE_CMD:
            # print('Processing aging args')
            aging = sargv[3][len(AGING_CMD):]
            age = int(sargv[4][len(AGE_CMD):])
        # else:
        #     print('Skipping aging args')
        #     pass

        print('Src: ' + src_loc)
        print('Dest: ' + dest_loc)

        copy_files(src_loc, dest_loc, list_for_copy(src_loc, dest_loc))

        print('Aging: ' + aging)
        print('Age: ' + str(age))

        if age > 0 and (aging == 'src' or aging == 'both'):
            delete_files(src_loc, list_for_delete(src_loc, age))

        if age > 0 and (aging == 'dest' or aging == 'both'):
            delete_files(dest_loc, list_for_delete(dest_loc, age))
    else:
        print('Unrecognized args. Pass -h for help')

    # is_first = True
    # for a in sargv:
    #     if is_first:
    #         is_first = False
    #         continue
    #     if a[0:len()] 


def main(sargv):
    # print(str(sargv))
    process_args(sargv)


if __name__ == '__main__':
    main(sys.argv)
