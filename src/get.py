from src.config import db, collection
from bson.objectid import ObjectId
from random import choice

def random_message_character(person):

    #this finds random scene where character attends
    
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

    limit = 10 if int(limit) > 10 else limit


    if scene_id == 'random':

        if season == -1:
            scene = list(collection.aggregate([
                { '$sample': { 'size': int(limit) } }]))
            scene = jsonize(scene)

            return scene
        elif episode == -1:

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

                
        else:
        
            scene = list(collection.aggregate([
            { '$match': {'$and': [{ 'episode.season': season }, {'episode.number': episode}] }},
            { '$sample': { 'size': 1 } }]))

            try:
                check = scene[0]
            except IndexError:
                return f'Error. The season {season},  episode {episode} entried does not exist. Please check API documentation for finding available seasons and episodes.'
            
            else:
                scene = jsonize(scene)
                return scene

    else:
        try:
            scene = [collection.find_one({ '_id': ObjectId(scene_id)})]
            scene = jsonize(scene)

            return scene

        except:
            return f'Error. The scene_id {scene_id} does not exist. Please check API documentation for finding available scene ids.'



def jsonize(my_list):

    tmp_list = []

    for item in my_list:

        id_string = str(item.get('_id'))
        item['_id'] = id_string
        tmp_list.append(item)
        

    return tmp_list



def list_items(item, season = -1, episode = -1):


    if item == 'character':
        return return_characters(season, episode)

    if item == 'scene':
        return return_scenes(season, episode)








def return_characters(season = -1, episode = -1):

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
