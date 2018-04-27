rebate = 0.06  #this is diff between weekend and working-day:   working-day is 0.02 ; weekend is 0.06
sp_1 = input("please input sp_1: ")
sp_2 = input("please input sp_2: ")
total = float(sp_1) + float(sp_2)
mul = float(sp_1) * float(sp_2)
profit_withou_bonus = total - mul
return_profi = total * rebate
return_bonus = (return_profi - profit_withou_bonus) / total
print('percent: {:.2%}'.format(return_bonus))
