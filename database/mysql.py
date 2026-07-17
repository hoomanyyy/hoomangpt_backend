import pymysql
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import date


load_dotenv()


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)



def connection():

    return pymysql.connect(

        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor

    )



# -------------------------
# PLAN
# -------------------------


def get_user_plan(user_id):

    con = connection()
    cursor = con.cursor()


    cursor.execute(
        """
        SELECT plan
        FROM plans
        WHERE user_id=%s
        ORDER BY date DESC
        LIMIT 1
        """,
        (user_id,)
    )


    result = cursor.fetchone()

    con.close()



    if not result:

        return "FREE"


    return result["plan"]




def get_daily_limit(user_id):


    plan = get_user_plan(user_id)



    if plan == "FREE":

        return 2



    if plan == "PRO":

        return 50



    if plan == "VIP":

        return 999999



    return 2





# -------------------------
# USAGE
# -------------------------


def can_use(user_id):


    limit = get_daily_limit(user_id)


    con = connection()
    cursor = con.cursor()



    cursor.execute(
        """
        SELECT count
        FROM usage_limit
        WHERE user_id=%s
        AND usage_date=%s
        """,
        (
            user_id,
            date.today()
        )
    )


    row = cursor.fetchone()


    con.close()



    if not row:

        return True



    return row["count"] < limit





def add_usage(user_id):


    today = date.today()


    con = connection()
    cursor = con.cursor()



    cursor.execute(
        """
        SELECT *
        FROM usage_limit
        WHERE user_id=%s
        AND usage_date=%s
        """,
        (
            user_id,
            today
        )
    )



    row = cursor.fetchone()



    if row:


        cursor.execute(
            """
            UPDATE usage_limit
            SET count=count+1
            WHERE user_id=%s
            AND usage_date=%s
            """,
            (
                user_id,
                today
            )
        )


    else:


        cursor.execute(
            """
            INSERT INTO usage_limit
            (
            user_id,
            count,
            usage_date
            )
            VALUES(%s,%s,%s)
            """,
            (
                user_id,
                1,
                today
            )
        )


    con.commit()

    con.close()





def use_credit(user_id):


    if not can_use(user_id):

        return False



    add_usage(user_id)


    return True





def get_usage(user_id):


    con = connection()
    cursor = con.cursor()



    cursor.execute(
        """
        SELECT count
        FROM usage_limit
        WHERE user_id=%s
        AND usage_date=%s
        """,
        (
            user_id,
            date.today()
        )
    )



    row = cursor.fetchone()


    con.close()



    if not row:

        return 0


    return row["count"]






# -------------------------
# AUTH
# -------------------------


def user_login(email,password):


    con = connection()

    try:


        cursor = con.cursor()


        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            """,
            (email,)
        )


        user = cursor.fetchone()



        if not user:

            return None



        if not pwd_context.verify(
            password,
            user["password"]
        ):

            return None



        return {

            "id":user["id"],

            "name":user["name"],

            "email":user["email"]

        }



    finally:

        con.close()





def user_signup(name,email,password):


    con = connection()


    try:


        cursor = con.cursor()



        hashed = pwd_context.hash(password)



        cursor.execute(
            """
            INSERT INTO users
            (
            name,
            email,
            password
            )
            VALUES(%s,%s,%s)
            """,
            (
                name,
                email,
                hashed
            )
        )


        con.commit()



        user_id = cursor.lastrowid



        # ساخت پلن FREE خودکار

        cursor.execute(
            """
            INSERT INTO plans
            (
            plan,
            user_id,
            date
            )
            VALUES(%s,%s,NOW())
            """,
            (
                "FREE",
                user_id
            )
        )


        con.commit()



        return {

            "id":user_id,

            "name":name,

            "email":email,

            "plan":"FREE"

        }



    finally:

        con.close()

def email_exists(email):

    con = connection()
    cursor = con.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE email=%s
        """,
        (email,)
    )

    result = cursor.fetchone()

    con.close()

    return result is not None

def change_email(user_id, new_email):

    if email_exists(new_email):

        return False


    con = connection()
    cursor = con.cursor()


    cursor.execute(
        """
        UPDATE users
        SET email=%s
        WHERE id=%s
        """,
        (
            new_email,
            user_id
        )
    )


    con.commit()
    con.close()


    return True

def change_password(user_id, new_password):

    con = connection()
    cursor = con.cursor()


    hashed = pwd_context.hash(new_password)


    cursor.execute(
        """
        UPDATE users
        SET password=%s
        WHERE id=%s
        """,
        (
            hashed,
            user_id
        )
    )


    con.commit()
    con.close()


    return True


def upgrade_plan(user_id, plan):

    con = connection()

    cursor = con.cursor()


    cursor.execute(
        """
        INSERT INTO plans
        (
            user_id,
            plan,
            date
        )
        VALUES
        (
            %s,
            %s,
            NOW()
        )
        """,
        (
            user_id,
            plan
        )
    )


    con.commit()

    con.close()


    return True

