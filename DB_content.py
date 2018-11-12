import mysql.connector as mdb

class DB():
    def __init__(self):

        con = mdb.connect(host='127.0.0.1', user='root', passwd='1234')
        cur = con.cursor()

        cur.execute("CREATE SCHEMA IF NOT EXISTS experiment;")
        con.commit()

        cur.execute("USE experiment;")
        con.commit()

        cur.execute("CREATE TABLE IF NOT EXISTS Users(\
                     id MEDIUMINT NOT NULL AUTO_INCREMENT,\
                     user_name VARCHAR(30) NOT NULL,\
                     instruction_1 varchar(10),\
                     instruction_2 varchar(10),\
                     question varchar(10),\
                     end_page varchar(10),\
                     experiment_type tinyint(10),\
                     PRIMARY KEY (id));")

        cur.execute("CREATE TABLE IF NOT EXISTS Actions (\
                     id MEDIUMINT,\
                     user_name VARCHAR(30) NOT NULL,\
                     user_action_id INT,\
                     experiment_type tinyint(10),\
                     Firewall_investment TINYINT,\
                     IDSs_investment TINYINT,\
                     Insurance_investment TINYINT,\
                     Pm FLOAT(10,5),\
                     dprime FLOAT(10,5),\
                     compensate FLOAT(10,5),\
                     optimal_threshold FLOAT(10, 5),\
                     score FLOAT(10,5),	\
                     malicious_or_not varchar(30),\
                     Hit TINYINT,\
                     Miss TINYINT,\
                     FA TINYINT,\
                     CR TINYINT,\
                     PRIMARY KEY (id, user_name, user_action_id));")

        cur.execute("SET SQL_SAFE_UPDATES=0;")
        con.commit()
        con.close()

