# tumbl-down

An automatic image downloader for Tumblr blogs and other image-focused sites.
The program uses its own dedicated parser, using web scraping and public API that doesn't require tokens.

# Dependencies

This project is built on latest Python 3 version (currently 3.9), which you need in order to test and run this program.
Backwards compatibility towards old Python 3 or Python 2 versions is not considered; continue at your own risk.

# Setting up virtualenv

This project uses python virtualenv for dependency management.
This set-up needs to be done only once, and any subsequent python executions are to be done inside the venv.
To set up, on the root project directory, run:

> virtualenv -p python3 venv

You may also replace `venv` with the name of your choice. Also replace every subsequent occurrences of `venv` with your name of choice.

Enter `source venv/bin/activate` on your terminal to enable virtualenv before proceeding to the next step.

## Install dependencies

To install dependencies, run:

> pip install -r requirements.txt

**Note:** It is possible to forgo creating virtual environment and install dependencies in your bare OS; However, it is recommended to use virtualenv and install dependencies there, to avoid dependency version conflicts or other complications arising from shared libraries.

# Running

Enter virtualenv by entering `source venv/bin/activate` on your terminal, if applicable.
On the root project directory, run `python tumbl-down.py [options] <service> <account_id...>` (values in <> are mandatory).
To see available options, run `python tumbl-down.py -h`.

# Testing
 
Enter virtualenv by entering `source venv/bin/activate` on your terminal, if applicable.
On the root project directory, run `python -m unittest <test_package_name>`.
For example, to run test file `test/tumblr_feed.py`, run `python -m unittest test.tumblr_feed`.

# License

This project is licensed under BSD (3-clause).
