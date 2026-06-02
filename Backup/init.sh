#!/bin/sh

sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl restart flask
sudo systemctl restart control

sudo systemctl status nginx
sudo systemctl status flask
sudo systemctl status control