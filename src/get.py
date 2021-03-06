from src.config import db, collection
from bson.objectid import ObjectId
from random import choice
import numpy as np

def random_message_character(person):
    '''
    Finds a random script line in all documents of the MongoDb collection
    Args:
        person(str): character name
    Returns:
        tmp_list(list): list containing a dictionary with script line

    '''
    
    try:
        scene = list(collection.aggregate([
        { '$match': { 'attendees': person } },
        { '$sample': { 'size': 1 } }]))[0]
    except IndexError:
        return f'Error. The character {person} do not exist. Please check API documentation for finding available characters.'


    lines_character = [line.get('line')  for line in scene.get('script') if line.get('speaker') == person ]

    selected_line = choice(lines_character)

    tmp_list = [{'line': selected_line, 'episode': scene.get('episode'), 'scene': {'_id': str(scene.get('_id')), 'attendees': scene.get('attendees')}}]

    return tmp_list


def scene(scene_id, season = -1, episode = -1, limit = 1):
    '''
    Based on parameters, finds a scene (MongoDB document) from MongoDB collection
    Args:
        scene_id(str): ObjectID number from a MongoDB document or 'random'
        season(str): season number, for random option
        episode(str): episode number, for random option
        limit(int): number of occurrences for random option

    Returns:
        scene(list) or Error message

    '''

    try:
        check = int(limit)
        if check < 0:
            return 'Error. Wrong limit value. Please provide positive integer'
    except:
        return 'Error. Wrong limit value. Please provide positive integer'
    else:
        limit = 10 if int(limit) > 10 else limit


    if scene_id == 'random':

        if season == -1 and episode == -1:
            scene = list(collection.aggregate([
                { '$sample': { 'size': int(limit) } }]))
            scene = jsonize(scene)

            return scene
        elif season != -1 and episode == -1:

            scene = list(collection.aggregate([
            { '$match': { 'episode.season': season } },
            { '$sample': { 'size': int(limit) } }]))

            try:
                check = scene[0]
            except IndexError:
                return f'Error. The season {season} entried does not exist. Please check API documentation for finding available seasons.'

            else:
                scene = jsonize(scene)
                return scene

                
        elif season != -1 and episode != -1:
        
            scene = list(collection.aggregate([
            { '$match': {'$and': [{ 'episode.season': season }, {'episode.number': episode}] }},
            { '$sample': { 'size': int(limit) } }]))

            try:
                check = scene[0]
            except IndexError:
                return f'Error. The season {season},  episode {episode} entried does not exist. Please check API documentation for finding available seasons and episodes.'
            
            else:
                scene = jsonize(scene)
                return scene
        else:
            return f'Error. You have specified an episode without a season.'

    else:
        try:
            scene = [collection.find_one({ '_id': ObjectId(scene_id)})]
            scene = jsonize(scene)

            return scene

        except:
            return f'Error. The scene_id {scene_id} does not exist. Please check API documentation for finding available scene ids.'



def jsonize(my_list):
    '''
    Auxiliary function to convert ObjectID of documents to string for return in json file.
    Args:
        my_list(list): list of MongoDB documents
    
    Returns:
        tmp_list(list): json-friendly list of documents

    '''

    tmp_list = []

    for item in my_list:

        id_string = str(item.get('_id'))
        item['_id'] = id_string
        tmp_list.append(item)
        

    return tmp_list



def list_items(item, season = -1, episode = -1):

    '''
    Main function to handle list get method
    Args:
        item(str): type of list to return
        season(str): season number
        episode(str): episode number

    Returns:
        Queried list or error message

    '''


    if item == 'character':
        return return_characters(season, episode)

    if item == 'scene':
        return return_scenes(season, episode)

    if item == 'season':
        return return_seasons()
    
    if item == 'episode':

        return return_episodes(season)

    else: 
        return f'Error. The item {item} entried is not correct. Please check API documentation for available items.'




def return_seasons():
    '''
    Auxiliary function for returning list of seasons.

    Returns:
        tmp_list(list): list of seasons

    '''

    tmp_list = collection.distinct('episode.season')

    return tmp_list

