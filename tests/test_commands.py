from pip_run import commands


def test_check_ipython_no_ipython_arg():
    pip_args, py_args = ['foo'], ['bar']
    new_pip_args, new_py_args = commands.check_ipython(pip_args, py_args)
    assert new_pip_args == pip_args
    assert new_py_args == py_args


def test_check_ipython_ipython_arg_no_python_args():
    pip_args, py_args = ['ipython', 'foo'], []
    new_pip_args, new_py_args = commands.check_ipython(pip_args, py_args)
    assert set(new_pip_args) == {'foo', 'ipython'}
    assert new_py_args == ['-m', 'IPython']


def test_check_ipython_ipython_arg_python_args():
    pip_args, py_args = ['ipython', 'foo'], ['bar']
    new_pip_args, new_py_args = commands.check_ipython(pip_args, py_args)
    assert set(new_pip_args) == {'foo', 'ipython'}
    assert new_py_args == py_args
