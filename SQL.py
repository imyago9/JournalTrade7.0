import psycopg2
from psycopg2 import sql
import sys
import os
from dotenv import load_dotenv


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


load_dotenv(resource_path('resources/parameters.env'))

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()


def verify_credentials(username, password):
    try:
        cursor.execute("SELECT user_id, password FROM users WHERE username=%s", (username,))
        result = cursor.fetchone()

        if result and result[1] == password:
            print(result)
            print(result[0])
            print(result[1])
            user_id = result[0]
            UserSession().set_user_id(user_id)
            return True
        return False

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False

    except Exception as e:
        print(f"Other error: {e}")
        return False


def register_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id", (username, password))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False

    except Exception as e:
        print(f"Other error: {e}")
        return False


def insert_account(user_id, account_name, account_type):
    try:
        query = """
        INSERT INTO accounts (user_id, account_name, account_type) 
        VALUES (%s, %s, %s);
        """
        cursor.execute(query, (user_id, account_name, account_type))
        conn.commit()
        return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False

    except Exception as e:
        print(f"Other error: {e}")
        return False


def get_all_accounts(user_id):
    try:
        cursor.execute("SELECT account_id, account_name, account_type FROM accounts WHERE user_id = %s;", (user_id,))
        conn.commit()
        accounts = cursor.fetchall()
        return accounts
    except Exception as e:
        print(f'Error getting all accounts: {e}')


def insert_trade(account_id, instrument, direction, entries, exits, entry_time, exit_time, profit, com):
    try:
        cursor.execute("""
            INSERT INTO trades (account_id, instrument, direction, entry_time, exit_time, profit, com)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING trade_id
        """, (account_id, instrument, direction, entry_time, exit_time, profit, com))

        trade_id = cursor.fetchone()[0]

        for entry_price, entry_qty in entries:
            cursor.execute("""
                INSERT INTO trade_entries (trade_id, entry_price, entry_qty)
                VALUES (%s, %s, %s)
            """, (trade_id, entry_price, entry_qty))

        for exit_price, exit_qty in exits:
            cursor.execute("""
                INSERT INTO trade_exits (trade_id, exit_price, exit_qty)
                VALUES (%s, %s, %s)
            """, (trade_id, exit_price, exit_qty))

        conn.commit()
        return trade_id

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False

    except Exception as e:
        print(f"Other error: {e}")
        conn.rollback()
        return False


