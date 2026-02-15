from python4cpm import Python4CPM
from psycopg import connect, sql


P4CPM = Python4CPM("Postgres")


def _get_creds(from_reconcile=False):
    if from_reconcile is False:
        username = P4CPM.args.username
        password = P4CPM.secrets.password.get()
    else:
        username = P4CPM.args.reconcile_username
        password = P4CPM.secrets.reconcile_username.get()
    return username, password


def verify(from_reconcile=False):
    username, password = _get_creds(from_reconcile)
    with connect(
        host=P4CPM.args.address,
        dbname="postgres",
        user=username,
        password=password,
        autocommit=True
    ) as conn:
        with conn.cursor():
            P4CPM.log_info("verify: Password verified successfully")


def change(from_reconcile=False):
    username, password = _get_creds(from_reconcile)
    with connect(
        host=P4CPM.args.address,
        dbname="postgres",
        user=username,
        password=password,
        autocommit=True
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("ALTER USER {} WITH PASSWORD {}").format(
                    sql.Identifier(P4CPM.args.username),
                    sql.Literal(P4CPM.secrets.new_password.get())
                )
            )
            P4CPM.log_info("change: Password changed successfully")


def main():
    try:
        action = P4CPM.args.action
        if action == Python4CPM.ACTION_VERIFY:
            verify()
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_LOGON:
            verify()
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_CHANGE:
            change()
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_PRERECONCILE:
            verify(from_reconcile=True)
            P4CPM.close_success()
        elif action == Python4CPM.ACTION_RECONCILE:
            change(from_reconcile=True)
            P4CPM.close_success()
        else:
            P4CPM.log_error(f"main: invalid action: '{action}'")
            P4CPM.close_fail()
    except Exception as e:
        P4CPM.log_error(f"{type(e).__name__}: {e}")
        P4CPM.close_fail()


if __name__ == "__main__":
    main()
