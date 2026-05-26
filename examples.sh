#!/bin/bash
set -e
BASE_URL="http://localhost:5000"

echo "Health"
curl -s "$BASE_URL/health" | python3 -m json.tool

echo "\nRoot"
curl -s "$BASE_URL/" | python3 -m json.tool

echo "\nWeather Madrid"
curl -s "$BASE_URL/weather?city=Madrid" | python3 -m json.tool

echo "\nWeather coords Madrid"
curl -s "$BASE_URL/weather?lat=40.4168&lon=-3.7038" | python3 -m json.tool

echo "\nMultiple"
curl -s -X POST "$BASE_URL/weather/multiple" -H 'Content-Type: application/json' -d '{"cities":["Madrid","London"]}' | python3 -m json.tool
