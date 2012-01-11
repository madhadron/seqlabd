import common
import seqlab.refs
import pytest

def test_ref_put_get():
    r = seqlab.refs.Ref()
    with pytest.raises(ValueError):
        r.get()
    assert r.put(3) == None
    assert r.get() == 3

def test_get_fieldref():
    r = seqlab.refs.Ref()
    r.put({'a': 3})
    assert r.get() == {'a': 3}
    fr = r['a']
    assert fr.get() == 3
    assert fr.put(5) == 3
    assert fr.get() == 5
    assert r.get() == {'a': 5}
    
