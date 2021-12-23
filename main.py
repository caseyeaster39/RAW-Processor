import os
import json
import rawpy
import exifread

from PIL import Image


def get_stored_directories():
    try:
        with open('./cache/dir_store.json', 'r') as fin:
            path_dict = json.load(fin)
            if not path_dict:
                path_dict = empty_json_handler()
    except FileNotFoundError:
        path_dict = empty_json_handler()
    if path_dict:
        print('\n##################################################')
        print('The following directories are available for search:')
        for alias, directory in path_dict.items():
            print(f'\t{alias}: {directory}')
        print('##################################################\n')
    return path_dict


def empty_json_handler():
    path_dict = {}
    valid_input = False
    user_in = None
    while not valid_input:
        if not user_in:
            user_in = input("You have not yet saved a photography directory. Would you like to add one? "
                            "(y,n)\n").lower()
        else:
            user_in = input("Invalid input, please enter y or n:\n").lower()
        if user_in == 'y':
            valid_input = True
            path_dict = add_new_directory()
        elif user_in == 'n':
            valid_input = True
    return path_dict


def user_actions(directories):
    done = False
    user_option_prompt = "You have the following options (enter corresponding number):\n" \
                         "\t1. Select existing paths for conversion.\n" \
                         "\t2. Add another path to the search directory.\n" \
                         "\t3. Remove an existing path from the search directory.\n" \
                         "\t4. Exit script.\n"
    while not done:
        user_action = input(user_option_prompt)
        if user_action == '1':
            compressor_dirs = get_compressor_dirs(directories)
            selected_dirs = path_selection(compressor_dirs)
            if selected_dirs:
                for directory in selected_dirs:
                    raw_to_jpg(directory)
                print("\n########################################################################################")
                print(f"Conversion complete on selected directories:")
                for directory in selected_dirs:
                    print(f" -> {os.path.split(directory)[0]}")
                print("########################################################################################\n")
        elif user_action == '2':
            add_new_directory(directories)
        elif user_action == '3':
            remove_directory()
        elif user_action == '4':
            done = True
        else:
            print("\nInvalid input, please enter the number corresponding to your choice.\n")


def add_new_directory(path_dict=None):
    path_dict = path_dict if path_dict else {}
    folder = input("Please copy the full directory here:\n")
    while not os.path.exists(folder):
        folder = input("Invalid path; please try again. Otherwise, hit return to exit:\n")
        if not folder:
            break
    if folder:
        folder_alias = input(f"You are adding {folder} to your stored directories.\n"
                             f"What name would you like to give this directory?\n")
        path_dict[folder_alias] = folder
        with open('./cache/dir_store.json', 'w') as fout:
            json.dump(path_dict, fout)
    return path_dict


def remove_directory():
    with open('./cache/dir_store.json', 'r') as fin:
        path_dict = json.load(fin)

    print('\n##################################################')
    print('Which directory would you like to remove?')
    for alias, directory in path_dict.items():
        print(f'\t{alias}: {directory}')
    print('##################################################\n')

    valid_input = False
    while not valid_input:
        to_remove = input("Please type an alias to delete the entry from storage, or press return to exit.\n")
        if to_remove in path_dict:
            del path_dict[to_remove]
            valid_input = True
        elif to_remove == "":
            valid_input = True
        else:
            print("Alias not found in storage.")

    with open('./cache/dir_store.json', 'w') as fout:
        json.dump(path_dict, fout)


def get_compressor_dirs(directories):
    compressor_paths = {}
    for alias, directory in directories.items():
        compressor_paths[alias] = do_search(directory)
    return compressor_paths


def do_search(directory, compressor_paths=None):
    compressor_paths = compressor_paths if compressor_paths else []
    files = os.listdir(directory)
    for file in files:
        abs_path = os.path.join(directory, file)
        if file == 'compressor':
            compressor_paths.append(abs_path)
        elif os.path.isdir(abs_path):
            compressor_paths = do_search(abs_path, compressor_paths)
    return compressor_paths


