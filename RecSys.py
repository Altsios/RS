import csv 
import math 
import json 
import requests 

data = [] 
context = [] 
sim = [] 
viewed = [] 
notViewed = [] 


# читаем данные из файла 
def read(file, lst):
    f = open(file)
    for row in csv.reader(f):
        lst.append(row)
        f.close()


def sort_col(i): # сортировка sim
 return i[1]


# подсчет похожести двух пользователей
def fsim(row, u, v):
    numer = 0 # числитель
    denomeru = 0 # часть знаменателя 1
    denomerv = 0 # часть знаменателя 2
    for i in range(1, len(row)):
        if int(i) in viewed: # интересуют только те фильмы, что смотрел пользователь
            if int(data[v][i]) == -1: # если сравниваемый пользователь не оценил
                continue
            numer += int(data[u][i]) * int(data[v][i]) # формируем знаменатель
            denomeru += int(data[u][i]) ** 2
            denomerv += int(data[v][i]) ** 2
    if denomerv == 0 or denomeru == 0: # если они не смотрели одни и те же фильмы
        return
    return round(numer / (math.sqrt(denomeru) * math.sqrt(denomerv)), 3) # округляем до тысячных


# Находим k похожих для заданного пользователя(num) 
def findsim(num, k):
    lst = []
    cnt = len(data[0]) # число элементов в строке
# списоки фильмов, которые оценил и не оценил искомый пользователь 
    for i in range(1, cnt):
        if int(data[num][i]) == -1: # если пользователь еще не смотрел фильм
            notViewed.append(i) # i - номер фильма в исходной матрице
        else:
            viewed.append(i) # просмотренные пользователем фильмы
for row in data: # проходимся по всем пользователям кроме исходного, учитывая только просмотренные им фильмы 
    ch = row[0]
    if ch == '': # не смотрим первую строчку
        continue
    ch = ch[ch.find(' ')]
    ch = ch.replace('-1', '0')
    v = int(ch)
    if v == num: # не сравниваем с самим пользователем
        continue
        lst.append([v, fsim(row, num, v)])
        lst.sort(key=sort_col, reverse=True)
    global sim
    sim = lst[:k] # оставляем в глобальном списке k похожих


def ratefilm(averrate, i): 
    numer = 0 # числитель
    denomeru = 0 # знаменатель
    for user in sim:
        us = user[0]
        cntus = 0
        usaver = 0 # средняя оценка для сравниваемого пользователя
        if int(data[us][i]) != -1: # пользователь смотрел нужный фильм
            for rate in range(1, len(data[us])): # считаем для него среднее по фильмам
                if int(data[us][rate]) != -1:
                    cntus += 1 # считаем количество фильмов для серднего
                    usaver += int(data[us][rate])
                    usaver /= cntus # вычислили среднюю оценку для данного фильма
                    numer += user[1] * (int(data[us][i]) - usaver)
                    denomeru += user[1]
                else:
                    continue # если пользователь не смотрел данный фильм, идем к следуюдему в похожих
    return round(averrate + numer / denomeru, 3)


def knnmeth(num):
    dict = {}
    averrate = 0 # средняя оценка для искомого пользователя
    for i in viewed:
        averrate += int(data[num][i])
        averrate /= len(viewed)
    for i in notViewed:
        dict['movie ' + str(i)] = ratefilm(averrate, i)
    return dict


def contadv(ratedict, ans):
    percdict = {} # слвоарь с фильмом и процентом его просмотра в будние дни
    copyrate = ratedict.copy()
    for key in ratedict: # для каждого фильма из рекомендованнфх нахлдим процент просмотра в будние дни
        mov = int(key[key.find(' '):])
        cnt = 0
        weekcnt = 0
        for user in sim: # процент ищем среди похожих
            us = user[0]
            if context[us][mov] != ' -': # не в будний день
                if context[us][mov] not in [' Sat', ' Sun']: # если смотрели в будни
                    weekcnt += 1
                    cnt += 1
        percdict[key] = round(weekcnt / cnt, 1) # округляем до десятых
    newcopy = sorted(ratedict.items(), reverse=True)[0]
    for key in percdict.keys():
        if percdict[key] < 0.7: # если процент просмотра в будний день меньше 70%
            del copyrate[key] # удаляем запись из копии словаря с рейтингами
    copyrate = sorted(copyrate.items(), reverse=True) # сортируем по оценке, возвращая самый рекомендуемый
    if len(copyrate) == 0: # ничто под условия не подошло
        ans[newcopy[0]] = newcopy[1] # советуем фильм с самым высоким предсказанным рейтингом
    else:
        ans[copyrate[0][0]] = copyrate[0][1] # советуем самый просматриваемый в будний день фильм с макс. рейтингом


def main():
    k = 5 # k-похожих
    num = 37 # номер пользователя, для которого ищем оценки
# ЗАДАНИЕ 1 
    read("data.csv", data)
    findsim(num, k)
    my_dict = knnmeth(num) # словарь для хранения списка оцененных фильмов
# ЗАДАНИЕ 2 
    read("context.csv", context)
    contextdict = {} # ответ на второе задание
    contadv(my_dict, contextdict)
# ОТПРАВКА РЕЗУЛЬТАТОВ 
    js = json.dumps({'user': num, '1': my_dict, '2': contextdict}, indent=6)
    print(js)
    r = requests.post('https://cit-home1.herokuapp.com/api/rs_homework_1', js,
    headers={'Content-type': "application/json"})
# смотрим АШШШШИБК!!! или извещение об успехе 
    print(r.json())


if __name__ == "__main__": 
    main()