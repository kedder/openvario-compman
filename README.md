# Gliding Competiton Manager for OpenVario

[![Build Status](https://travis-ci.com/kedder/openvario-compman.svg?branch=master)](https://travis-ci.com/kedder/openvario-compman)
[![Coverage Status](https://coveralls.io/repos/github/kedder/openvario-compman/badge.svg?branch=master)](https://coveralls.io/github/kedder/openvario-compman?branch=master)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintainability](https://api.codeclimate.com/v1/badges/45964f7cf5f78f3a0f98/maintainability)](https://codeclimate.com/github/kedder/openvario-compman/maintainability)

This application is intended for glider pilots participating in gliding
competitions, published on [Soaring Spot](https://soaringspot.com). It runs on
[OpenVario](https://openvario.org/) flight computer and automatically downloads
current contest airspace and waypoint files when they are published on Soaring
Spot. `compman` also configures [XCSoar](https://xcsoar.org/) to use the
updated files. You can switch between contests easily without need to download
and transfer files to the flight computer manually.

It is a text-mode application, which might look primitive for modern
graphics-rich UI standards. However, it is written using contemporary software
engineering techniques, responsive, very fast and easy to use, even with very
limited input controls available for OpenVario. It also has a fairly simple
code, that makes `openvario` easy to understand and change.

[![asciicast](https://asciinema.org/a/307125.svg)](https://asciinema.org/a/307125)

## Usage

This app requires Internet connection to be useful. The simplest way to get it
on your OpenVerio is to use a small USB WiFi dongle.

Typically, during the gliding competition, you run `compman` daily to check if
new competition files were uploaded to Soaring Spot (or when new files are
announced during the briefing). When `compman` is started, new files for the
current competition will be automatically downloaded to the device. As soon as
you select them, XCSoar will be reconfigured to use these files. Simply exit
`compman` and run the XCSoar the usual way.

When you go to the next competition, simply switch the contest using `compman`
menu system. All competition files will be automatically downloaded and XCSoar
will be reconfigured. No more complicated downloading of files on the flash
drives and transferring them manually to the OpenVario!

`compman` can be operated using only 6 buttons: 4 arrow keys for navigating,
<kbd>Enter</kbd> (usually a push on rotary encoder or joystick) for selecting
items and <kbd>Esc</kbd> (usually marked as <kbd>X</kbd>) for going back.

## Installation

To install `compman` on your OpenVario you will also need to be able to ssh to
the device or connect to it through standard debugging serial port. Assuming
the network connection is up, use `opkg` package manager to download and
install `compman`:

```
$ echo src compman http://openvario.lebedev.lt/opkg/armv7vet2hf-neon >> /etc/opkg/customfeeds.conf
$ opkg update
$ opkg install openvario-compman
$ opkg install ovmenu-compman
```

If you have already installed [openvario-shell](https://github.com/kedder/openvario-shell), all you have to do is:

```
$ opkg install openvario-compman
```

At this point you should be able to run compman from command line:

```
$ compman
```

Reboot your OpenVario and you should also see the new menu item for `compman`!

## Developing

It is not required to own or have access to OpenVario device in order to
develop `compman`. The only requirements are Python 3.7 or higher and terminal
emulator, readily available on MacOS or Linux operating systems. There are lots
of free options for Windows as well.

### Setting up the development environment

`compman` uses `pipenv` for managing dependencies and dev environment. If you
don't have it yet, install with:

```sh
$ pip install pipenv
```

After checking out the sources, `cd` to `openvario-compman` directory and run:

```sh
$ pipenv shell
$ pipenv install
```

After that, your development environment is ready, you should be able to run
the app:

```sh
$ compman
```

It is possible to adjust few options by providing them in `.env` file, located
in project directory. You can copy the sample file `sample.env` to `.env` and
adjust values there.

### Development tools

`compman` uses various tools to check the code quality. They are generally
available through `make` program. Most useful are these:

* `make test` - runs the test suite
* `make mypy` - checks the sources with static type checker
* `make black` - reformats the source code to match the code style

It is often useful to watch the log file while running `compman` in development
environment. The log file will contain traces of actions user makes and
tracebacks from exceptions happening during the execution. Use `tail` to watch
the logs in a separate terminal window:

```sh
$ tail -F ~/.compman/compman.log
```

### Filesystem

`compman` keeps all its files under `~/.compman` directory. It contains the set
of directories for each configured competition. Each competition directory
contains downloaded airspace and waypoints files. This directory can be changed
by stting `COMPMAN_DATADIR` environment variable or using `--datadir`
command-line option.

`compman` expects to find XCSoar profile in `~/.xcsoar` directory.
