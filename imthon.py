import psycopg2

class Suppermarket:

    def __init__(self,dbname,user,password,host="localhost",port=5432):
        self.conn=psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur=self.conn.cursor()
        self.user_id=0
        self.price=0
        self.qunatity=0



    def login(self,username,password):
        self.cur.execute("SELECT password,user_id from users WHERE username=%s",(username, ))
        result=self.cur.fetchone()
        if result is None:
            print("Foydalanuvchi topilmadi!")
            return 0
        pw,u_i=result
        if pw==password:
            self.user_id=u_i
            print(f"Xush kelibsiz {username}")
            return 1
        
        else:
            print("Password error!")
            return 0



    def create_accaunt(self,username,password):
        self.cur.execute("INSERT INTO users(username,password) values (%s,%s)",(username,password))
        self.conn.commit()
        print("Foydalanuvchi qo'shildi")



    def products(self):
        self.cur.execute("Select count(*) from products")
        result=self.cur.fetchone()

        if result[0]==0:
            print("Xazircha maxsulotlar mavjud emas!")

        else:
            self.cur.execute("Select * from products")
            rows=self.cur.fetchall()

            for row in rows:
                print(f"Id: {row[0]}, MaxsulotIsmi: {row[1]}, Narxi: {row[2]} so'm, Soni: {row[3]}")

            s=input("Maxsulot Sotib olmoqchimisiz(Y/N): ")
            if s.lower()=="y":
                n=int(input("\nSotib olmoqchi bo'lgan maxsulotingiz idsi: "))
                q=int(input("Sonini kiriting: "))
                self.cur.execute("insert into basket(product_id,user_id,soni) values (%s,%s,%s)",(n,self.user_id,q))
                self.conn.commit()
                print("Maxsulot savatga qo'shildi")

            else:
                return



    def wacht_list(self):
        self.cur.execute("Select count(*) from products")
        result=self.cur.fetchone()

        if result[0]==0:
            print("Xazircha maxsulotlar mavjud emas!")

        else:
            self.cur.execute("Select * from products")
            rows=self.cur.fetchall()

            for row in rows:
                print(f"Id: {row[0]}, MaxsulotIsmi: {row[1]}, Narxi: {row[2]} so'm, Soni: {row[3]}")
  


    def basket(self):
        self.price=0
        self.cur.execute("Select count(*) from basket where user_id=%s", (self.user_id,))
        result=self.cur.fetchone()

        if result[0]==0:
            print("Savatingiz bo'sh!")

        else:
            ba='''Select basket_id,product_name,unit_price,soni from basket as b
            inner join products as p on b.product_id=p.product_id
            where user_id=%s
            '''
            self.cur.execute(ba,(self.user_id, ))
            rows=self.cur.fetchall()
            print("Sizning savatingizda bor maxsulotlar: \n")

            for row in rows:
                basket_id, product_name, unit_price, quantity = row
                self.price += unit_price * quantity
                print(f"Idsi: {basket_id}, Nomi: {product_name}, Narxi: {unit_price} so'm , Soni: {quantity}, Jami: {self.price} so'm\n")

            print('''\n
            1.mahsulotni o'chirish
            2.mahsulotni harid qilish
            3.menuga qaytish
            ''')
            n=input("Soni kiriting: ")

            if n=="1":
                de=int(input("mahsulot idisini kiriting: "))
                self.cur.execute("Delete from basket where basket_id=%s",(de, ))
                self.conn.commit()
                print("Mahsulot o'chirildi")
            elif n=="2":
                self.card()

            elif n=="3":
                return
            
            else:
                print("Xatolik!!!")



    def update(self):
        query = '''
        SELECT b.product_id, b.soni, p.quantity FROM basket AS b
        inner JOIN products AS p ON b.product_id = p.product_id
        WHERE b.user_id = %s
        '''
        self.cur.execute(query, (self.user_id,))
        rows = self.cur.fetchall()

        for product_id, bought_quantity, current_quantity in rows:
            new_quantity = current_quantity - bought_quantity
            if new_quantity < 0:
                new_quantity = 0

            self.cur.execute("UPDATE products SET quantity=%s WHERE product_id=%s", (new_quantity, product_id))
        
        self.conn.commit()



    def card(self):
        card_id=input("Karta idisi: ")
        pasword=input("Karta ko'di: ")
        self.cur.execute("select password,balance from cards where card_id=%s",(card_id, ))
        result=self.cur.fetchone()
        if result is None:
            print("Id xato kiritilgan!")
        pw,bl=result
        if pw==pasword:

            if bl>=self.price:
                bl-=self.price
                self.cur.execute("UPDATE cards SET balance=%s WHERE card_id=%s",(bl,card_id))
                self.conn.commit()
                print("Xaridingiz uchun rahmat:)")

                self.update()
                self.cur.execute("Delete from basket where user_id=%s",(self.user_id, ))
                self.conn.commit()

            else:
                print("Balansda yetarli mablag' mavjud emas!!!")
        else:
            print("Kod xato kiritilgan!")
            


    def add_product(self,product_name,unit_price,quantity):
        self.cur.execute("Insert into products(product_name,unit_price,quantity) values (%s,%s,%s)",(product_name,unit_price,quantity))
        self.conn.commit()
        print("Mahsulot qo'shildi")



    def del_product(self,product_id):
        self.cur.execute("Delete from products where product_id=%s",(product_id, ))
        self.conn.commit()
        print("Maxsulot o'chirildi")


    def update_quantity(self):
        product_id=int(input("Mahsulot idsini kiriting: "))
        quantity=int(input("Sonini kiriting: "))

        self.cur.execute("Update products Set quantity=%s where product_id=%s",(quantity,product_id))
        self.conn.commit()
        print("Mahsulot soni yangilandi")

    

    def close(self):
        self.cur.close()
        self.conn.close()
        

    
