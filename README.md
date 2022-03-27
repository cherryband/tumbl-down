# tumbl-down

An automatic image downloader for Tumblr blogs and other image-focused sites.
The program uses its own dedicated parser, using web scraping and public API that doesn't require tokens.

# Dependencies

This project is built on latest Python 3 version (currently 3.9), which you need in order to test and run this program.
Backwards compatibility towards old Python 3 or Python 2 versions is not considered; continue at your own risk.

# Setting up virtualenv

This project uses python virtualenv for dependency management.
The setup needs to be done only once, and any subsequent python executions are done inside the venv.
To set up, on the root project directory, run:

> virtualenv -p python3 venv

You may also replace `venv` with the name of your choice. Also replace every subsequent occurances of `venv` with your name of choice.

Enter `source venv/bin/activate` on your terminal to enable virtualenv before proceeding to next step.

## Install dependencies

To install dependencies, run:

> pip install -r requirements.txt

**Note:** It is possible to forgo creating virtual environment and install dependencies in your bare OS; However, it is recommended to use virtualenv and install dependencies there, to avoid dependency version conflicts or other complications arising from shared libraries.

# Running

The program is in development and is not functional. TODO.

# Testing
 
Enter virtualenv by entering `source venv/bin/activate` on your terminal, if applicable.
On the test directory, run `python <test_filename>.py`.

# License

This project is licenced under BSD (3-clause).
