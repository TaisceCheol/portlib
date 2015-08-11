from sklearn import neighbors

n_neighbors = 1

X = [
	["16161616444","8888161684"],
	["888888","4.816168"],
	["88888848","4.88848"]
]

y = ['reel','jig','slip-jig']

clf = neighbors.KNeighborsClassifier(n_neighbors, weights='uniform')

clf.fit(X, y)

print clf.predict(["88816164","8884."])
print clf.predict(["4444","4444"])
