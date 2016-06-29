# flask-cookiecutter
My take on a cookiecutter project for a blank Flask site.

### Build Status
[![Build Status](https://travis-ci.org/smeggingsmegger/flask-cookiecutter.svg?branch=master)](https://travis-ci.org/smeggingsmegger/flask-cookiecutter)

### Getting Started

You'll need cookiecutter:

`pip install cookiecutter`

Now you can initialize a blank Flask project just by creating a new copy:

`cookiecutter https://github.com/smeggingsmegger/flask-cookiecutter`

### What's Included

My Flask template makes use of the following Flask plugins:

- Flask-Assets
- Flask-Cache
- Flask-DebugToolbar
- Flask-Login
- Flask-SQLAlchemy
- Flask-Script
- Flask-WTF
- Flask-Mail
- Flask-Migrate
- Flask-Permissions

Flask-WTF is only used for the basic login form that is included. You will want to prune and curate that list as you see fit.

(For instance, if you aren't sending emails you don't need Flask-Mail)

I just included the most common plugins that I use on a regular basis to create, what I think is, a nice blend of the micro-framework and the "batteries included" approach.
