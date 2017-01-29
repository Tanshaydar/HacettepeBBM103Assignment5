from os import listdir, makedirs
from os.path import isfile, join, exists

"""
OPEN FILES AND CREATE DICTIONARIES IF NECESSARY
"""
outputReview = open("review.txt", "w", encoding="iso-8859-1")
outputFilmGenre = open("filmGenre.txt", "w", encoding="iso-8859-1")

filmsPath = "film"
filmListPath = "filmList"
filmGuessPath = "filmGuess"

"""
stop words
"""
stopWordsFile = open("stopwords.txt", "r", encoding="iso-8859-1")

"""
movie id | movie title | video release date | IMDb URL
| unknown | Action | Adventure | Animation | Children's | Comedy | Crime | Documentary | Drama | Fantasy | Movie-Noir | Horror | Musical | Mystery | Romance | Sci-Fi | Thriller | War | Western |

"""
filmNameList = []  # This is for the first stage, review.txt comparison
itemFile = open("u.item", "r", encoding="iso-8859-1")
itemDictionary = {}

"""
id | genre
"""
genreDictionary = {}
genreFile = open("u.genre", "r", encoding="iso-8859-1")

"""
user id | age | gender | occupation id | zip code & list of rating which is added manually after file read
"""
userDictionary = {}
userFile = open("u.user", "r", encoding="iso-8859-1")

"""
id | occupation
"""
occupationDictionary = {}
occupationFile = open("u.occupation", "r", encoding="iso-8859-1")

"""
user id | movie id | rating | timestamp
"""
dataFile = open("u.data", "r", encoding="iso-8859-1")

"""
READ NECESSARY DATA
"""

for line in itemFile.readlines():
    items = line.rstrip("\n").split("|")
    itemDictionary[items[0]] = items[1:]
    filmNameList.append(items[1].partition(" (")[0].lower())

for line in genreFile.readlines():
    genres = line.rstrip("\n").split("|")
    genreDictionary[genres[1]] = genres[0]

for line in userFile.readlines():
    users = line.rstrip("\n").split("|")
    users.append([])
    userDictionary[users[0]] = users[1:]

for line in occupationFile.readlines():
    occupations = line.rstrip("\n").split("|")
    occupationDictionary[occupations[0]] = occupations[1]

for line in dataFile.readlines():
    dataf = line.rstrip("\n").split("\t")
    userRatingDictionary = {dataf[1]: dataf[2:]}
    userDictionary[dataf[0]][4].append(userRatingDictionary)

"""
STAGE 1
"""

filmFileList = [file for file in listdir(filmsPath) if isfile(join(filmsPath, file))]
fileFilmNameList = []

movieReviewDictionary = {}  # This will be necessary for creating html files

for filmFile in filmFileList:
    filmFile = open(join(filmsPath, filmFile), "r")
    filmName = filmFile.readline().partition(" (")[0].lower()
    fileFilmNameList.append(filmName)
    review = ""
    for line in filmFile.readlines():
        line = line.rstrip("\n")
        review += line + " "
    movieReviewDictionary[filmName] = review
    filmFile.close()

existingFilms = [film for film in filmNameList if film in fileFilmNameList]


class FilmNotInList(Exception):
    """Class for user-defined exception"""
    pass


for key, value in itemDictionary.items():
    try:
        if value[0].partition(" (")[0].lower() in existingFilms:
            outputReview.write(key + " " + value[0].partition(" (")[0] + "  is found in folder\n")
        else:
            raise FilmNotInList
    except FilmNotInList:
        outputReview.write(
            key + " " + value[0].partition(" (")[0] + "  is not found in folder. Look at " + value[2] + "\n")

if not exists(filmListPath):
    makedirs(filmListPath)
