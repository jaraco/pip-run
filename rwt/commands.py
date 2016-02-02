def parse_script_args(args):
	"""
	Separate the command line arguments into arguments for pip
	and arguments to Python.

	>>> parse_script_args(['foo', '--', 'bar'])
	(['foo'], ['bar'])

	>>> parse_script_args(['foo', 'bar'])
	(['foo', 'bar'], [])
	"""
	try:
		pivot = args.index('--')
	except ValueError:
		pivot = len(args)
	return args[:pivot], args[pivot+1:]
