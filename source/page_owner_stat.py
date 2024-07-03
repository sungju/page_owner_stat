#!/usr/bin/env/python
# --------------------------------------------------------------------
# Author: Daniel Sungju Kwon
#
# Analyse page_owner data and make summary
#
# Contributors:
# --------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import sys
import os
import operator
import subprocess
from optparse import OptionParser

def get_size_str(size, coloring = False):
    size_str = ""
    if size > (1024 * 1024 * 1024): # GiB
        size_str = "%.1f GiB" % (size / (1024*1024*1024))
        if coloring == True:
            crashcolor.set_color(crashcolor.RED)
    elif size > (1024 * 1024): # MiB
        size_str = "%.1f MiB" % (size / (1024*1024))
        if coloring == True:
            crashcolor.set_color(crashcolor.MAGENTA)
    elif size > (1024): # KiB
        size_str = "%.1f KiB" % (size / (1024))
        if coloring == True:
            crashcolor.set_color(crashcolor.GREEN)
    else:
        size_str = "%.0f B" % (size)

    return size_str


alloc_by_dict = {}
alloc_type_dict = {}
alloc_module_dict = {}
page_size=4096

def handle_a_file(filename, options):
    if not os.path.isfile(filename):
        print("File '%s' does not exist" % (filename))
        sys.exit(1)

    global page_size
    try:
        if options.pagesize != 0:
            page_size = options.pagesize
        else:
            page_size = int(subprocess.check_output(['getconf', 'PAGESIZE']))
    except Exception as e:
        print(e)
        pass
    with open(filename, 'r') as f:
        while True:
            by_type = ""
            by_whom = ""
            mod_name = ""
            line = f.readline()
            if not line:
                break
            
            if ("times," in line) and ("pages," in line):
                words = line.split()
                times = int(words[0])
                pages = int(words[2])
                by_type = words[6]
                while True:
                    line = f.readline().rstrip()
                    if line.startswith(" "):
                        break

                while True:
                    if ("0x" not in line):
                        break
                    by_whom = by_whom + "\n\t" + line
                    if "[" in line and mod_name == "":
                        mod_name = line[line.find("[") + 1:-1]
                    line = f.readline().strip()

            else:
                words = line.split()
                if ("times:" in line):
                    times = int(words[0])
                    words = f.readline().split(",")
                else:
                    times = 1
                    words = line.split(",")

                if (len(line.strip()) == 0):
                    continue
                #print("<%s, %d>" % (line.strip(), f.tell()))
                if words[0].startswith("Page allocated via order"):
                    by_type = ""
                else:
                    by_type = words[3].split()[2]
                pages = 2**int(words[0].split()[-1])
                pages = pages * times
                while True:
                    line = f.readline().rstrip()
                    if line.startswith(" "):
                        break

                while True:
                    line = f.readline().strip()
                    if len(line) == 0:
                        break
                    by_whom = by_whom + "\n\t" + line
                    words = line.split()
                    if "[" in words[-1] and mod_name == "":
                        mod_name = words[-1][1:-1]


            alloc_pages = pages
            if by_whom != "":
                if by_whom in alloc_by_dict:
                    pages = pages + alloc_by_dict[by_whom]

                alloc_by_dict[by_whom] = pages

            if by_type != "":
                pages = alloc_pages
                if by_type in alloc_type_dict:
                    pages = pages + alloc_type_dict[by_type]

                alloc_type_dict[by_type] = pages

            if mod_name != "":
                pages = alloc_pages
                if mod_name in alloc_module_dict:
                    pages = pages + alloc_module_dict[mod_name]

                alloc_module_dict[mod_name] = pages


    if len(alloc_by_dict) > 0:
        print("By call trace")
        print("=============")
        sorted_usage = sorted(alloc_by_dict.items(),
                key=operator.itemgetter(1), reverse=options.reverse)
                        
        sum_size = 0
        print_count = 0
        total_count = len(sorted_usage) - 1
        if options.all:
            print_start = 0
            print_end = total_count
        else:
            if options.reverse:
                print_start = 0
                print_end = min(total_count, 10)
            else:
                print_start = total_count - 10
                if print_start < 0:
                    print_start = 0
                print_end = total_count

        skip_printed = False

        for by_whom, pages in sorted_usage:
            sum_size = sum_size + pages

            if print_start <= print_count <= print_end:
                print("\n%10s : %s" % (get_size_str(pages * page_size), by_whom))
            else:
                if len(sorted_usage) > 10:
                    if not skip_printed:
                        print("\n%15s %d %s" % (
                            "... < skipped ",
                            len(sorted_usage) - 10,
                            " items > ..."))
                    skip_printed = True

            print_count = print_count + 1

        if sum_size > 0:
            print("\nTotal allocated size : %s (%d kB)" % (get_size_str(sum_size * page_size), sum_size * page_size / 1024))


    if len(alloc_module_dict) > 0:
        print("\n")
        print("By allocated modules")
        print("====================")
        sorted_usage = sorted(alloc_module_dict.items(),
                key=operator.itemgetter(1), reverse=options.reverse)

        sum_size = 0
        print_count = 0
        total_count = len(sorted_usage) - 1
        if options.all:
            print_start = 0
            print_end = total_count
        else:
            if options.reverse:
                print_start = 0
                print_end = min(total_count, 10)
            else:
                print_start = total_count - 10
                if print_start < 0:
                    print_start = 0
                print_end = total_count

        skip_printed = False
        for mod_name, pages in sorted_usage:
            sum_size = sum_size + pages

            if print_start <= print_count <= print_end:
                print("%10s : %s" % (get_size_str(pages * page_size), mod_name))
            else:
                if len(sorted_usage) > 10:
                    if not skip_printed:
                        print("\n%15s %d %s" % (
                            "... < skipped ",
                            len(sorted_usage) - 10,
                            " items > ..."))
                    skip_printed = True

            print_count = print_count + 1

        if sum_size > 0:
            print("\nTotal allocated by modules : %s (%d kB)" % (get_size_str(sum_size * page_size), sum_size * page_size / 1024))


    if len(alloc_type_dict) > 0:
        print("\n")
        print("By allocation type")
        print("==================")
        sorted_usage = sorted(alloc_type_dict.items(),
                key=operator.itemgetter(1), reverse=options.reverse)

        sum_size = 0
        print_count = 0
        total_count = len(sorted_usage) - 1
        if options.all:
            print_start = 0
            print_end = total_count
        else:
            if options.reverse:
                print_start = 0
                print_end = min(total_count, 10)
            else:
                print_start = total_count - 10
                if print_start < 0:
                    print_start = 0
                print_end = total_count

        skip_printed = False
        for by_type, pages in sorted_usage:
            sum_size = sum_size + pages

            if print_start <= print_count <= print_end:
                print("%10s : %s" % (get_size_str(pages * page_size), by_type))
            else:
                if len(sorted_usage) > 10:
                    if not skip_printed:
                        print("\n%15s %d %s" % (
                            "... < skipped ",
                            len(sorted_usage) - 10,
                            " items > ..."))
                    skip_printed = True

            print_count = print_count + 1


def page_owner_stat():
    op = OptionParser()
    op.add_option("-r", "--reverse", dest="reverse", default=0,
            action="store_true",
            help="Show in reverse")

    op.add_option("-a", "--all", dest="all", default=0,
            action="store_true",
            help="Show all list")

    op.add_option("-p", "--pagesize", dest="pagesize", default=0,
            type=int, action="store",
            help="Set kernel pagesize. ex) ppc64le = 65536")

    (o, args) = op.parse_args()

    for arg in args:
        handle_a_file(arg, o)


if ( __name__ == '__main__'):
    page_owner_stat()