sm=Suppermarket("supper_market_db","User_Sql","123")


def log():
    while True:
        print('''\n
                1. yangi akkaunt yaratish,
                2. login kirish
              ''')
        n = input("Sonni kiriting: ")

        if n == '1':
            un = input("username: ")
            pw = input("password: ")
            sm.create_accaunt(un, pw)

        elif n == '2':
            un = input("username: ")
            pw = input("password: ")
            if un=="Admin" and pw=="123":
                admin_panel()

            elif sm.login(un, pw) == 1:
                menu()            


        else:
            print("Menuda ko'rsatilgan sonlarni kiriting!")



def admin_panel():

    while True:
        print('''
            1.Mahsulot qo'shish
            2.Mahsulot ochirish
            3.Mahsulotlarni ko'rish
            4.Mahsulot sonini yangilash
            5.Chiqish
            ''')
        n=input("Soni kiriting: ")

        if n=='1':
            p_n=input("Maxsulot nomi: ")
            un=input("Narxi: ")
            qu=int(input("Soni: "))
            sm.add_product(p_n,un,qu)

        elif n=='2':
            p_i=input("Mahsulot idsini kiriting: ")

            sm.del_product(p_i)

        elif n=='3':
            sm.wacht_list()

        elif n=='4':
            sm.update_quantity()
        
        elif n=='5':
            print("Xayr salomat bo'ling!")
            exit()
            
        
        else:
            print("Menuda ko'rsatilgan sonlarni kiriting!")



def menu():
    while True:
        print('''
        Menu
        1. Mahsulotlar
        2. Savat
        3. Chiqish
        ''')
        n = input("Sonni kiriting: ")
        if n == '1':
            sm.products()

        elif n == '2':
            sm.basket()

        elif n == '3':
            print("Xayr salomat bo'ling!")
            exit()

        else:
            print("Menuda ko'rsatilgan sonlarni kiriting!")


if __name__=="__main__":
    log()


# Users jadvali
# CREATE TABLE users (
# 	user_id SERIAL PRIMARY KEY,
#     username VARCHAR(50) ,
#     password VARCHAR(255)
# );

# Products jadvali
# CREATE TABLE products(
#   quantity int,
# 	product_id SERIAL PRIMARY KEY,
# 	product_name varchar(20),
# 	unit_price real
# );

# Savat jadvali
# CREATE TABLE basket(
#   soni int,
# 	basket_id SERIAL PRIMARY KEY,
# 	product_id int,
# 	user_id int,
#   FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
#   FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
# );

# Cartalar jadvali
# CREATE TABLE cards(
# 	card_id varchar(16),
# 	password varchar(20),
# 	balance real
# );