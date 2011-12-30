import common
import seqlablib.report

import test_mdx

def test_subdirs_for_summary():
    m = test_mdx.MockMDX()
    assert seqlablib.report.subdirs_for_summary('data/workups', m) == \
        [(test_mdx.ws[0],'W01_JENKINS',False),
         (test_mdx.ws[2],'TH3_MOZART',True)]


test_subdirs_for_summary()
