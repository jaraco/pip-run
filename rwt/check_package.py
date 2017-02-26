import pip
from contextlib import redirect_stdout
import os
import re
"""
This helps use the methods from pkg-config (github.com/matze/pkgconfig) without having to make changes to environment
"""

def get_installed_packages():
	with redirect_stdout(open('pipListFile', "w")):
		pip.main(["list", "--format=legacy"])

	f = open('pipListFile', 'r')
	piplist = f.readlines()
	pipdict = {}
	for i in range(len(piplist)):
		package = piplist[i]
		package = package[:-1]
		packageSplit = package.split(" ")
		packageSplit = packageSplit[:2]
		packageSplit[1] = packageSplit[1].replace("(","")
		packageSplit[1] = packageSplit[1].replace(")","")
		pipdict[packageSplit[0]] = packageSplit[1]
	os.remove('pipListFile')
	return pipdict

def _compare_versions(v1, v2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]

    n1 = normalize(v1)
    n2 = normalize(v2)

    return (n1 > n2) - (n1 < n2)

def _split_version_specifier(spec):
    """
    Splits version specifiers in the form ">= 0.1.2" into ('0.1.2', '>=')
    """
    m = re.search(r'([<>=]?=?)?\s*((\d*\.)*\d*)', spec)
    return m.group(2), m.group(1)


def installed(package, version, pipdict):
    """
    Check if the package meets the required version.
    """
    if package not in pipdict:
        return False

    number, comparator = _split_version_specifier(version)
    modversion = pipdict[package]

    try:
        result = _compare_versions(modversion, number)
    except ValueError:
        msg = "error with version specifier, installing {0} anyway".format(package)
        return False

    if comparator in ('', '=', '=='):
        return result == 0

    if comparator == '>':
        return result > 0

    if comparator == '>=':
        return result >= 0

    if comparator == '<':
        return result < 0

    if comparator == '<=':
        return result <= 0

pipdict = get_installed_packages()
print(installed("pandas", ">= 2.8", pipdict))