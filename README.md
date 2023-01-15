# bp-auditor

`bp-auditor` is a Python package that allows users to monitor the compliance
of block producers on the Telos blockchain network with the Telos Blockchain
Network Operating Agreement (TBNOA). The package has two main parts:

* Data Gatherer: a fully asynchronous process using the `trio` structured
concurrency framework. Once pointed to a antelope chain main load balancer
endpoint, it will query the top block producers by vote and analyze their
compliance with the network operation agreement. It can do 10 producers at
once by default, but this is configurable. The data gathered gets timestamped
and stored into a SQLite3 database ("reports.db" by default) and is meant to
be run every day at a specific time (we recommend 00:00 UTC).

* Data Producer: the second part of the package produces an excel sheet which
acts as a monthly report, in this report all the previously gathered daily
reports from this month are shown in an user-friendly way, for easier
evaluation by the compliance officer.

## Installation

To install the package, simply run:

    pip install -e .

## Usage

The package provides the following commands:

    Usage: bpaudit [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      gather      Run the data gatherer
      install     Systemd unit installer
      produce     Produce the monthly report

Each sub command has it's own `--help` text.

To run the data gatherer, simply run:

    bpaudit gather

To produce the monthly report, simply run:

    bpaudit produce

## Systemd Integration

You can use the `bpaudit install` command to generate systemd unit and timer files
to set up the data gatherer to run automatically at a specific time.

This will allow the data gatherer to run automatically without the need for
manual interaction.


## Virtualenv

It is recommended to use a virtual environment when installing and running
`bp-auditor`. A virtual environment is an isolated Python environment where you can
install packages without affecting the system's Python installation. This allows
you to have a specific version of Python and specific packages for your project,
without interfering with other projects on the same system.

To set up a virtual environment, you can use the `venv` module that comes with
Python 3 or a third-party package such as `virtualenv`.

To create a virtual environment with the `venv` module, run the following command
in your terminal:

    python3 -m venv venv

This will create a new folder called `venv` in your current directory, where the
isolated Python environment will be located.

To activate the virtual environment, run the following command:

    source venv/bin/activate

You will now see the name of your virtual environment in the command prompt,
indicating that it is active.

Once the virtual environment is activated, you can install bp-auditor by running
`pip install bp-auditor` and then use the package as described in the usage section.
When you're done using the package, you can deactivate the virtual environment by
running `deactivate`.

