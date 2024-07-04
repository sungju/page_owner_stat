# page_owner_stat
Analyse '/sys/kernel/debug/page_owner' to have better understanding of memory usage

It reads raw page_owner data or the data sorted with `page_owner_sort` and provide the usage summary.

You can run it like below.

~~~
python ./source/page_owner_stat.py page_owner_sorted.txt
~~~

### Notes

If you are running the script in a different system from the data source, you may need to set page size by yourself.

For example, for the data from `ppc64le`, you can use `-p 65536` like below.

~~~
python ./source/page_owner_stat.py -p 65536 page_owner_sorted.txt
~~~
