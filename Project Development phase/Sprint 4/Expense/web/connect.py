import ibm_db

def get_db_connection():

    try:

        conn = ibm_db.connect("DATABASE=<dbname>;\
            HOSTNAME=<hostname>;\
            PORT=30376;\
            Security=SSL;\
            SSLServerCertificate=DigiCertGlobalRootCA.crt;\
            UID=<uname>;\
            PWD=<pasword>;","","")
        print("Connected to DB")
        return conn
    except:
        print("error while connecting ",ibm_db.conn_errormsg())
        return 0
    
connection = get_db_connection()