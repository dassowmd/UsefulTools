import os
import get_song_data
from shutil import copyfile
import tqdm

def walk_directory(root_directory):
    is_delete_old_file = True
    for dir_name, sub_dir_list, file_list in os.walk(root_directory):
        print('Found directory: %s' %dir_name)
        if 'Music Organized' not in str(dir_name):
            for fname in file_list:
                try:
                    filepath = os.path.join(dir_name, fname)
                    song_data = get_song_data.search_best_match(filepath)
                    print 'Successfully matched song %s' %fname
                    move_file(filepath, root_directory, song_data, is_delete_old_file, True)
                except Exception as e:
                    print fname

                    print e
                    # Copy file that caused error to review directory
                    print 'moved file to review directory'

                    try:
                        dest_path = os.path.join(root_directory, 'Music Organized','0_Review',fname)
                        dest_dir = os.path.dirname(dest_path)
                        if os.path.exists(dest_dir):
                            pass
                        else:
                            os.makedirs(dest_dir)

                        copyfile(filepath, dest_path)
                        if is_delete_old_file == True:
                            os.remove(filepath)
                    except Exception as e:
                        print e

def move_file(curr_filepath, dest_root, song_data, is_delete_old_file = False, overwrite_new = True):
    dest_dir = os.path.join(dest_root, 'Music Organized', song_data['artist'])
    filename, file_extension = os.path.splitext(curr_filepath)
    file_title = song_data['title'].replace('/', '//') + file_extension
    dest_path = os.path.join(dest_dir, file_title)
    successfull_copy = False

    if os.path.exists(dest_dir):
        pass
    else:
        os.makedirs(dest_dir)

    if os.path.exists(dest_path):
        if overwrite_new == True:
            try:
                copyfile(curr_filepath, dest_path)
            except Exception as e:
                print e
        else:
            print 'File already exists at %s. Skipping' %dest_path
    else:
        if overwrite_new == True:
            try:
                copyfile(curr_filepath, dest_path)
            except Exception as e:
                print e
    if is_delete_old_file == True:
        os.remove(curr_filepath)


walk_directory('/media/dassowmd/My Passport/Old Hard Drive/Music (copy)')