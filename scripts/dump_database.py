#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import subprocess as sp
import argparse
import sys

from utils import get_container_id, get_database_connection_info

if __name__ == "__main__":

    args = get_database_connection_info("dump")
    container_id = get_container_id()
    sp.call(f"docker exec -it {container_id} pg_dump -p {args.port} -U {args.username} -d {args.database_name} > {args.output}", shell=True)
