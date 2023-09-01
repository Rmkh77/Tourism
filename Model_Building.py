import warnings
warnings.filterwarnings('ignore')

from geopy.geocoders import Nominatim
import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv("dataset.csv")
print(df.info())

city_names = df['location']

#geopy in action
country = 'India'
longitude =[]
latitude =[]
geolocator = Nominatim(user_agent="Trips")
#finding latitude and longitude of all places present in the dataset
for c in city_names.values:
    location = geolocator.geocode(c+','+ country)
    if location is not None:
          latitude.append(location.latitude)
          longitude.append(location.longitude)
df['latitude']=latitude
df['longitude']=longitude

l2=df.iloc[:,-1:-3:-1]

#Finding the optimum number of clusters for k-means classification
#calculating wcss value for k=1 to 11
from sklearn.cluster import KMeans
wcss = []
for i in range(1, 18):
    kmeans = KMeans(n_clusters = i, init = 'k-means++', max_iter = 300, n_init = 10, random_state = 0)
    kmeans.fit(l2)
    wcss.append(kmeans.inertia_)
    
#plotting k vs wcss
plt.plot(range(1, 18), wcss)
plt.title('The elbow method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS') #within cluster sum of squares
plt.show()

#clustering the data into 9 groups
kmeans=KMeans(9)
kmeans.fit(l2)
id=kmeans.fit_predict(l2)
df['loc_clu']=id

import pickle as pkl
pkl.dump(df,open('pickle_file.pkl','wb'))



