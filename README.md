# page_owner_stat
Analyse '/sys/kernel/debug/page_owner' to have better understanding of memory usage

It reads raw page_owner data or the data sorted with `page_owner_sort` and provide the usage summary.

You can run it like below.

~~~
python ./source/page_owner_stat.py page_owner_sorted.txt
~~~
