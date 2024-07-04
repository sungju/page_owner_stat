# page_owner_stat

## Analyse page_owner data

### Example


~~~
$ python page_owner_stat.py page_ower.txt

...
  12.8 GiB : 
	[<ffffffffc0871cbd>] arc_get_data_abd.isra.33+0x3d/0x60 [zfs]
	[<ffffffffc0871d31>] arc_hdr_alloc_abd+0x51/0xc0 [zfs]
	[<ffffffffc0871e8a>] arc_hdr_alloc+0xea/0x170 [zfs]
	[<ffffffffc0874e22>] arc_read+0x632/0x10e0 [zfs]
	[<ffffffffc087eb8c>] dbuf_read_impl+0x20c/0x670 [zfs]
	[<ffffffffc087fd5a>] dbuf_read+0xca/0x5e0 [zfs]
	[<ffffffffc088c4a4>] dmu_buf_hold_array_by_dnode+0x114/0x4c0 [zfs]

Total allocated size : 42.2 GiB (44201540 kB)


By allocated modules
====================

 ... < skipped  24  items > ...
   4.3 MiB : vmw_pvscsi
   8.3 MiB : sunrpc
  10.1 MiB : vmwgfx
  10.7 MiB : ttm
  26.1 MiB : iscsi_scst
  27.4 MiB : vmxnet3
 129.6 MiB : scst
   2.0 GiB : xfs
   2.3 GiB : spl
  31.1 GiB : zfs

Total allocated by modules : 35.6 GiB (37355284 kB)

Notes: Calculation was done with pagesize=4096
~~~
