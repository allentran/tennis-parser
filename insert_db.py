import argparse
import pathlib

import numpy as np
import mysql.connector
import pandas as pd


class DBLoader(object):

    def __init__(self, datapath, user, password, database, host):
        self.datapath = pathlib.Path(datapath)
        self.user = user
        self.password = password
        self.database_name = database
        self.database_host = host

    def __enter__(self):
        print(self.user, self.password, self.database_host, self.database_name)
        self.conn = mysql.connector.connect(
            user=self.user,
            password=self.password,
            host=self.database_host,
            database=self.database_name
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def insert_tournaments(self, male=True):
        match_path = self.datapath / f'charting-{"m" if male else "f"}-matches.csv'
        df = pd.read_csv(match_path)

        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                    SELECT DISTINCT 
                        name
                    FROM tournament_d
                """
            )
            tournament_names = cursor.fetchall()

        existing_tournaments = set([row['name'] for row in tournament_names])
        new_tournaments = set(df['Tournament'].unique().tolist()) - existing_tournaments

        with self.conn.cursor(dictionary=True) as cursor:
            for tournament_name in new_tournaments:
                cursor.execute(
                    """
                        INSERT INTO tournament_d
                            (name) 
                        VALUES (%s)
                    """,
                    (tournament_name, )
                )
            self.conn.commit()

    def insert_players(self, male=True):
        match_path = self.datapath / f'charting-{"m" if male else "f"}-matches.csv'
        df = pd.read_csv(match_path)
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                    SELECT DISTINCT 
                        name
                    FROM player_d
                """
            )
            player_names = cursor.fetchall()
        existing_players = set([row['name'] for row in player_names])
        new_players = set(df['Player 1'].str.strip().unique().tolist()) | set(df['Player 2'].str.strip().unique().tolist())
        new_players = new_players - existing_players

        with self.conn.cursor(dictionary=True) as cursor:
            for player_name in new_players:
                if isinstance(player_name, float):
                    if np.isnan(player_name):
                        continue
                try:
                    cursor.execute(
                        """
                            INSERT INTO player_d
                                (name, male) 
                            VALUES (%s, %s)
                        """,
                        (player_name, 1 if male else 0)
                    )
                    self.conn.commit()
                except mysql.connector.errors.IntegrityError:
                    pass

    def insert_matches(self, male=True):
        match_path = self.datapath / f'charting-{"m" if male else "f"}-matches.csv'
        df = pd.read_csv(match_path).drop_duplicates('match_id').rename(
            columns={'Player 1': 'player1', 'Player 2': 'player2'}
        )
        df['match_date'] = pd.to_datetime(df['Date'], errors='coerce', format='%Y%m%d').dt.date
        df = df[df['match_date'].notnull()]
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                    SELECT DISTINCT 
                        mcp_id
                    FROM match_f
                """
            )
            existing_mcp_ids = set([row['mcp_id'] for row in cursor.fetchall()])
            cursor.execute(
                """
                    SELECT id, name
                    FROM tournament_d
                """
            )
            tournament_mapper = pd.DataFrame(cursor.fetchall()).set_index('name').to_dict()['id']
            cursor.execute(
                """
                    SELECT id, name
                    FROM player_d
                """
            )
            player_mapper = pd.DataFrame(cursor.fetchall()).set_index('name').to_dict()['id']


        player_mapper = {p.lower(): _id for (p, _id) in player_mapper.items()}
        tournament_mapper = {t.lower(): _id for (t, _id) in tournament_mapper.items()}

        new_mcp_ids = set(df['match_id'].tolist()) - existing_mcp_ids
        new_df = df[df['match_id'].isin(new_mcp_ids)]

        with self.conn.cursor(dictionary=True) as cursor:
            for row in new_df.itertuples():
                print(row)
                cursor.execute(
                    """
                        INSERT INTO match_f
                            (player1_id, player2_id, tournament_id, round, surface, best_of_sets, mcp_id, match_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        player_mapper[row.player1.lower().strip()] if isinstance(row.player1, str) else None,
                        player_mapper[row.player2.lower().strip()] if isinstance(row.player2, str) else None,
                        tournament_mapper[row.Tournament.lower()],
                        row.Round,
                        row.Surface if isinstance(row.Surface, str) else None,
                        row._14,
                        row.match_id,
                        row.match_date
                    )
                )
            self.conn.commit()

    def insert_shots(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_path',
        type=str
    )
    parser.add_argument(
        '--u',
        default='root',
        type=str
    )
    parser.add_argument(
        '--p',
        type=str,
        required=True
    )
    parser.add_argument(
        '--host',
        type=str,
        required=True
    )
    parser.add_argument(
        '--database',
        type=str,
        required=True
    )
    args = parser.parse_args()
    with DBLoader(args.data_path, args.u, args.p, args.database, args.host) as db:
        db.insert_tournaments()
        db.insert_players()
        db.insert_matches()
        db.insert_shots()
