"""
Daemon to monitor a file hierarchy and create sequence reports.

Any time 'workup.json' or any .ab1 file is added to a directory, check
if there is a usable set of files in that directory. If so, generate a
sequence report for them.
"""
