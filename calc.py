val=int(input("enter a number : "))
list=[val]
user_input="no"
while user_input=="no":
        user=input("+ for addition \n* for product \n- for subtract \n/ for division \n ")
        
       # var=0
        b=int(input("enter another value for operation : "))
        if user=="+":
            sum=val+b
            #print(sum)
            
            var=f"+{b}"
            list.append(var)
             #for i in list:
                #  print(i)
            print(*list,"=",sum)
            val=sum
            
        elif user=="*":
            pro=val*b
            #print(pro)
            var=f"*{b}"
            list.append(var)
            #for i in list:
                  #print(i)
            print(*list,"=",pro)
            val=pro
        elif user=="-":
            sub=val-b
            #print(sub)
            var=f"-{b}"
            list.append(var)
            #for i in list:
                # print(i)
            print(*list,"=",sub)
            val=sub
        else:
            div=val/b
            #print(div)
            var=f"/{b}"
            list.append(var)
            #for i in range(len(list)):
                #  print 
            print(*list,"=",div)          
            val=div
        choice=input("do want to exit :")
        
        if choice=="no":
                user_input="no"
        else :
                user_input="yes"
print("Thankyou , see you soon :)")
