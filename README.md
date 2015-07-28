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

Run the message queue worker:

        python manage.py celeryd


By default the message queue (using celery) uses the same database as
the site depends on. This makes it easy for local development.

To override this to use a RabbitMQ server or something like that set the
environment variable `BROKER_URL`. For example:

        export BROKER_URL="amqp://guest:guest@localhost:5672//"

Use locally
-----------

1. Add a `<script>` tag to your page for `collect.js`:

        <script>
        (function() {
        var s = document.createElement('script');
        s.src = 'http://127.0.0.1:8000/static/collect.js';
        s.async=true; s.onload=function() {
            Webalyzer('example.com');
        } document.head.appendChild(s)})();
        </script>

2. Hit your page(s)

3. Go to the collected analysis page: http://127.0.0.1:8000/analyzer/

There are configuration options available for when you initialize the
`Webalyzer` in that script snippet. For example, instead of:

        Webalyzer('example.com');

You can do this:

        Webalyzer('example.com', {
             doSend: function(html, url) {
                 if (getWeather() === 'raining') {
                     return false;
                 }
                 return true;
             },
             beforeSendHTML: function(html, url) {
                 return html.replace(/negative/g, 'positive');
             },
        });

The `doSend` function gives you an opportunity to cancel the sending,
by returning `false`. You could potentially use this to throttle some
of the traffic or perhaps you only want it sent depending on some other
condition.

The `beforeSendHTML` gives you an opportunity to change the HTML that's
going to be sent. For example, you might scrub something in the content.
