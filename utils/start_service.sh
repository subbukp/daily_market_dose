#!/bin/bash

sleep 30

# Kill existing sessions if any
tmux kill-server 2>/dev/null

sleep 2

# Session 1: ngrok
tmux new-session -d -s ngrok
sleep 1
tmux send-keys -t ngrok "ngrok http --url=misapprehensively-fleshliest-michelina.ngrok-free.dev 2001" Enter

# Session 2: main app
tmux new-session -d -s market
sleep 1
tmux send-keys -t market "/home/ps/daily_market_dose/.venv/bin/python3.12 /home/ps/daily_market_dose/main.py" Enter

# Session 3: mcp server
tmux new-session -d -s mcp
sleep 1
tmux send-keys -t mcp "/home/ps/daily_market_dose/.venv/bin/python3.12 /home/ps/daily_market_dose/mcp_server.py" Enter