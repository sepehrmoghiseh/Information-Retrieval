import json
import math

data={}
sort={}
list=[]
data_log=[]
index_log=[]
with open('result.json') as f:
  data = json.load(f)

print("\n\n\n\n\n\n")
for i in data.keys():
  sort[i]=data[i][0]

sort_by_value = dict(sorted(sort.items(), key=lambda item: item[1],reverse=True))
for i in sort_by_value.keys():
  list.append(sort_by_value[i])

for i in range(len(list)):
  data_log.append(math.log(list[i]))
  index_log.append((math.log(i+1)))

# importing the required module
import matplotlib.pyplot as plt

# x axis values
# corresponding y axis values

# plotting the points
plt.plot(index_log, data_log)
# naming the x axis
plt.xlabel('x - axis')
# naming the y axis
plt.ylabel('y - axis')

# giving a title to my graph
plt.title('zipf law')

# function to show the plot
plt.show()


def slopee(x1, y1, x2, y2):
  x = (y2 - y1) / (x2 - x1)
  return x


print(slopee(data_log[0], index_log[0], data_log[1], index_log[1]))