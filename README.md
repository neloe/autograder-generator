# autograder-generator

This python script allows you to choose a gradle project (that follows the structure Netbeans defaults to) that uses JUnit4.
It scans the project for the name of the tests and generates the GitHub Classroom autograding configuration files in the repo.
This allows you to create the assignments with autograding baked in without setting up running individual tests.

Right now this program sets each test to 1 point since GHCR doesn't allow fractions of points in a given test.  
The Total Points field currently does nothing, but if the fractional points support is added you will be able to specify the number of points to even spread across the tests.

This program does not require any additional python packages to run, just Python 3.
To run: `python generate-actions.py` or open and run in your favorite IDE.

TODO:
* Make button label clear after files are generated
* Add support for JUnit 5 (depends on how gradle works with that); perhaps autodetect?
