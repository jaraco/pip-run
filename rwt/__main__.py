import tokenize
import sys

from . import deps


def load(args):
	"""
	Load the script in args[0] and run it as if it had
	been invoked naturally.
	"""
	globals()['__file__'] = args[0]
	sys.argv[:] = args

	open_ = getattr(tokenize, 'open', open)
	script = open_(__file__).read()
	norm_script = script.replace('\\r\\n', '\\n')
	return compile(norm_script, __file__, 'exec')


if __name__ == '__main__':
	with deps.on_sys_path(sys.argv[1]):
		exec(load(sys.argv[2:]))
