## Task 1: searching 
**Given an emotion profile, return songs that match emotion profile in decreasing order**
- - - -
##### key challenges:
* How to consider multiple emotions and rank songs accordingly 
* How to search efficiently as database scale 
##### Assumptions:
* Database already populated with songs and its emotion profile
* Songs are more likely to be emotionally consistent than inconsistent 
* Users are unlikely to try to convey strong conflicting emotions  
##### Objectives:
* Well defined index structure to allow easy and efficient queries 
* Well-formed query to allow accurate query results 
##### Ideas:
**Approach 1** (_implemented_): Sort result by decreasing order of song and input’s sum of square error/L2 Norm 
* No information loss, widely accepted similarity metric 
* require calculation on the fly, require index full scan, expensive 
* Runtime exception on script
* support for [dense_vector datatype](https://www.elastic.co/guide/en/elasticsearch/reference/master/dense-vector.html) is likely to be supported in the future, which can be used for [scoring based on cosine similarity](https://www.elastic.co/guide/en/elasticsearch/reference/master/query-dsl-script-score-query.html#vector-functions)

**Approach 2** (_implemented_): spatial indexing - think of Wheel of Emotion as a cartesian coordinate system centered at (0, 0), and assign x, y value to any particular song. 
* The coordinate of each emotion is determined by its intensity (radius), and where the emotion is on the wheel of emotion (angle). The coordinate of a song is calculated by adding up the coordinate of each emotion. 
* This approach assumes relation between emotions, as outlined by Robert Plutchik’s wheel of emotions 
* Emotionally consistent songs would lean towards one particular direction 
* Emotionally inconsistent songs would be more towards the middle 
* Uses Elasticsearch’s support for spatial indexing with geo_point for fast querying and sorting 
* boiling a song’s emotional profile down to a geolocation makes search significantly easier and faster, however it creates some some information loss 

**Approach 3**: hybrid of approach 1 and approach 2
* Use approach 2 to get top N results
* Sort the N results using approach 1, eliminate the need to run L2 Norm on entire database

**Approach 4**: Building on top of the cartesian coordinate system outlined in approach 2, we can represent each song’s emotion profile as an octagon on the coordinate system. Songs with maximum overlap and minimum disjoint regions to the input would be more optimal 
* Elasticsearch supports indexing of shapes with geo_shape, however sorting results based on overlap is not yet supported 
* Use locality-sensitive hashing (LSH) to hash emotional profile, allowing elasticsearch to index and query efficiently
* Example of such plugins: [ElastiK Nearest Neighbors – Insight Data](https://blog.insightdatascience.com/elastik-nearest-neighbors-4b1f6821bd62)

#####  Misc comments & observations:
* need a good system to parse search query into an emotional profile 
* can use a knowledge base with words with predefined emotion profile 
* create an emotion detection package that parse any sentence into emotion profile 
* if user music taste profile of a user is known, could use an additional layer of filter to narrow down genres more likely to match user’s taste 


## Task 2: prediction
**predict the new lyrics’ emotion profile based on lyric itself and the emotion profile of all songs in the database**
- - - -
#####  Key challenges:
* How to use each lyrical line as a cue for the new lyric’s emotion profile 
* How to use existing songs’ emotion profile and their similarity to new lyrics to deduce an emotion profile for the new song 

##### Assumptions:
* Database already populated with songs along with their lyrics and accurate emotion profile 
* Lyrics is the only determinant of a song’s emotion profile (would not hold in reality as genre, rhythm etc are also indicators)
* Songs with higher similarity to the new lyrics is likely to have similar emotion profile with the new lyrics 
#####  Objectives:
* Well defined query to search for songs in the database that matches the new lyric the most
* Index structure that allows for easier and more efficient matching between new lyrics and existing lyrics
##### Ideas: 
**Approach 1**(_implemented_): Match songs with closest lyrical similarity with new lyrics (line by line), and use a weighted average approach to deduce new lyrics’ emotion profile 
* Utilizes the English analyzer for both indexing and searching to allow for more relevant search result
* Utilizes elasticsearch’s scoring system and uses the relevancy scores for each song as weights for weighted average
* Each lyrical line is assigned an emotion profile based on the weighted average of top results from elasticsearch query, with each hit’s score as the weight, and the emotion profile of the whole song is the average of emotion profiles of each lyrical line
* Since some lyrical lines might not convey much emotion, the result could potentially be skewed

**Approach 2** (_implemented_): Use the entire song’s lyric as a search query to get the result, and average it with the result from approach 1
* This could alleviate the skew problem mentioned in approach 1

##### Misc comments & observations: 
* This task does not have as much runtime constraint as the previous task. We care more about accuracy of the emotion profile assignment than fast assignment 
* It would be helpful to have a dictionary of words that specifies the emotion of a word and the intensity of the emotion. Each song can then be analyzed and classified independently according to the frequency and intensity of emotion words. If emotion profile of songs in the database is incorrect or database entries are not extensive, predicting new lyric’s emotion profile based on existing ones might skew results 
* A song’s rhythm, genre as well as an artist’s style, among other things, should also be considered when building an emotion profile 
