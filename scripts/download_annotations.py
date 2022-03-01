#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import os
import json

import psycopg2
from tqdm import tqdm
from getpass import getpass

def main(args):
    password = getpass("Please enter your password\n>")
    connection = psycopg2.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=password,
        database="nihl"
    )
    cursor = connection.cursor()

    # This query fetches the latest annotation provided for all annotated
    # reports that are valid (i.e. that contain an audiogram)
    query = (
"""
SELECT DISTINCT ON (report_id) audiograms, report_id
FROM (
    SELECT *
    FROM annotations
    WHERE valid = true
    ORDER BY date_added DESC
) AS subquery;
"""
) 
    cursor.execute(query)

    if not os.path.exists(args.output):
        os.mkdir(args.output)
    for annotation, report_id in tqdm(cursor.fetchall()):
        with open(os.path.join(args.output, f"{report_id}.json"), "w") as ofile:
            ofile.write(json.dumps(annotation))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Dumps the annotations from the database into a directory specified.")
    parser.add_argument("-H", "--host", required=False, default="0.0.0.0", type=str, help="Database host.")
    parser.add_argument("-p", "--port", required=False, default=5432, type=int, help="Port.")
    parser.add_argument("-U", "--user", required=False, default="postgres", type=str, help="The username for the database.")
    parser.add_argument("-o", "--output", required=True, type=str, help="Path to the folder where the annotations should be stored.")
    args = parser.parse_args()

    main(args)
