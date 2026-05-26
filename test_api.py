#!/usr/bin/env python3
import os
import sys

try:
    import requests
except ImportError:
    print('ERROR: falta la librería requests. Instálala con: python3 -m pip install requests')
    sys.exit(1)

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

ENDPOINTS = {
    'health': '/health',
    'index': '/',
    'weather': '/weather',
    'weather_multiple': '/weather/multiple'
}


def print_section(title):
    print('\n' + '=' * 60)
    print(title)
    print('=' * 60)


def show_response(resp):
    print(f'Status Code: {resp.status_code}')
    try:
        print('Response:')
        print(resp.json())
    except Exception:
        print('Response body:')
        print(resp.text)


def test_health():
    print_section('Health Check')
    resp = requests.get(BASE_URL + ENDPOINTS['health'], timeout=10)
    show_response(resp)
    return resp.status_code == 200 and resp.json().get('status') == 'ok'


def test_index():
    print_section('Index Root')
    resp = requests.get(BASE_URL + ENDPOINTS['index'], timeout=10)
    show_response(resp)
    return resp.status_code == 200 and 'endpoints' in resp.json()


def test_weather_city():
    print_section('Weather by City (Madrid)')
    resp = requests.get(BASE_URL + ENDPOINTS['weather'], params={'city': 'Madrid'}, timeout=10)
    show_response(resp)
    data = resp.json().get('data', {}) if resp.status_code == 200 else {}
    return resp.status_code == 200 and data.get('city') and data.get('weather')


def test_weather_coords():
    print_section('Weather by Coordinates')
    resp = requests.get(BASE_URL + ENDPOINTS['weather'], params={'lat': '40.4168', 'lon': '-3.7038'}, timeout=10)
    show_response(resp)
    return resp.status_code == 200 and resp.json().get('success') is True


def test_multiple():
    print_section('Multiple Weather')
    payload = {'cities': ['Madrid', 'London']}
    resp = requests.post(BASE_URL + ENDPOINTS['weather_multiple'], json=payload, timeout=15)
    show_response(resp)
    return resp.status_code == 200 and resp.json().get('success') is True


def main():
    print('Weather API test runner')
    print(f'Using BASE_URL={BASE_URL}')
    tests = [
        ('Health', test_health),
        ('Index', test_index),
        ('Weather City Madrid', test_weather_city),
        ('Weather Coordinates', test_weather_coords),
        ('Weather Multiple', test_multiple),
    ]

    passed = 0
    for name, func in tests:
        try:
            success = func()
        except Exception as exc:
            print(f'ERROR in {name}: {exc}')
            success = False
        print(f'{name}: {"PASS" if success else "FAIL"}')
        if success:
            passed += 1

    print('\nSummary: {}/{} tests passed'.format(passed, len(tests)))
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == '__main__':
    main()
