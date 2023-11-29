#!/bin/bash

session="celery"

tmux start-server

tmux new-session -d -s $session

tmux send-keys "cd .." C-m
tmux send-keys "export DEBUG=True" C-m
tmux send-keys "celery -A celery_app worker --loglevel=info --queues=default" C-m

tmux splitw -h

tmux send-keys "cd .." C-m
tmux send-keys "export DEBUG=True" C-m
tmux send-keys "celery -A celery_app flower --loglevel=INFO" C-m

tmux splitw -h

tmux send-keys "cd .." C-m
tmux send-keys "export DEBUG=True" C-m
tmux send-keys "celery -A celery_app beat -S celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler --loglevel=INFO" C-m

#tmux select-layout even-horizontal

tmux attach-session -t $session
