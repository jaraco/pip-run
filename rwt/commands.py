def parse_script_args(args):
	"""
	Separate the command line arguments into arguments for pip
	and arguments to invoke a script.

	>>> parse_script_args(['foo', '--', 'bar'])
	(['foo'], ['bar'])

	>>> parse_script_args(['foo', 'bar'])
	Traceback (most recent call last):
	...
	ValueError: '--' is not in list
	"""
	pivot = args.index('--')
	return args[:pivot], args[pivot+1:]
