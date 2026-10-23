def test_python_runtime():
    import sys

    assert sys.version_info.major == 3
    assert sys.version_info.minor == 11
