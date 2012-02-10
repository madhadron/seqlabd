import common
import threading
import seqlab.placed
import time

seqlab.placed.daemonaction('data/seqlab.conf')


# def test_placed(tmpdir):
#     if tmpdir == None:
#         import py.path
#         tmpdir = py.path.local('data')
#     inboxdir = tmpdir.mkdir('source')
#     targetdir = tmpdir.mkdir('target')
#     exitevent = threading.Event()
#     threading.Thread(target=lambda: seqlab.placed.main('data/seqlab.conf',
#                                                   str(inboxdir),
#                                                   str(targetdir),
#                                                   exitevent)).start()
#     inboxdir.join('280.22708_H02_016.ab1').ensure(dir=False)
#     time.sleep(1)

#     t = time.localtime()
#     path = targetdir.join(time.strftime('%Y', t),
#                           time.strftime('%Y_%B', t), time.strftime('%Y_%m_%d', t),
#                           'H34908_MORRALL_alt_16s')
#     assert path.join('279.22708_G02_014.ab1').check(exists=1)
#     assert path.join('metadata.json').check(exists=1)
#     with open(str(path.join('metadata.json'))) as h:
#         j = json.load(h)
#         expected = {'amp_name': 'alt_16s',
#                     'specimen_description': 'BNE-FLAP',
#                     'seq_key': 22708,
#                     'accession': 'H34908',
#                     'specimen_category': None,
#                     'pat_name': 'MORRALL,MARK R',
#                     'tests': [['TSEXAM-BACTERIAL',
#                                'Tissue extract and amplify bacterial primers'],
#                               ['TSEXAM-AFB',
#                                'Tissue extract and amplify AFB primers'],
#                               ['TSEXAM-FUNGAL',
#                                'Tissue extract and amplify fungal primers']]}
#         assert j == expected
#     exitevent.set()

# test_placed(None)
