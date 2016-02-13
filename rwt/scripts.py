import sys
import ast
import tokenize


def read_deps(script, var_name='__requires__'):
	"""
	Given a script path, read the dependencies from the
	indicated variable (default __requires__). Does not
	execute the script, so expects the var_name to be
	assigned a static list of strings.
	"""
	with open(script) as stream:
		return _read_deps(stream.read())


def _read_deps(script, var_name='__requires__'):
	"""
	>>> _read_deps("__requires__=['foo']")
	['foo']
	"""
	mod = ast.parse(script)
	node, = (
		node
		for node in mod.body
		if isinstance(node, ast.Assign)
		and len(node.targets) == 1
		and node.targets[0].id == var_name
	)
	return ast.literal_eval(node.value)


def run(cmdline):
	"""
	Execute the script as if it had been invoked naturally.
	"""
	namespace = dict()
	filename = cmdline[0]
	namespace['__file__'] = filename
	namespace['__name__'] = '__main__'
	sys.argv[:] = cmdline

	open_ = getattr(tokenize, 'open', open)
	script = open_(filename).read()
	norm_script = script.replace('\\r\\n', '\\n')
	code = compile(norm_script, filename, 'exec')
	exec(code, namespace)