def path_selection(image_dirs):
    dir_lookup = {}
    to_be_compressed = []
    dir_index = 0

    print("Directories available for conversion:")
    for alias, directory_list in image_dirs.items():
        print(f" -> {alias}")
        for directory in directory_list:
            dir_index += 1
            dir_lookup[dir_index] = directory
            compressor_parent_folder = os.path.split(os.path.split(directory)[0])[-1]
            print(f"\t{dir_index}. {compressor_parent_folder}")
    print("===================================================================\n")
    print("Which directories would you like to select? Press return to cancel.")
    valid_input = False
    while not valid_input:
        user_choice = input("Enter the numbers corresponding to your selection (space separated), "
                            "or just enter \"A\" to select them all.\n").lower().split()
        if user_choice == ['a']:
            valid_input = True
            for _, dir_list in image_dirs.items():
                for directory in dir_list:
                    to_be_compressed.append(directory)
        elif user_choice == ['']:
            valid_input = True
        else:
            try:
                entries = [int(entry) for entry in user_choice]
            except TypeError:
                print(f"Invalid input:\n -> {user_choice}\n"
                      f"Please enter space-separated integers corresponding to available choices.")
                break

            for entry in entries:
                if entry > dir_index:
                    print(f"No entry found for \"{entry}\"")
                    break
                else:
                    to_be_compressed.append(dir_lookup[entry])
            valid_input = True
    return to_be_compressed


def raw_to_jpg(compression_path):
    files = os.listdir(compression_path)
    total = len(files)
    i = 1
    if len(files) == 0:
        return
    compression_parent = os.path.split(compression_path)[0]
    print("\n###########################################################")
    print(f"Running converter on {compression_parent}.")
    for file in files:
        if file.endswith('.NEF'):
            print(f" -> Converting file {i}/{total}: {file[:-4]}", end='\r')
            i += 1

            abs_path = os.path.join(compression_path, file)
            with open(abs_path, 'rb') as fin:
                tags = exifread.process_file(fin, details=False, stop_tag='EXIF DateTimeOriginal')
            dt_exif = str(tags['EXIF DateTimeOriginal']).split()
            dt_info = dt_exif[0].split(':')

            memories_subdirectory = os.path.join(compression_parent, "memories")
            if not os.path.exists(memories_subdirectory):
                os.mkdir(memories_subdirectory)

            new_subdirectory = os.path.join(memories_subdirectory, f"{dt_info[0]}-{dt_info[1]}-{dt_info[2]}")
            if not os.path.exists(new_subdirectory):
                os.mkdir(new_subdirectory)

            with rawpy.imread(abs_path) as raw:
                rgb = raw.postprocess(use_camera_wb=True)
            Image.fromarray(rgb).save(f"{os.path.join(new_subdirectory, file[:-4])}.jpg")
    print(f"Conversion done for {compression_parent}.")
    print("###########################################################\n")

    deleter = input(f"Would you like to delete the RAW pictures in {compression_path}? (y/n)\n").lower()
    valid_input = False
    while not valid_input:
        if deleter == 'y':
            valid_input = True
            for file in files:
                if file.endswith('.NEF'):
                    abs_path = os.path.join(compression_path, file)
                    print(f" -> Deleting: {file[:-4]}", end='\r')
                    try:
                        os.remove(abs_path)
                    except OSError as e:
                        print(f"Error: {e.filename} - {e.strerror}.")
            print(f"Deleted files from {compression_path}")
        elif deleter == 'n':
            valid_input = True
            print(f"Continuing without deletion in {compression_path}...")
        else:
            print("Please enter a valid input (y/n):\n")


def main():
    image_dirs = get_stored_directories()
    if image_dirs:
        user_actions(image_dirs)
    else:
        print("No stored directories, exiting script...")


if __name__ == '__main__':
    main()
