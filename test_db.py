import psycopg2


if __name__ == '__main__':
	
	conn = psycopg2.connect(dbname='BRDC_UPDATE',user='postgres',host='localhost',port=5433, password='heathcliff')
	print("+++++++++++++")
	print(conn)
	cur = conn.cursor()
	cur.execute("SELECT * FROM pg_catalog.pg_tables;")
	conn.commit()
	dat_out = cur.fetchall()

	for line in dat_out:

		print("____")
		print(line)
		print("Done")

		