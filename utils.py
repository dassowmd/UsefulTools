import time
import os
import glob
import pickle


def timeit(method):
    is_print = False
    time_min = 2000

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            if is_print:
                if (te - ts) * 1000 > time_min:
                    print("%r  %2.2f ms" % (method.__name__, (te - ts) * 1000))
        return result

    return timed


def prepend_zeros(string, desired_length):
    s = "0" * (desired_length - len(str(string))) + str(string)
    return s


__all__ = ["memoize"]


def memoize(function, limit=None):
    if isinstance(function, int):

        def memoize_wrapper(f):
            return memoize(f, function)

        return memoize_wrapper

    dict = {}
    list = []

    def memoize_wrapper(*args, **kwargs):
        key = pickle.dumps((args, kwargs))
        try:
            list.append(list.pop(list.index(key)))
        except ValueError:
            dict[key] = function(*args, **kwargs)
            list.append(key)
            if limit is not None and len(list) > limit:
                del dict[list.pop(0)]

        return dict[key]

    memoize_wrapper._memoize_dict = dict
    memoize_wrapper._memoize_list = list
    memoize_wrapper._memoize_limit = limit
    memoize_wrapper._memoize_origfunc = function
    memoize_wrapper.func_name = function.func_name
    return memoize_wrapper


def get_files(directory, directory_path):
    file_list = []
    for root, sub_dirs, files in os.walk(directory):
        for i in files:
            file_list.append(os.path.join(root, i))
        for sub_dir in sub_dirs:
            sub_dir_files = get_files(
                sub_dir, directory_path=os.path.join(directory_path, sub_dir)
            )
            if len(sub_dir_files) > 0:
                for i in sub_dir_files:
                    file_list.append(os.path.join(root, i))
    return file_list


def line_count(directory):
    os.chdir(directory)
    total_lines = 0
    total_lines_all = 0
    files = get_files(directory=directory, directory_path=directory)
    for fn in files:
        if fn.endswith(".py") or fn.endswith(".sql"):
            with open(fn) as f:
                for line in f:
                    total_lines_all += 1
                    if line.strip() and not line.strip().startswith("#"):
                        total_lines += 1
        # else:
        #     print fn
    print ("Total lines %i" % total_lines)
    print ("Total lines all %i" % total_lines_all)


if __name__ == "__main__":
    directory = input("What directory would you like to count?")
    line_count(directory=directory)
