# write your code here
import os
import sys

from hashlib import md5


def hash_files(grouped_files):
    hashed_files = {}
    for size, files in grouped_files.items():
        hashed_files[size] = {}
        for file in files:
            with open(file, 'rb') as f_in:
                f_hash = md5(f_in.read()).hexdigest()
            if f_hash in hashed_files[size].keys():
                hashed_files[size][f_hash].append(file)
            else:
                hashed_files[size][f_hash] = [file]
    return hashed_files


def handler(dir):
    duplicated_files = {}
    files = []
    grouped_files = {}
    file_format = input('Enter file format:')
    print('Size sorting options:\n1. Descending\n2. Ascending')
    correct_input = False
    hash_option = None
    delete_option = None
    while not correct_input:
        sort_order = int(input('Enter a sorting option:'))
        if sort_order not in (1, 2):
            print('Wrong option')
            continue
        reverse = True if sort_order == 1 else False
        break

    for dirpath, dirname, filenames in os.walk(dir):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            file_size = os.path.getsize(file_path)
            if file_path.endswith(file_format) or not file_format:
                files.append({file_size: file_path})
    # convert list of dict to dict of list
    for files_info in files:
        for size, f_name in files_info.items():
            if size in grouped_files:
                grouped_files[size].append(f_name)
            else:
                grouped_files[size] = [f_name]
    for size in sorted(grouped_files.keys(), reverse=reverse):
        print(f'{size} bytes')
        print('\n'.join(grouped_files[size]))

    while hash_option not in ['yes', 'no']:
        hash_option = input('Check for duplicates?\n')
        if hash_option not in ['yes', 'no']:
            print('Wrong option')
    if hash_option == 'no':
        return
    grouped_files = hash_files(grouped_files)
    file_num = 1
    printed = False
    for size in sorted(grouped_files.keys(), reverse=reverse):
        for file_hash, files in grouped_files[size].items():
            if len(files) == 1:
                continue
            else:
                if not printed: print(f'{size} bytes')
                print(f'HASH {file_hash}')
                for file in files:
                    print(f'{file_num}. {file}')
                    duplicated_files[file_num] = file
                    file_num += 1
                printed = True
        printed = False

    while delete_option not in ['yes', 'no']:
        delete_option = input('Delete files?\n')
        if delete_option not in ['yes', 'no']:
            print('Wrong option')
    if delete_option == 'no':
        return

    while True:
        user_input = input('Enter file numbers to delete:').split()
        if not user_input:
            print('Wrong format')
            continue
        try:
            id_for_delete = [int(f_id) for f_id in user_input]
            break
        except ValueError:
            print('Wrong format')
            continue

    freed_space = 0
    for f_id in id_for_delete:
        freed_space += os.path.getsize(duplicated_files[f_id])
        os.remove(duplicated_files[f_id])
    print(f'Total freed up space: {freed_space} bytes')


def main():
    if len(sys.argv) != 2:
        print('Directory is not specified')
        return
    root_dir = sys.argv[1]

    handler(dir=root_dir)


if __name__ == '__main__':
    main()
