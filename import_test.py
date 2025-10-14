import sys, traceback, os
print('cwd:', os.getcwd())
print('sys.path[0]:', sys.path[0])
print('\n-- sys.path (first 20 entries) --')
for i, p in enumerate(sys.path[:20]):
    print(i, p)
print('\n-- sys.modules keys containing utils --')
print([k for k in sys.modules.keys() if 'utils' in k.lower()])
try:
    import utils
    print('\nImported utils:', utils)
    print('utils.__file__:', getattr(utils, '__file__', None))
    print('utils.__package__:', getattr(utils, '__package__', None))
except Exception as e:
    print('\nImport error:')
    traceback.print_exc()
