Webalyzer - Collects web code for analysis and reporting
========================================================

Webalyzer helps you collect HTML from live web pages and run analysis
on the the HTML in batches for reporting purposes.


Requirements
------------

* PostgreSQL
* Redis
* Python & pip
* node & npm

Setup
-----

1. Start your PostgreSQL and Redis servers

2. Create and activate a virtual environment:

        virtualenv venv
        source venv/bin/activate

3. Install python requirements from the `requirements.txt` file:

        pip install -r requirements.txt

Ideally you should use [`peep`](https://pypi.python.org/pypi/peep) to
assure you don't install anything that hasn't been vetted for:

        pip install peep
        peep install -r requirements.txt

4. Install node requirements:

        npm install -g crass yuglify

5. Create postgres database:

        createdb webalyzer

6. Add default environment variable settings in `.env` file:
        
        SECRET_KEY=terrible-secret
        DEBUG=True
        ALLOWED_HOSTS=*
        DATABASE_URL=postgresql://<username>@localhost:5432/webalyzer

7. Run migrations:

        python manage.py migrate

Run
---

Run the django server:

        python manage.py runserver

Run the Alligator worker:

        python manage.py run-gator

Use locally
-----------

1. Add a `<script>` tag to your page for `collect.js`:

        <script src="http://127.0.0.1:8000/static/collect.js"
        data-webalyzer="example.com"></script>

2. Hit your page(s)

3. Go to the collected analysis page: http://127.0.0.1:8000/analyzer/

4. Enter your `data-webalyzer` attribute value (e.g., `example.com`) and click "Start Analysis"
