import common
from seqlab.mdx import Workup
import sqlite3

ws = [Workup(accession='A01', workup='W01', pat_name='Jenkins, John', amp_name='rpoB',path=None),
      Workup(accession='A02', workup='G12', pat_name='Lawes, William', amp_name='16S',path=None),
      Workup(accession='Q03', workup='TH3', pat_name='Mozart, Wolfgang', amp_name='rpoB',path=None)]

class MockMDX(object):
    seqkeys = ['alpha', 'beta', 'gamma']
    workups = ['W01','G12','TH3']
    def lookup_by_sequence_key(self, key):
        return ws[self.seqkeys.index(key)]
    def lookup_by_workup(self, key):
        return ws[self.workups.index(key)]
    def update_by_workup(self, key, path):
        w = ws[self.workups.index(key)]
        ws[self.workups.index(key)] = Workup(accession=w.accession,
                                             workup=w.workup,
                                             pat_name=w.pat_name,
                                             amp_name=w.amp_name,
                                             path=path)
