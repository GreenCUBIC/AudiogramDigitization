#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
import subprocess as sp
import argparse
import sys

def get_container_id():
    # List the docker processes
    docker_ps_output = sp.check_output("docker ps", shell=True).decode("utf-8")
    containers = docker_ps_output.split("\n")[1:]

    # Find the relevant ones (that contain "nihl" and "database" in the name)
    database_containers = [container for container in containers if "nihl" in container and "database" in container]

    # If none are found, exit
    if len(database_containers) == 0:
        print(("No running containers for the NIHL database were found.\n"
            "Please start the docker container with the command `docker-compose up -d database`."))
        sys.exit(1)

    return database_containers[0].split()[0]

def get_database_connection_info(operation_type: str):
    if operation_type not in ("dump", "restore"):
        raise "Valid values for argument `operation_type` are `dump` or `restore`."
    parser =  argparse.ArgumentParser(description="Obtains the relevant database information for use in database-related scripts.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port where the database is running.")
    parser.add_argument("-U", "--username", type=str, required=True, help="Username to connect to the database.")
    parser.add_argument("-d", "--database_name", type=str, required=True, help="Name of the database to dump.")
    if operation_type == "dump":
        parser.add_argument("-o", "--output", type=str, required=True, help="Name of the dump file (JUST THE NAME, NOT THE PATH).")
    if operation_type == "restore":
        parser.add_argument("-i", "--input", type=str, required=True, help="Name of the dump file to be restored.")
    args = parser.parse_args()
    return args
