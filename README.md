Webalyzer - Collects web code for analysis and reporting
========================================================

Webalyzer helps you collect HTML from live web pages and run analysis
on the the HTML in batches for reporting purposes.


Requirements
------------

* PostgreSQL
* Python & pip
* node & npm

Setup
-----

Install everything in the `requirements.txt` file:

        pip install -r requirements.txt

Ideally you should use [`peep`](https://pypi.python.org/pypi/peep) to
assure you don't install anything that hasn't been vetted for:

        pip install peep
        peep install -r requirements.txt

For the CSS parsing you need the [crass](https://github.com/mattbasta/crass) nodejs module installed
and made available on the `PATH`:

        npm install -g crass yuglify

Create postgres database:

        createdb webalyzer

Add default environment variable settings in `.env`:
        
        SECRET_KEY=terrible-secret
        DEBUG=True
        ALLOWED_HOSTS=*
        DATABASE_URL=postgresql://<username>@localhost:5432/webalyzer

Run migrations:

        python manage.py migrate

Collect static assets:

        python manage.py collectstatic

Add `webalyzer.dev` to your `/etc/hosts` file:

        127.0.0.1 webalyzer.dev

Run
---

Use the django runserver:

        python manage.py runserver

Use locally
-----------

1. Add a `<script>` tag to your page for `collect.js`:

        <script src="http://webalyzer.dev/static/collect.js"
        data-webalyzer="example.com"></script>

2. Hit your page(s)

3. Go to the collected analysis page: http://webalyzer.dev/analyzer/

4. Enter your `data-webalyzer` attribute value and click "Start Analysis"
