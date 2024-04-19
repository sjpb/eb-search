#!/usr/bin/env python3

""" NB all searches are case-insensitive """

from easybuild.tools.options import set_up_configuration
from easybuild.tools.robot import search_easyconfigs
from easybuild.framework.easyconfig.easyconfig import get_toolchain_hierarchy
import sys, os, argparse, runpy, ast

parser = argparse.ArgumentParser(description='Search for EasyBuild configs')
parser.add_argument('name', help="Name of software contains NAME ")
parser.add_argument('-v', '--version', help="Version of software contains VERSION")
parser.add_argument('-t', '--toolchain', help="Toolchain contains TOOLCHAIN")
parser.add_argument('-c', '--compatible', action='store_true', help="with -t, compatible toolchains contains TOOLCHAIN")
parser.add_argument('-f', '--full', action='store_true', help="Show full path")

args = parser.parse_args()
# print(args)
# exit()

def parse_eb(path):
    """ Return a dict of settings from a .eb file """
    settings = dict(name=None, version=None, toolchain=None, toolchainopts=None, versionsuffix=None)
    with open(path) as f:
        src = f.read()
    for n in ast.parse(src).body:
        if not isinstance(n, ast.Assign):
            continue
        assert len(n.targets) == 1
        assert isinstance(n.targets[0], ast.Name)
        name = n.targets[0].id
        try:
            val = ast.literal_eval(n.value)
        except ValueError: # might not be a literal if it uses an easybuild constant
            val = None
        if val and name in settings:
            settings[name] = val
    return settings

if __name__ == '__main__':
    set_up_configuration([]) # have to explicitly tell it not to use sys.argv
    easyconfigs = search_easyconfigs(args.name, print_result=False)
    for path in easyconfigs:
        eb_name = os.path.basename(path)
        if not eb_name.endswith('.eb'): # e.g .patch
            continue
        eb_params = parse_eb(path)
        name = eb_params['name'].lower()
        ver = eb_params['version']
        tc = eb_params['toolchain']
        toolchain = f"{tc['name']}-{tc['version']}".lower()
        if args.name.lower() not in name:
            continue
        if args.toolchain:
            if args.compatible:
                compat_tcs = [f"{t['name']}-{t['version']}" for t in get_toolchain_hierarchy(tc)]
                matching_tcs = [c for c in compat_tcs if args.toolchain in c.lower()]
                if not len(matching_tcs):
                    continue
            elif args.toolchain not in toolchain:
                continue
        # TODO: handle NOT parsing args.compat:
        print(eb_name, f"({', '.join(matching_tcs)})")