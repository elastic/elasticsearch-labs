#!/bin/sh
cd start
zip -r ../search-tutorial-starter.zip \
    search-tutorial/README.md \
    search-tutorial/LICENSE \
    search-tutorial/requirements.txt \
    search-tutorial/data.json \
    search-tutorial/.flaskenv \
    search-tutorial/app.py \
    search-tutorial/templates/* \
    search-tutorial/static/*
