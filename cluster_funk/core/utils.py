import os
import re
import tarfile


def find_nearest_root(current_path=os.getcwd(), iterleft=20):
    if not iterleft:
        return None
    if os.path.exists("%s/.cf" % (current_path)):
        return current_path
    return find_nearest_root(os.path.abspath(os.path.join(current_path, os.pardir)), iterleft=iterleft-1)


def get_subfolders(start_path):
    try:
        root = find_nearest_root()
        full_path = os.path.join(root, start_path)
        if os.path.exists(full_path):
            return os.listdir(full_path)
        return list()
    except TypeError as type_issue:
        return list()


def environment_names():
    return get_subfolders("environments")


def template_names(env):
    return [filename.split(".")[0] for filename in get_subfolders("environments/%s" % (env))]


def job_names():
    return get_subfolders("jobs")