def return_episodes(season):
    '''
    Auxiliary function for returning list of episodes given a season.
    Args:
        season(str): season number

    Returns:
        tmp_list(list): list of episodes or error message

    '''

    tmp_list = collection.distinct('episode.number',{'episode.season': season})

    try:
        check = tmp_list[0]
    except IndexError:
        return f'Error. The season {season} entried does not exist. Please check API documentation for finding available seasons.'

    else:
        return tmp_list



def return_characters(season = -1, episode = -1):
    '''
    Auxiliary function for returning list of characters.
    Args:
        season(str): season number, optional.
        episode(str): episode number, optional.
        

    Returns:
        tmp_list(list): list of episodes or error message.

    '''

    if season == -1:
        tmp_list = collection.distinct('attendees')
        return tmp_list

    elif season != -1 and episode == -1:

        tmp_list = collection.distinct('attendees', {'episode.season': season})

        try:
            check = tmp_list[0]
        except IndexError:
            return f'Error. The season {season} entried does not exist. Please check API documentation for finding available seasons.'

        else:   

            return tmp_list

    else:

        tmp_list = collection.distinct('attendees', {'$and':[{'episode.season': season},{'episode.number': episode}]})
        try:
            check = tmp_list[0]

        except IndexError:
            return f'Error. The season {season},  episode {episode} entried does not exist. Please check API documentation for finding available seasons and episodes.'
        else:

            return tmp_list


def return_scenes(season, episode):
    '''
    Auxiliary function for returning list of scenes.
    Args:
        season(str): season number
        episode(str): episode number
        

    Returns:
        list of scenes or error message.

    '''

    if season == -1 or episode == -1:

        return 'Error. Missing a required parameter. Please check API documentation.'

    else:

        list_object = collection.distinct('_id', {'$and':[{'episode.season': season},{'episode.number': episode}]})
        try:
            check = list_object[0]
        except IndexError:
            return f'Error. The season {season},  episode {episode} entried does not exist. Please check API documentation for finding available seasons and episodes.'

        else:

            return [{'scene_id': str(obj), 'season': season, 'episode': episode} for obj in list_object]



def sentiment_character(person, season = -1, episode = -1):
    '''
    Retrieves from collection, the sentiment score of a character.
    Args:
        person(str): character name
        season(str): season number, optional
        episode(str): episode number, optional
    
    Returns:
        List containing dictionary with information or error message

    '''

    if season == -1 and episode == -1:
        matches = list(collection.find({'attendees':person}, {'script':1, '_id':0}))

    elif season != -1 and episode == -1:
        matches = list(collection.find({'attendees':person, 'episode.season':season}, {'script':1, '_id':0}))

    else:
        matches = list(collection.find({'attendees':person, 'episode.season':season, 'episode.number': episode}, {'script':1, '_id':0}))

   

    try:
        check = matches[0]

    except IndexError:

        if season == -1 and episode == -1:
            return f'Error. The character {person} do not exist. Please check API documentation for finding available characters.'

        elif season != -1 and episode == -1:
            return f'Error. The character {person} or season {season} entried do not exist. Please check API documentation for finding available characters and seasons.'

        else:
            return f'Error. The character {person} or season {season}  or episode number {episode} entried do not exist. Please check API documentation for finding available characters, seasons and episodes.'


    else:
                    
        tmp_list = []
        for match in matches:
            for line in match.get('script'):
                if line.get('speaker') == person:
                    tmp_list.append(line.get('sentiment_score'))
                else:
                    pass
        

        return [{'character' : person, 'sentiment_score': round(np.array(tmp_list).mean(),3)}]

def sentiment_episode(season, episode):
    '''
    Retrieves from collection, the sentiment score of a episode.
    Args:
        season(str): season number
        episode(str): episode number
    
    Returns:
        List containing dictionary with information or error message

    '''

    match = list(collection.find({ 'episode.season': season, 'episode.number': episode}))
    try:
        check = match[0]
    except IndexError:
        return f'Error. The season {season},  episode {episode} entried does not exist. Please check API documentation for finding available seasons and episodes.'

    else:
        tmp_list = []
        for scene in match:
            
            
            mean_scene = np.mean([line.get('sentiment_score') for line in scene.get('script')])

            tmp_list.append(mean_scene)

        
    final_score = round(np.mean(tmp_list),3)
    
    return [{'season': season, 'episode': episode, 'sentiment_score': final_score}]












