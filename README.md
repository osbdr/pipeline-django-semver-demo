# pipeline-django-semver-demo

Beispiel einer Pipeline, die folgendes kann:
- Outdated Check
- Code Format mit `black` überprüfen
- Sortierung der Imports mit `isort` überprüfen
- Security Check mit `bandit`
- Erstellung eines Docker Images

Die Dependencies werden mit Renovate aktualisiert. Mehr Infos: https://github.com/renovatebot/renovate

> **Hinweis**: 
> - `pip list --outdated` endet unabhängig vom Ergebnis immer mit Exit Code `0`, damit die Pipeline entsprechend reagiert wurde der Befehl erweitert.

```
name: Django Pipeline

on:
  pull_request:
    branches: '**'
  push:
    branches:
      - develop
  schedule:
    - cron: '0 20 * * 5'

jobs:
  outdated:
    runs-on: ubuntu-latest
    if: startsWith(github.head_ref, 'renovate') == false
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.8.2

    - name: pip install
      run: pip install -r requirements.txt --user

    - name: outdated
      run: pip list --outdated --not-required --user | grep . && echo "there are outdated packages" && exit 1 || echo "all packages up to date"

  black:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.8.2

    - name: pip install
      run: pip install -r requirements.txt 

    - name: black
      run: black --check .

  isort:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.8.2

    - name: pip install
      run: pip install -r requirements.txt 

    - name: isort
      run: isort **/*.py -c -vb

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.8.2

    - name: pip install bandit
      run: pip install bandit==1.6.2

    - name: bandit
      run: bandit -r **/*.py -f json -o report.json

    - name: show report
      if:  ${{ success() || failure() }}
      run: cat report.json

    - name: upload report
      if:  ${{ success() || failure() }}
      uses: actions/upload-artifact@v2
      with:
        name: Bandit Security Report
        path: report.json

  django_matrix:
    name: Python ${{ matrix.python-version }} / Django ${{ matrix.django-version}}
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 4
      matrix:
        python-version: [3.7, 3.8]
        django-version: ["~=2.2.0", "~=3.0.0"]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip uninstall -y Django
        pip install Django${{ matrix.django-version }}
    - name: Django test runner
      run: |
        python manage.py test
    - name: Django souce code check
      run: |
        python manage.py check
    - name: Django Template validation
      run: |
        python manage.py validate_templates
  docker:
    runs-on: ubuntu-18.04
    steps:
    - uses: actions/checkout@v2

    - name: docker build
      run: docker build . --file Dockerfile -t ${{ github.repository }} -t ${{ github.repository }}:$(date +%s)
```

```
name: Django Sqlite Mac, Linux, Windows

on:
  pull_request:
    branches: '**'
  push:
    branches:
      - develop
  schedule:
    - cron: '0 20 * * 5'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        python_version: [3.7, 3.8]
        os: [macos-latest, windows-latest, ubuntu-latest]
    steps:
    - uses: actions/checkout@v1
    - name: Set up Python ${{ matrix.python_version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python_version }}
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Django souce code check
      run: |
        python manage.py check
    - name: Django test runner
      run: |
        python manage.py test
    - name: Django Template validation
      run: |
        python manage.py validate_templates
```

## Referenzen
- pip list: https://pip.pypa.io/en/stable/reference/pip_list/
- black: https://github.com/psf/black
- isort: https://github.com/timothycrosley/isort
- bandit: https://pypi.org/project/bandit/

- Docker Pipeline: https://partner.bdr.de/gitlab/kfe-devops/pipeline-docker-nodejs-demo
