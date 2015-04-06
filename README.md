Webalyzer - Collects web code for analysis and reporting
========================================================

Webalyzer helps you collect HTML from live web pages and run analysis
on the the HTML in batches for reporting purposes.


Requirements
------------

Everything in the `requirements.txt` file:

        pip install -r requirements.txt

Ideally you should use [`peep`](https://pypi.python.org/pypi/peep) to
assure you don't install anything that hasn't been vetted for:

        pip install peep
        peep install -r requirements.txt


For the CSS parsing you need the [crass](https://github.com/mattbasta/crass) nodejs module installed
and made available on the `PATH`:

        npm install -g crass

        
