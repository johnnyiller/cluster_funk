from cluster_funk.core.utils import \
    get_subfolders, \
    find_nearest_root, \
    template_names, \
    job_names


import os
from mock import patch
from mock import MagicMock


def test_get_subfolders(tmp):

    mockroot = MagicMock(return_value=tmp)

    with patch('cluster_funk.core.utils.find_nearest_root', mockroot) as mocked:

        os.mkdir('.cf')
        os.mkdir('afolder')
        os.mkdir(os.path.join('afolder', '1'))
        os.mkdir(os.path.join('afolder', '2'))
        output = get_subfolders('afolder')
        assert output == ['1', '2']

        output = get_subfolders('nonsensefolder')
        assert output == []


def test_get_subfolders_without_root(tmp):

    mockroot = MagicMock(return_value=None)

    with patch('cluster_funk.core.utils.find_nearest_root', mockroot) as mocked:

        os.mkdir('afolder')
        os.mkdir(os.path.join('afolder', '1'))
        os.mkdir(os.path.join('afolder', '2'))
        output = get_subfolders('afolder')
        assert output == []


def test_find_nearest_root(tmp):
    os.mkdir('.cf')
    os.mkdir('afolder')
    os.mkdir(os.path.join('afolder', '1'))
    os.mkdir(os.path.join('afolder', '1', '2'))
    root_path = find_nearest_root(os.path.join(tmp, 'afolder', '1', '2'))
    assert root_path == tmp


def test_template_names():

    mockpaths = MagicMock(return_value=['one.yml', 'two.yaml', 'three.yaml'])

    with patch('cluster_funk.core.utils.get_subfolders', mockpaths) as mocked:
        output = template_names("someenv")
        mocked.assert_called_with("environments/someenv")
        assert output == ["one", "two", "three"]


def test_job_names():

    mockpaths = MagicMock(return_value=['one', 'two', 'three'])

    with patch('cluster_funk.core.utils.get_subfolders', mockpaths) as mocked:
        output = job_names()
        mocked.assert_called_with("jobs")
        assert output == ["one", "two", "three"]
