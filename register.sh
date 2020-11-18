#!/bin/sh
curl -X POST   http://127.0.0.1:8001/register_with   -H 'Content-Type: application/json'   -d '{"node_address": "http://127.0.0.1:8002"}'
curl -X POST   http://127.0.0.1:8001/register_with   -H 'Content-Type: application/json'   -d '{"node_address": "http://127.0.0.1:8003"}'
curl -X POST   http://127.0.0.1:8001/register_with   -H 'Content-Type: application/json'   -d '{"node_address": "http://127.0.0.1:8004"}'
curl -X POST   http://127.0.0.1:8002/register_with   -H 'Content-Type: application/json'   -d '{"node_address": "http://127.0.0.1:8003"}'
curl -X POST   http://127.0.0.1:8002/register_with   -H 'Content-Type: application/json'   -d '{"node_address": "http://127.0.0.1:8004"}'
curl -X POST   http://127.0.0.1:8003/register_with   -H 'Content-Type: application/json'   -d '{"node_address": "http://127.0.0.1:8004"}'