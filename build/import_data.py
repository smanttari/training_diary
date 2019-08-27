"""
Script for importing static sample data to treenit-database.
"""
import csv
import sqlite3

datasets = {
    "aika": """
        INSERT INTO treenipaivakirja_aika (
            vvvvkkpp,
            pvm,
            vuosi,
            kk,
            kk_nimi,
            paiva,
            vko,
            viikonpaiva,
            viikonpaiva_lyh,
            hiihtokausi
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
    "laji": """
        INSERT INTO treenipaivakirja_laji (
            id,
            laji,
            laji_nimi,
            laji_ryhma,
            user_id
        )
        VALUES (?,?,?,?,?)""",
    "tehoalue": """
        INSERT INTO treenipaivakirja_tehoalue (
            id,
            jarj_nro,
            teho,
            alaraja,
            ylaraja,
            user_id
        )
        VALUES (?,?,?,?,?,?)"""
}

# open connection to db
conn = sqlite3.connect('Treenit/treenit.sqlite3')
cur = conn.cursor()

# insert datasets
for dataset,sql in datasets.items():
    try:
        # read csv
        data = []
        with open(f'build/{dataset}.csv', encoding='ansi') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                data.append(row)

        # insert data to db
        cur.executemany(sql, data)
        conn.commit()
        
        # check results
        cur.execute(f"select count(*) from treenipaivakirja_{dataset}")
        rows = cur.fetchall()
        print('Number of rows inserted to {}: {}'.format(dataset, str(rows[0][0])))
    except Exception as err:
        print(str(err))

# close connection
conn.close()