def insert_zone_scoring(trade_id, scores):
    try:
        cursor.execute("""
            INSERT INTO trade_zones (trade_id, strength, basetime, freshness, trend, curve, profitzone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (trade_id,
              scores['strength'] if scores['strength'] is not None else int(0),
              scores['basetime'] if scores['basetime'] is not None else float(0.0),
              scores['freshness'] if scores['freshness'] is not None else int(0),
              scores['trend'] if scores['trend'] is not None else int(0),
              scores['curve'] if scores['curve'] is not None else float(0.0),
              scores['profitzone'] if scores['profitzone'] is not None else int(0)))
        conn.commit()
        print(f'Inserting scoring into trade id: {trade_id}')
        return True
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Other error: {e}")
        conn.rollback()
        return False


def update_zone_scoring(trade_id, field, new_value):
    try:
        cursor.execute(""" 
            SELECT strength, basetime, freshness, trend, curve, profitzone 
            FROM trade_zones 
            WHERE trade_id = %s
        """, (trade_id,))
        current_zone_score = cursor.fetchone()

        if current_zone_score:
            fields = ['strength', 'basetime', 'freshness', 'trend', 'curve', 'profitzone']
            field_index = fields.index(field)
            if current_zone_score[field_index] != new_value:
                update_query = f"UPDATE trade_zones SET {field} = %s WHERE trade_id = %s"
                cursor.execute(update_query, (new_value, trade_id))
                conn.commit()
                print(f"Updated {field} for trade_id {trade_id}.")
            else:
                print(f"No changes detected for {field} of trade_id {trade_id}.")
        else:
            print(f"No existing trade zone found for trade_id {trade_id}.")
        return True
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    except ValueError:
        print(f"Field '{field}' is not valid.")
        return False
    except Exception as e:
        print(f"Other error: {e}")
        conn.rollback()
        return False


def get_account_id(user_id, account_name):
    try:
        # Assuming conn is your database connection
        cursor = conn.cursor()
        query = """
        SELECT account_id
        FROM accounts
        WHERE user_id = %s AND account_name = %s;
        """
        cursor.execute(query, (user_id, account_name))
        account_id = cursor.fetchone()

        if account_id:
            return account_id[0]
        else:
            print("Account not found.")
            return None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Other error: {e}")
        return None


def get_trades_for_account(account_id):
    try:
        cursor.execute("""
        SELECT t.trade_id, t.instrument, t.direction, t.entry_time, t.exit_time, t.profit, t.com,
               te.entry_price, te.entry_qty, 
               tx.exit_price, tx.exit_qty,
               tz.strength, tz.basetime, tz.freshness, tz.trend, tz.curve, tz.profitzone
        FROM trades t
        LEFT JOIN trade_entries te ON t.trade_id = te.trade_id
        LEFT JOIN trade_exits tx ON t.trade_id = tx.trade_id
        LEFT JOIN trade_zones tz ON t.trade_id = tz.trade_id
        WHERE t.account_id = %s
        ORDER BY t.entry_time DESC;
        """, (account_id,))
        trades = cursor.fetchall()
        trade_data = {}
        for row in trades:
            trade_id = row[0]
            if trade_id not in trade_data:
                trade_data[trade_id] = {
                    'trade_id': trade_id,
                    'instrument': row[1],
                    'direction': row[2],
                    'entry_time': row[3],
                    'exit_time': row[4],
                    'profit': row[5],
                    'commission': row[6],
                    'entries': [],
                    'exits': [],
                    'strength': row[11],
                    'basetime': row[12],
                    'freshness': row[13],
                    'trend': row[14],
                    'curve': row[15],
                    'profitzone': row[16],
                }

            if row[7] is not None and row[8] is not None:
                trade_data[trade_id]['entries'].append({'price': row[7], 'quantity': row[8]})
            if row[9] is not None and row[10] is not None:
                trade_data[trade_id]['exits'].append({'price': row[9], 'quantity': row[10]})
        return list(trade_data.values())
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Other error: {e}")
        return []


def check_trades_for_nt_account(account_id):
    try:
        cursor.execute("""
        SELECT t.trade_id, t.instrument, t.direction, t.entry_time, t.exit_time, t.profit, t.com,
               te.entry_price, te.entry_qty, 
               tx.exit_price, tx.exit_qty
        FROM trades t
        LEFT JOIN trade_entries te ON t.trade_id = te.trade_id
        LEFT JOIN trade_exits tx ON t.trade_id = tx.trade_id
        WHERE t.account_id = %s
        ORDER BY t.entry_time DESC;
        """, (account_id,))
        trades = cursor.fetchall()
        trade_data = {}
        for row in trades:
            trade_id = row[0]
            if trade_id not in trade_data:
                trade_data[trade_id] = {
                    'trade_id': trade_id,
                    'instrument': row[1],
                    'direction': row[2],
                    'entry_time': row[3],
                    'exit_time': row[4],
                    'profit': row[5],
                    'commission': row[6],
                    'entries': [],
                    'exits': []
                }

            if row[13] is not None and row[14] is not None:
                trade_data[trade_id]['entries'].append({'price': row[13], 'quantity': row[14]})
            if row[15] is not None and row[16] is not None:
                trade_data[trade_id]['exits'].append({'price': row[15], 'quantity': row[16]})
        return list(trade_data.values())
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Other error: {e}")
        return []


def insert_screenshot(trade_id, screenshot_data, label):
    try:
        insert_query = """
        INSERT INTO trade_screenshots (trade_id, screenshot, screenshot_index)
        VALUES (%s, %s, %s) RETURNING screenshot_id;
        """
        cursor.execute(insert_query, (trade_id, psycopg2.Binary(screenshot_data), label))
        screenshot_id = cursor.fetchone()[0]
        conn.commit()
        print(f'Inserting screenshot {label} into trade id: {trade_id}')
        return screenshot_id
    except Exception as e:
        print(f"Error inserting screenshot: {e}")
        conn.rollback()

def update_screenshot(trade_id, new_screenshot_data, label):
    try:
        cursor.execute("SELECT screenshot FROM trade_screenshots WHERE trade_id = %s AND screenshot_index = %s", (trade_id, label))
        current_screenshot = cursor.fetchone()

        if current_screenshot:
            if current_screenshot[0] != new_screenshot_data:
                update_query = """
                UPDATE trade_screenshots SET screenshot = %s WHERE trade_id = %s AND screenshot_index = %s
                """
                cursor.execute(update_query, (psycopg2.Binary(new_screenshot_data), trade_id, label))
                conn.commit()
                print(f"Updated screenshot for trade_id {trade_id} and label {label}.")
            else:
                print(f"No changes detected for screenshot of trade_id {trade_id} and label {label}.")
        else:
            # If no screenshot exists for this trade and label, insert a new one
            insert_screenshot(trade_id, new_screenshot_data, label)

        return True
    except Exception as e:
        print(f"Error updating screenshot: {e}")
        conn.rollback()
        return False



def get_screenshot(trade_id, screenshot_index):
    try:
        query = """
        SELECT screenshot
        FROM trade_screenshots
        WHERE trade_id = %s AND screenshot_index= %s;
        """
        cursor.execute(query, (trade_id, screenshot_index))
        result = cursor.fetchone()
        screenshot = result[0] if result else None
        return screenshot
    except Exception as e:
        print(f"Error getting screenshot for trade_id {trade_id} and index {screenshot_index}: {e}")
        conn.rollback()

def get_all_screenshots(trade_id):
    try:
        query = """
        SELECT screenshot_index, screenshot
        FROM trade_screenshots
        WHERE trade_id = %s AND screenshot_index IN ('HTF', 'ITF', 'LTF');
        """
        cursor.execute(query, (trade_id,))
        results = cursor.fetchall()
        screenshots = {'HTF': None, 'ITF': None, 'LTF': None}
        for screenshot_index, screenshot_data in results:
            screenshots[screenshot_index] = screenshot_data

        return screenshots
    except Exception as e:
        print(f"Error getting screenshots for trade_id {trade_id}: {e}")
        conn.rollback()
        return None

def get_zone_scores(trade_id):
    try:
        cursor.execute("""
            SELECT strength, basetime, freshness, trend, curve, profitzone
            FROM trade_zones 
            WHERE trade_id = %s;
        """, (trade_id,))
        result = cursor.fetchone()
        if result:
            return {
                'strength': result[0],
                'basetime': result[1],
                'freshness': result[2],
                'trend': result[3],
                'curve': result[4],
                'profitzone': result[5]
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving data from server: {e}")
        conn.rollback()
        return None, None


def insert_or_update_zone_with_screenshot(trade_id, zone_score, screenshots, entry_note_text):
    try:
        if zone_score:
            cursor.execute("SELECT trade_id FROM trade_zones WHERE trade_id = %s", (trade_id,))
            if cursor.fetchone():
                for field, score in zone_score:
                    update_zone_scoring(trade_id, field, score)
            else:
                insert_zone_scoring(trade_id, zone_score)
            print('1. Entered Zone Scores.')
        if screenshots:
            for label, screenshot_data in screenshots:
                if screenshot_data:
                    update_screenshot(trade_id, screenshot_data, label)
            print('2. Entered Screenshots.')
        if entry_note_text:
            cursor.execute("SELECT note_id, note_text FROM trade_notes WHERE trade_id = %s", (trade_id,))
            result = cursor.fetchone()
            if result:
                update_trade_note(result[0], entry_note_text, note_type='trade')
            else:
                insert_trade_note(trade_id, entry_note_text)
            print('3. Entered note text.')
        return True
    except Exception as e:
        print(f"Error saving score, notes, and/or screenshots: {e}")
        return False

def insert_daily_note(account_id, note_text, date):
    if len(note_text) > 500:
        raise ValueError("Note text exceeds 500 character limit")
    try:
        insert_query = sql.SQL("""
            INSERT INTO daily_notes (account_id, note_text, created_at) 
            VALUES (%s, %s, %s)
            RETURNING note_id;
        """)
        cursor.execute(insert_query, (account_id, note_text, date))
        conn.commit()
        note_id = cursor.fetchone()[0]
        print(f"Note successfully inserted with note_id: {note_id}")
        return note_id
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")


def update_trade_note(note_id, new_text, note_type=None):
    if len(new_text) > 500:
        raise ValueError("Note text exceeds 500 character limit")
    try:
        type = 'trade_notes' if note_type == 'trade' else 'daily_notes' if note_type == 'daily' else None
        update_query = sql.SQL(f"""
                UPDATE {type}
                SET note_text = %s, created_at = CURRENT_TIMESTAMP
                WHERE note_id = %s;
            """)
        cursor.execute(update_query, (new_text, note_id))
        conn.commit()
        print(f"Note with note_id {note_id} successfully updated.")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")


def insert_trade_note(trade_id, note_text):
    if len(note_text) > 500:
        raise ValueError("Note text exceeds 500 character limit")
    try:
        insert_query = sql.SQL("""
            INSERT INTO trade_notes (trade_id, note_text) 
            VALUES (%s, %s)
            RETURNING note_id;
        """)
        cursor.execute(insert_query, (trade_id, note_text))
        conn.commit()
        note_id = cursor.fetchone()[0]
        print(f"Note successfully inserted with note_id: {note_id}")
        return note_id
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")

def get_trade_note(trade_id=None, account_id=None, date=None):
    try:
        if trade_id:
            id = trade_id
            note_type = 'trade_notes'
            column_name = 'trade_id'
            select_query = sql.SQL("""
                SELECT note_id, note_text, created_at
                FROM {note_type}
                WHERE {column_name} = %s;
            """).format(
                note_type=sql.Identifier(note_type),
                column_name=sql.Identifier(column_name)
            )
            cursor.execute(select_query, (id,))

        elif account_id and date:
            id = account_id
            note_type = 'daily_notes'
            column_name = 'account_id'
            select_query = sql.SQL("""
                SELECT note_id, note_text, created_at
                FROM {note_type}
                WHERE {column_name} = %s AND created_at = %s;
            """).format(
                note_type=sql.Identifier(note_type),
                column_name=sql.Identifier(column_name)
            )
            cursor.execute(select_query, (id, date))

        else:
            raise ValueError("Either trade_id or account_id must be provided")

        result = cursor.fetchone()

        if result:
            note_id, note_text, created_at = result
            print(note_id, note_text, id, note_type)
            return note_id, note_text, created_at
        else:
            time = date if date else ''
            print(f"No note found for {column_name}:{time}: {id}")
            return None, None, None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def save_trade_with_screenshots(trade_data, screenshots):
    try:
        # Save trade and get trade_id
        trade_id = insert_trade(
            trade_data['account_id'],
            trade_data['instrument'],
            trade_data['direction'],
            trade_data['entries'],
            trade_data['exits'],
            trade_data['entry_time'],
            trade_data['exit_time'],
            trade_data['profit'],
            trade_data['commission'],
        )

        insert_zone_scoring(trade_id, trade_data)

        for label, screenshot_data in screenshots:
            if screenshot_data:
                insert_screenshot(trade_id, screenshot_data, label)
        return True
    except Exception as e:
        print(f"Error saving trade with screenshots: {e}")
        return False


def send_friend_request(user_id, friend_id):
    try:
        insert_query = """
        INSERT INTO friends (user_id, friend_id, status)
        VALUES (%s, %s, 'pending')
        ON CONFLICT (user_id, friend_id) DO NOTHING;
        """
        cursor.execute(insert_query, (user_id, friend_id))
        conn.commit()
    except Exception as e:
        print(f"Error sending friend request: {e}")
        conn.rollback()


def accept_friend_request(user_id, friend_id):
    try:
        update_query = """
        UPDATE friends
        SET status = 'accepted'
        WHERE user_id = %s AND friend_id = %s AND status = 'pending';
        """
        cursor.execute(update_query, (user_id, friend_id))

        if cursor.rowcount == 1:  # Only proceed if the update was successful
            insert_reverse_query = """
            INSERT INTO friends (user_id, friend_id, status)
            VALUES (%s, %s, 'accepted')
            ON CONFLICT (user_id, friend_id) DO NOTHING;
            """
            cursor.execute(insert_reverse_query, (user_id, friend_id))
            print(f'Friend request from {user_id} was accepted by {friend_id}')

        conn.commit()
    except Exception as e:
        print(f"Error accepting friend request: {e}")
        conn.rollback()


def reject_friend_request(user_id, friend_id):
    try:
        delete_query = """
        DELETE FROM friends 
        WHERE (user_id = %s AND friend_id = %s) OR (user_id = %s AND friend_id = %s);
        """
        cursor.execute(delete_query, (user_id, friend_id, friend_id, user_id))
        conn.commit()
        print(f"Friend request from user_id {user_id} to user_id {friend_id} has been rejected.")
    except Exception as e:
        print(f'Error rejecting friend request: {e}')


def update_friend_request_status(user_id, friend_id, status):
    try:
        update_query = """
        UPDATE friends
        SET status = %s
        WHERE user_id = %s AND friend_id = %s;
        """
        cursor.execute(update_query, (status, user_id, friend_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating friend request status: {e}")
        conn.rollback()


def get_friends(user_id, status='accepted'):
    try:
        select_query = """
        SELECT DISTINCT u.user_id, u.username
        FROM friends f
        JOIN users u ON (
            (f.friend_id = u.user_id AND f.user_id = %s) OR 
            (f.user_id = u.user_id AND f.friend_id = %s)
        )
        WHERE f.status = %s;
        """
        cursor.execute(select_query, (user_id, user_id, status))
        friends = cursor.fetchall()
        return friends
    except Exception as e:
        print(f"Error retrieving friends: {e}")
        return []


def get_received_friend_requests(user_id):
    try:
        select_query = """
        SELECT u.user_id, u.username
        FROM friends f
        JOIN users u ON f.user_id = u.user_id
        WHERE f.friend_id = %s AND f.status = 'pending';
        """
        cursor.execute(select_query, (user_id,))
        requests = cursor.fetchall()
        return requests
    except Exception as e:
        print(f"Error retrieving friend requests: {e}")
        return []


def username_to_userid(username):
    try:
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the user_id
        else:
            print("Username not found")
            return None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Other error: {e}")
        return None


def get_username_by_userid(user_ids):
    try:
        user_ids_tuple = tuple(user_ids)  # Convert list to tuple for the IN clause
        cursor.execute("SELECT username FROM users WHERE user_id IN %s", (user_ids_tuple,))
        results = cursor.fetchall()
        if results:
            return [result[0] for result in results]  # Return list of usernames
        else:
            print("No user IDs found")
            return []
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Other error: {e}")
        return []


class UserSession:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.user_id = None
        return cls._instance

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id