for movieId, movieValues in itemDictionary.items():
    movie = movieValues[0].partition(" (")[0].lower()
    if movie in existingFilms:
        outputHtml = open(join(filmListPath, movieId + ".html"), "w")
        movieName = movieValues[0].partition(" (")[0]
        imdbLink = movieValues[2]

        ratingList = [(userId, ratings) for userId, value in userDictionary.items() for ratings in value[4] if
                      movieId in ratings]

        genres = ""
        genreCount = 0
        for genre in movieValues[3:]:
            if genre == "1":
                genres += genreDictionary[str(genreCount)] + " "
            genreCount += 1

        userDataList = ""
        userCount = 0
        totalRates = 0
        for ratings in ratingList:
            userCount += 1
            totalRates += int(ratings[1][movieId][0])
            userDataList += "<b>User: </b> "
            userDataList += str(ratings[0])
            userDataList += "  <b> Rate: </b> "
            userDataList += ratings[1][movieId][0]
            userDataList += "  <br><b>User Detail: </b><b>Age: </b> "
            userDataList += str(userDictionary[ratings[0]][0])
            userDataList += "<b> Gender: </b> "
            userDataList += userDictionary[ratings[0]][1]
            userDataList += "<b> Occupation: </b> "
            userDataList += occupationDictionary[userDictionary[ratings[0]][2]]
            userDataList += "<b> Zip Code: </b> "
            userDataList += str(userDictionary[ratings[0]][3])
            userDataList += "<br>"

        totalRate = totalRates / userCount

        outputHtml.write("<html>\n<head>\n<title>"
                         + movieName
                         + " </title>\n</head>\n<body>\n<font face=\"Times New Roman\" font size=\"6\" color=\"red\"<b>"
                         + movieName
                         + " </b></font><br>\n<b>Genre: </b>"
                         + genres
                         + "<br>\n<b>IMDB Link: </b><a href=\""
                         + imdbLink
                         + "\">"
                         + movieName
                         + " </a><br>\n<font face=\"Times New Roman\" font size=\"4\" color=\"black\"><b>Review: </b><br>"
                         + movieReviewDictionary[movie]
                         + "\n</font><br><br>\n<b>Total User: </b>"
                         + str(userCount)
                         + "  /  <b>Total Rate: </b>"
                         + str(totalRate)
                         + "<br>\n<br><b>User who rate the film: </b><br>"
                         + userDataList
                         + "\n</body>\n</html>")
        outputHtml.close()

"""
STAGE 2
"""

filmGuessFileList = [file for file in listdir(filmGuessPath) if isfile(join(filmGuessPath, file))]
fileFilmNameList = []

stopWordList = set([])
for stop_word in stopWordsFile.readlines():
    stopWordList.add(stop_word.rstrip("\n"))

genreWords = {}  # This will be necessary for creating html files

for movieId, movieValues in itemDictionary.items():
    movie = movieValues[0].partition(" (")[0].lower()
    if movie in existingFilms:
        genres = ""
        genreCount = 0
        for genre in movieValues[3:]:
            if genre == "1":
                wordList = set([])
                for word in movieReviewDictionary[movie].split(" "):
                    wordList.add(word)
                    if genreDictionary[str(genreCount)] in genreWords:
                        genreWords[genreDictionary[str(genreCount)]] |= wordList
                    else:
                        genreWords[genreDictionary[str(genreCount)]] = set([])
            genreCount += 1
print(genreWords)

filmGuessNames = {}

for filmFile in filmGuessFileList:
    filmFile = open(join(filmGuessPath, filmFile), "r")
    filmName = filmFile.readline().partition(" (")[0].lower()
    filmGuessNames[filmName] = []
    reviewWords = set([])
    for filmLine in filmFile.readlines():
        if "REVIEWED ON" in filmLine:
            break
        else:
            wordList = []
            for word in filmLine.rstrip("\n").split(" "):
                wordList.append(word)
            reviewWords |= set(wordList)

        reviewWords - stopWordList

    for key, value in genreWords.items():
        # print(filmName.upper() + " " + str(len(reviewWords.intersection(value))) + " " + key)
        if len(reviewWords.intersection(value)) >= 20:
            filmGuessNames[filmName].append(key)
    filmFile.close()

outputFilmGenre.write("Guess Genres of Movie based on Movies\n")

for film, genres in filmGuessNames.items():
    line = ""
    line += film.upper() + " : "
    for genre in genres:
        line += genre + " "
    line += "\n"
    outputFilmGenre.write(line)

"""
CLOSE FILES
"""
stopWordsFile.close()
itemFile.close()
genreFile.close()
userFile.close()
occupationFile.close()
dataFile.close()

outputReview.close()
outputFilmGenre.close()
