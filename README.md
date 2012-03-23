seqlabd 1.0 - Analysis tools for the clinical sequencing lab
=============================================================

by Fred Ross <madhadron@gmail.com>

Overview
--------

seqlabd is a body of code, plus three daemons and one shell command, meant to speed up the workflow in the UWMC molecular microbiology lab. It is licensed under the GNU General Public License, version 3.

Its code follows a fairly standard organization of a Python project:

~~~
README.md    -- what you're reading now
LICENSE      -- a copy of the GNU GPL3
setup.py     -- Python distutils build script
bin/         -- executables for use in the shell
rc-scripts/  -- template rc scripts for integrating the daemons into SysV init
seqlab/      -- source code
test/        -- unit tests
~~~

The three daemons are placed, sequencereportd, and dailysummaryd. Each embodies one step in the workflow. The command, seqlab, provides manual access to many of the capabilities of the source code and lets users run the workflow steps manually if the daemons are down.

- placed monitors a directory for new AB1 files from the sequencer, looks up their metadata in the lab's MySQL database, then moves the AB1 files into the lab's long term storage hierarchy along with a JSON file giving the metadata.
- sequencereportd monitors the long term storage hierarchy for new AB1 files and tries to assemble pairs of strands, BLASTs the results, and writes an HTML file in the same directory summarizing its work.
- dailysummaryd monitors the same hierarchy, but whenever an HTML file is written by sequencereportd, it rebuilds an HTML in the directory above summarizing all the runs in subdirectories (this corresponds to one day's runs in the hierarchy).

Installation
------------

You must have Python 2.7 with numpy, BioPython, Cython, pyinotify, pydaemonize, and oursql to run seqlabd. For running its test suite, you will also need pytest. Note that if you're installing in a virtualenv environment, oursql will fail unless you install as sudo. It insists on putting a library in /usr/local/lib. Besides that, all of these packages should install from PyPI with pip. You will also need ssearch36 from FASTA 3.6 installed.

You must have the the molmicro MySQL database set up and reachable by the user that the daemons will run as. In it, you need to have a view like the following:

~~~
CREATE VIEW `workups` AS 
select `mdx`.`Accession` AS `accession`,
       `mdx`.`Workup Number` AS `workup`,
       `mdx`.`Patient Name` AS `pat_name`,
       `ac`.`Amp Name` AS `amp_name`,
       `sr`.`Seq Result ID` AS `seq_key`,
       `mdx`.`Specimen Description` AS `specimen_description`,
       `sc`.`desc` AS `specimen_category`,
       `mdx`.`Test 1` AS `test1_code`,
       `ot1`.`Test Name` AS `test1_name`,
       `mdx`.`Test 2` AS `test2_code`,
       `ot2`.`Test Name` AS `test2_name`,
       `mdx`.`Test 3` AS `test3_code`,
       `ot3`.`Test Name` AS `test3_name`,
       `mdx`.`Test 4` AS `test4_code`,
       `ot4`.`Test Name` AS `test4_name`,
       `mdx`.`Test 5` AS `test5_code`,
       `ot5`.`Test Name` AS `test5_name`,
       `mdx`.`Test 6` AS `test6_code`,
       `ot6`.`Test Name` AS `test6_name`,
       `mdx`.`Test 7` AS `test7_code`,
       `ot7`.`Test Name` AS `test7_name`,
       `mdx`.`Test 8` AS `test8_code`,
       `ot8`.`Test Name` AS `test8_name`,
       `mdx`.`Test 9` AS `test9_code`,
       `ot9`.`Test Name` AS `test9_name` 
from ((((((((((((`seq result` `sr` join `amp categories` `ac` on((`sr`.`Amp Category ID` = `ac`.`Amp Category ID`))) join `mdx` on((`sr`.`MDX ID` = `mdx`.`MDX ID`))) left join `specimen_category` `sc` on((`sc`.`index` = `mdx`.`specimen_category`))) left join `orderable test` `ot1` on((`ot1`.`Test Code` = `mdx`.`Test 1`))) left join `orderable test` `ot2` on((`ot2`.`Test Code` = `mdx`.`Test 2`))) left join `orderable test` `ot3` on((`ot3`.`Test Code` = `mdx`.`Test 3`))) left join `orderable test` `ot4` on((`ot4`.`Test Code` = `mdx`.`Test 4`))) left join `orderable test` `ot5` on((`ot5`.`Test Code` = `mdx`.`Test 5`))) left join `orderable test` `ot6` on((`ot6`.`Test Code` = `mdx`.`Test 6`))) left join `orderable test` `ot7` on((`ot7`.`Test Code` = `mdx`.`Test 7`))) left join `orderable test` `ot8` on((`ot8`.`Test Code` = `mdx`.`Test 8`))) left join `orderable test` `ot9` on((`ot9`.`Test Code` = `mdx`.`Test 9`)));
~~~

This view is the entire interface to the database. As long as it is stable, anything else can change. The daemons all share a common configuration file, which specifies how to connect to the database. The relevant lines are

~~~
# Connection information
db_server = localhost
db_port = 3306
db_name = mdx
db_username = seqlab
# Passwords are not stored here in plain text. db_credentials points to a text 
# file containing the password (and nothing else). Any leading or trailing 
# whitespace is ignored. The file should be readable only by the daemon's user any 
# other authorized to access the database.
db_credentials = /path/to/credential/file
~~~

To install seqlabd, in its directory run

~~~
python setup.py build
python setup.py install
~~~

You will need to write a configuration file and set up the RC scripts. The default location for the configuration file is /etc/seqlab.conf, but you can put it anywhere and run the daemons with '-c /path/to/config'. Here is an example configuration file:

~~~
[default]
target_path = /path/to/target
inbox_path = /path/to/inbox

db_server = localhost
db_port = 3306
db_username = root
db_credentials = data/dbcredential
db_name = mdx
~~~

The database lines were explained above. inbox_path is where new AB1 files will be deposited by users to be processed and where placed should pull its input from. target_path is the full path to the directory containing subdirectories named by year in the molmicro lab's file hierarchy.

In rc-scripts are example scripts that you would put in /etc/rc.d/init.d. You probably need to edit them to get the paths right. For more information, see 

/usr/share/doc/initscripts-9.03.27/sysvinitfiles

on Red Hat systems, or the article 

https://www.linux.com/learn/tutorials/442412-managing-linux-daemons-with-init-scripts

Subcommands of seqlab
---------------------

seqlab dispatches to various subcommands the way git does. There are two kinds of subcommands. The first kind recapitulates the behavior of the daemons:

- place: Put an AB1 file into the proper place in the file hierarchy, and write a JSON file of workup metadata.
- sequencereport: Write an HTML report from two AB1 files and a JSON file of metadata.
- dailysummary: Write an HTML report summarizing the sequence reports in subdirectories of the target directory.

The second kind provides access to some of the functionality of the source code on the command line:

- renderab1: Produce an HTML file from an AB1 file showing the traces, confidences, and bases.
- metadata: Write a JSON file of the workup metadata that placed would extract when trying to place a file.
- assemble: Assemble two AB1 files and metadata as sequencereport would, and write the assembly into a bzipped JSON file for additional processing.
- render: Render an assembly to HTML.
- addsequence: Add additional sequences to an assembly.
- blast: BLAST a line in an assembly and write the results as XML and JSON.
- statistics: Calculate statistics on a pair of lines in an assembly.

