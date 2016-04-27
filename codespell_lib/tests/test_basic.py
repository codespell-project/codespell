import tempfile

from nose.tools import assert_equal

from codespell_lib import main


def test_basic():
    """Test some basic functionality"""
    assert_equal(main('_does_not_exist_'), 0)
    with tempfile.NamedTemporaryFile() as f:
        f.write('this is a test file\n'.encode('utf-8'))
        f.flush()
        assert_equal(main(f.name,), 0)
        f.write('abandonned'.encode('utf-8'))
        f.flush()
        assert_equal(main(f.name), 1)
