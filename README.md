# pipeline-django-semver-demo

Extensive Django Pipeline, with Semantic Versioning and Gitflow Workflow. The pipeline demo allows the following:

- Outdated packages check
- Check code format with `black`
- Check the sorting of the imports with `isort`
- Security check with `bandit`
- Creation of a Docker Image

All dependencies are updated with Renovate, for more information check the following page: https://github.com/renovatebot/renovate

## Semantic versioning

This project uses [`semantic-release`](https://github.com/semantic-release/semantic-release) and [`conventionalcommits`](https://www.conventionalcommits.org/) for versioning to `develop` and `master`.

Semantic versioning is divided into 
* major, 
* minor and 
* patch(es). 

The tool analyses the commit titles to calculate a new version.

Within a configuration file you can defined which prefixes within a `$ git commit -m "prefix commit message"` are applied. The file is called:
[`.releaserc.json`](.releaserc.json), and common prefixes are

- feat: Minor (new features)
- fix: Patch (bug fixes)
- refactor: Patch (Code Refactoring)
- docs: Patch (documentation)
- test: Patch (new tests)
- style: Patch (Code Linting)
- perf: Patch (performance improvements)
- ci: Patch (pipeline changes)
- build: Patch (build system changes)
- chore: Patch (updates of dependencies)

Examples

- Introduction of a new tests, increases the version from e.g. `1.0.0` to `1.0.1`

  `$ git commit -m "test: add new unit tests"`
  
- Introduction of a new features, increases the version from e.g. `1.0.0` to `1.1.0`
  
  `$ git commit -m "feat: add new features"`
  
- Introduction of a new features that are not backward compatible, increases the version from e.g. `1.0.0` to `2.0.0`:

  `$ git commit -m "feat!: add new features"`

### `develop` Branch

The `develop` branch is configured as a pre-release. This is necessary in order to distinguish whether the release is used by the `develop` or the `master`. On the `develop` branch, the version therefore also contains `develop` and a build number, e.g. `1.1.0-develop.1`

### `develop` Branch

Der `develop` Branch ist als Pre-Release konfiguriert. Das ist nötig, um unterscheiden zu können, ob das Release vom `develop` oder vom `master` genutzt wird. Auf dem `develop` Branch beinhaltet die Version daher zusätzlich `develop` und eine Buildnummer, z.B. `1.1.0-develop.1`

```
name: Release Pipeline

on:
  push:
    branches:
      - develop
      - master

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-node@v1
      with:
        node-version: 12.16.3

    - name: prepare
      run: npm install @semantic-release/github @semantic-release/exec conventional-changelog-conventionalcommits
      
    - name: get version
      run: npx semantic-release --generate-notes false --dry-run
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    - run: echo ::set-env name=version::$(cat version)
    - name: publish docker image
      run: |
        echo ${{ secrets.GITHUB_TOKEN }} | docker login docker.pkg.github.com -u ${{ github.repository }} --password-stdin
        docker build . --file Dockerfile -t docker.pkg.github.com/${{ github.repository }}/app:$version
        docker push docker.pkg.github.com/${{ github.repository }}/app:$version
    - name: release
      run: npx semantic-release
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Pipeline

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
        python-version: 3.8

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
        python-version: 3.8

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
        python-version: 3.8

    - name: pip install
      run: pip install -r requirements.txt 

    - name: isort
      run: isort --check .

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.8

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
    runs-on: ubuntu-latest
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
