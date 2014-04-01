Usage: python includes.py library_includes application_includes winheaders.txt

The script includes.py finds out what application files include library headers
that transitively includes windows.h or another Windows header.

library_includes is the output from `grep -R -n include .` in the directory
specified by Boost as the include dir.
`boost-1_44_64_includes.txt` is an example (Boost 1.44 on Windows 64-bit).

application_includes is the output from `grep -R -n include .` in your
application directory.
`app_includes.txt` is an example (TPIE).

winheaders.txt contains the offending headers (for instance the headers in the
Windows API).
