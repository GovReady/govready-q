# from inspect import isclass
# from pkgutil import iter_modules
# from pathlib import Path
# from importlib import import_module
#
# # iterate through the modules in the current package
# package_dir = Path(__file__).resolve().parent
#
# for (_, module_name, _) in iter_modules([Path(__file__).parent]):
#     # import the module and iterate through its attributes
#     module = import_module("." + module_name, package=__package__)
#     print(f'importing module {module}')
#     for attribute_name in dir(module):
#         attribute = getattr(module, attribute_name)
#         # check if the attribute is a class
#         if isclass(attribute):
#             # print the class name
#             print(attribute.__name__)

# references
# - https://julienharbulot.com/python-dynamical-import.html