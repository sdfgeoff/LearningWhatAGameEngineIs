'''This aims to be a super simple dependency system. Like Make was intended to
be but with the power of python instead of shell. This will allow dynamic
generation of entries. This was aimed to allow commands to be run based on
lines in a CSV file - something no dependency system seems to be able to do!

All functions should return "True" if they produced changed output.
If a function returns False, then it indicates nothing changed, and any
downstream functions will not necessarily run (if all dependancies return False)
This allows functions to analyze things in more detail as well as allows
integration with version control etc.

They do not have to be functions, but they do have to be callable. They also
need to be hashable (for storage in the dependency tree).

Note: If something has no dependencies, then it is always executed as it is
percieved to be a "leaf" that checks for changes itself.
'''
import functools
import logging
import os
import hashlib
import pickle
import argparse
import shutil
import sys
import json


CACHE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.cachedir')
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
DEPENDENCY_TREE = {}


# -------------------------- Dependecy Tree Access ---------------------------
def depends_on(function, *functions):
    '''Marks a dependency between one function and some other functions'''
    DEPENDENCY_TREE.setdefault(function, functions)

def _get_immediate_dependencies(function):
    deps = DEPENDENCY_TREE.get(function)
    return deps

def clear_tree():
    global DEPENDENCY_TREE
    DEPENDENCY_TREE = {}


# ----------------------------- Function cache -------------------------------
def _mark_run(function, failed=False):
    '''Stores that this function ran sucessfully last time'''
    json.dump(
        {'ran':failed},
        open(_get_function_cache_filename(function), 'w')
    )

def _check_failure(function):
    '''Checks to see if this function failed to run previously'''
    try:
        data = json.load(open(_get_function_cache_filename(function)))
    except:
        return True
    return data.get('ran', False)

def _check_new_function(function):
    '''Checks to see if this is a new function'''
    try:
        data = json.load(open(_get_function_cache_filename(function)))
    except:
        logging.debug("New function or corrupt cache file for %s", function)
        return True
    return False


def _get_function_cache_filename(function):
    '''Find the file where cache data is to be stored for a single file'''
    return os.path.join(CACHE_PATH, _fingerprint_function(function))


def _fingerprint_function(function):
    '''Uniquely identifies a function and it's immediate dependencies'''
    hash_str = ''
    hash_str += str(pickle.dumps(function))
    return hashlib.md5(hash_str.encode('utf-8')).hexdigest()

def clear_cache():
    logging.debug("Clearing Cache")
    shutil.rmtree(CACHE_PATH)
    os.makedirs(CACHE_PATH)
    


# ------------------------------ Building -------------------------------
@functools.lru_cache(maxsize=None)
def _run_function(function):
    '''Runs a function - but it is cached so it isn't run multiple times in the
    same build process'''
    logging.info("Running: %s", function)
    try:
        res = function()
    except Exception as exc:
        _mark_run(function, failed=True)
        raise(exc)
    _mark_run(function, failed=False)
    if res is None:
        res = True
    assert isinstance(res, bool)
    return res


def _run_dependencies(function, force_tree=False):
    sub_functions = _get_immediate_dependencies(function)
    if sub_functions is None:
        return True
    return any([build(f, force_tree=force_tree) for f in sub_functions])

@functools.lru_cache(maxsize=None)
def build(function, force_single=False, force_tree=False):
    deps = _run_dependencies(function, force_tree)
    force = force_single or force_tree
    cache = _check_new_function(function) or _check_failure(function)
    if deps or force or cache:
        res = _run_function(function)
        return res
    return False


def start_build(name_function_mapping):
    '''Uses sys.argv to take input from the command line'''
    parser = argparse.ArgumentParser()
    parser.add_argument('targets', help="What you want built", nargs='*')
    parser.add_argument('--clear-cache', help="Removes all stored data (eg file timestamps). This will force a complete rebuild", action='store_true')
    parser.add_argument('--force-single', help="Forces just the specified targets to be run", action='store_true')
    parser.add_argument('--force-tree', help="Forces all dependancies of this command (and the command itself) to be run", action='store_true')
    parser.add_argument('--list-targets', help="Lists all named targets", action='store_true')
    parser.add_argument('--all', help="Builds all named targets (not necessarily all available targets)", action='store_true')
    config = parser.parse_args(sys.argv[1:])

    # The only valid targets are things that are callable, so we scrap the rest
    # allowing globals() to be fed straight into this function
    name_function_mapping = {n:f for n,f in name_function_mapping.items() if callable(f)}
    
    did_something = False
    if config.clear_cache:
        print("Clearing Cache")
        clear_cache()
        did_something = True
    if config.all:
        targets = [n for n in name_function_mapping]
    else:
        targets = config.targets
    for target in targets:
        if target not in name_function_mapping:
            print("Unknown target: {}\n".format(target))
        else:
            build(name_function_mapping[target], config.force_single, config.force_tree)
            did_something = True
    if config.list_targets or not did_something:
        print("Valid targets are:")
        for name in sorted(name_function_mapping.keys()):
            print(" - ", name)
    print("Done")


# ----------------------- The ONE predefined tree type ------------------------

class Empty:
    '''Just depends on things'''
    def __init__(self, *args):
        depends_on(self, *args)
        self.depends_on = functools.partial(depends_on, self)
        
    def __call__(self):
        return True


class File:
    '''A simple dependency on a file. You can chose bewteen comparison methods
    including 'hash', 'timestamp'. The str(filepath) should evaluate to a file
    that exists at instantiation time. If it is generated, then there should be
    the dependency on the function that handles the generation of the file.
    However, the check is deffered until execution for flexibility.
    '''
    def __init__(self, filepath, compare_by='timestamp'):
        self.filepath = str(filepath)
        self.compare_by = compare_by

        # Any metadata about the file will be stored here:
        self.cache_file = os.path.join(
            CACHE_PATH,
            str(hashlib.md5(self.filepath.encode('utf-8')).hexdigest())
        )

    def generate_comparison(self):
        '''Generate something with which to compare the file - this can be
        a hash or a timestamp'''
        if self.compare_by == 'timestamp':
            comparison = str(os.path.getmtime(self.filepath))
        elif self.compare_by == 'hash':
            with open(self.filepath) as file_data:
                hash_part = hashlib.md5()
                for chunk in iter(lambda: file_data.read(4096), b""):
                    hash_part.update(chunk)
            comparison = str(hash_part.hexdigest())
        else:
            raise ValueError("Unknown comparison method {}".format(self.compare_by))

        return comparison

    def load_cached(self):
        '''Loads a previously computed comparison value from the cache'''
        if os.path.isfile(self.cache_file):
            return open(self.cache_file).read()
        return ''

    def save_to_cache(self, data):
        '''Saves the comparison value to the cache'''
        open(self.cache_file, 'w').write(data)

    def __call__(self):
        if not os.path.isfile(self.filepath):
            raise ValueError('Filepath {} does not exist'.format(self.filepath))
        new = self.generate_comparison()
        old = self.load_cached()
        if new == old:
            # If it is unchanged, then we don't need to run downstream
            # functions
            return False

        # Otherwise it has changed, and we should run downstream functions
        self.save_to_cache(new)
        return True