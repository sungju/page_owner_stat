import sys
import operator
from optparse import OptionParser

alloc_by_dict = {}
alloc_module_dict = {}

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


def handle_a_file(filename, options):
    with open(filename, 'r') as f:
        while True:
            by_whom = ""
            mod_name = ""
            line = f.readline()
            if not line:
                break
            
            if ("times," in line) and ("pages," in line):
                words = line.split()
                pages = int(words[2])
                by_whom = words[6]
                line = f.readline()
                if "mask 0x6646ca" in line:
                    by_whom = "hugepages"
            elif ("times:" in line):
                words = line.split()
                times = int(words[0])
                words = f.readline().split(",")
                pages = 2**int(words[0].split()[-1])
                pages = pages * times
                f.readline() # skip info line
                while True:
                    line = f.readline().strip()
                    if ("+0x" not in line):
                        break
                    by_whom = by_whom + "\n\t" + line
                    if "[" in line and mod_name == "":
                        mod_name = line[line.find("[") + 1:-1]

            alloc_pages = pages
            if by_whom != "":
                if by_whom in alloc_by_dict:
                    pages = pages + alloc_by_dict[by_whom]

                alloc_by_dict[by_whom] = pages

            if mod_name != "":
                pages = alloc_pages
                if mod_name in alloc_module_dict:
                    pages = pages + alloc_module_dict[mod_name]

                alloc_module_dict[mod_name] = pages


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
            print("%10s : %s" % (get_size_str(pages * 4096), by_whom))
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
        print("\nTotal allocated size : %s" % (get_size_str(sum_size * 4096)))

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
            print("%10s : %s" % (get_size_str(pages * 4096), mod_name))
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
        print("\nTotal allocated by modules : %s" % (get_size_str(sum_size * 4096)))


def page_owner_stat():
    op = OptionParser()
    op.add_option("-r", "--reverse", dest="reverse", default=0,
            action="store_true",
            help="Show in reverse")

    op.add_option("-a", "--all", dest="all", default=0,
            action="store_true",
            help="Show all list")

    (o, args) = op.parse_args()

    for arg in args:
        handle_a_file(arg, o)


if ( __name__ == '__main__'):
    page_owner_stat()
