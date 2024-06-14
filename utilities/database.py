import psycopg2
import traceback
import configparser
import shortuuid


class database():

    # method used to get the parameters to connect to Redis
    def _get_postgres_parameters(self):
        # definition of the object used to read the config file
        configfile = configparser.ConfigParser()
        configfile.read("./config.ini")

        postgres = configfile["postgres"]
        self.user = postgres["user"]
        self.password = postgres["password"]
        self.database = postgres["database"]
        self.host = postgres["host"]
        self.port = postgres["port"]

    def __init__(self):
        try:
            self._get_postgres_parameters()
            self.connection = psycopg2.connect(
                user=self.user,
                password=self.password,
                database=self.database,
                host=self.host,
                port=self.port
            )
        except Exception as err:
            print("Error occurred in making connection …")
            traceback.print_exc()



    def insert(self,data):
        cursor = self.connection.cursor()

        data["uuid"] = shortuuid.uuid()
        columns = ", ".join(list(data.keys()))
        placeholders =", ".join(["%s"] * len(list(data.keys())))

        query = f""" INSERT INTO jobs_job ({columns}) VALUES ({placeholders}); """
        try:
            cursor.execute(query, [data[column] for column in list(data.keys())])
            self.connection.commit()
            print("Record inserted successfully!")
        except Exception as err:
            print(err)
        cursor.close()
        #self.connection.close()

    def read(self,channel_id,session_status="Active"):
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM jobs_job WHERE channel_id='{channel_id}' and session_status='{session_status}' LIMIT 500;")
            records = cursor.fetchall()
            self.connection.commit()
            cursor.close()
            #self.connection.close()
            return records
        except Exception as err:
            print(err)
            cursor.close()
            #self.connection.close()

    def update(self,data,channel,channel_id,session_status="Active"):
        cursor = self.connection.cursor()
        #values = [data[key] for key in data] + [channel_id,session_status]
        values = []
        updates = ""
        for key in data:
            updates +=f"{key}='{data[key]}' "

        query = f"""
        UPDATE jobs_job SET {updates} WHERE channel='{channel}' and channel_id='{channel_id}' and session_status='{session_status}';
        """

        print(query)

        try:
            cursor.execute(query, values)
            self.connection.commit()
        except Exception as err:
            print(err)
        cursor.close()
        #self.connection.close()

    def delete(self,channel,channel_id,session_status="Inactive"):
        cursor = self.connection.cursor()
        query = """ DELETE FROM jobs_job WHERE channel=%s and channel_id=%s and session_status=%s; """
        try:
            cursor.execute(query,[channel,channel_id,session_status])
            self.connection.commit()
        except Exception as err:
            print(err)
        cursor.close()
        #self.connection.close()


