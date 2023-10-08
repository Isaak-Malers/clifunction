![Build](https://github.com/Isaak-Malers/DecoratorCLI/actions/workflows/PythonApplication/badge.svg)


# DecoratorCLI
I wanted Cake, but in python.  This is currently a minimum viable product.  Check back for more features.

# Project Goals:
* Use modern python language features to make invoking python functions from the command line easy.  familiar CLI options like "Man" or "Help" should be populated automatically from type hints and doc strings.

* Do not require an invocation wrapper.  Invoking functions in "myPythonFile.py" should look something like:  ./myPythonFile.py myFunction --myIntArgument=50 -b=True

* Include automatic type coersion based on type hints.  Invoking ./myPythonFile.py myFunction --myIntArgument=50 -b=True should convert 50 to an int, and True to a bool

* Provide defaults, but remain un-oppinionated about invokation format.  It should be easy to extend the project to handle other arugment formats such as:  ./myPythonFile.py myFunction myIntArgument:50, b:True

* Provide a useful utility to as large a target auidience as possible.  This project should be approachable for a sophmore in a non CS related STEM field.  Errors should provide hints as to how to resolve issues.

* Enable complex projects with lots of functions/targets to be well organized.  Target annotations from multiple files should build a nice directory/tree structured organized man/help page, and be addressable by directory or directly if possible, eg:  ./myMainPythonFile.py myImportedModule.mySecondaryFunction --myIntArgument=50 -b=True

* These goals should be implemented with a single "@target" Annotation that takes no arguments.  It should be extremely easy to add to existing code/projects


# Stretch Project Goals:
* Provide Additional arguments to the @target annotation so that common tasks don't require bespoke coding.  These arguments will be "Mixed In" to the documentation and parsing for a particular targeted function

* Concurrency argument (defaults to 1).  Use the Threading library to spin up as many concurrent invocations of a task as desired.  This would enable easy multi-proccessing

* Home Directory Argument.  Make a particular function always run from within a particular path.

* Required Files Argument.  Make a target require a file by moniker (such as "config.json").  And then instead of getting the path to the file just get the string of the file contents instead.
