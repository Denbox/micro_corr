# KNOWN BUGS:
# Tutorial Level currently broken


import requests, inquirer, sys
from bs4 import BeautifulSoup

url = 'https://microcorruption.com'

def login(session, user, password):
    response = session.get(url + '/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('meta', attrs={'name': 'csrf-token'})['content']
    form_data = {
        'name': user,
        'password': password,
        'authenticity_token': csrf_token
    }

    response = session.post(url + '/login', data=form_data)

    if 'Choose Your Next Level' not in response.text:
        if 'Login failed' in response.text:
            print('Login failed!')
            return

        raise ValueError(f'Something went wrong during login...\n\nRaw HTML:\n{response.content}')

    return response

# requires we are at the level select page after login
def select_level(session):
    levels_dict = session.get(url + '/get_levels').json()

    if 'levels' not in levels_dict:
        raise ValueError(f'Something went wrong during level select...\n\nRaw Response:\n{response.content}')

    # do something better than this to add colorization to completed / not completed levels
    # also add point values to each level
    label = lambda level: '✅' if level['done'] else '❌'
    points = lambda level: int(level['rating'])
    pad_len = max(map(lambda x: len(str(points(x))), levels_dict['levels']))
    name = lambda level: level['name']
    level_names = list(map(lambda x: f'{label(x)} ({points(x):{pad_len}}) {name(x)}', levels_dict['levels']))

    # strip the first characters off choice to remove pass/fail, points, and spaces
    choice = inquirer.list_input('Select a Level', choices=level_names)[5 + pad_len:]
    return choice

def load_level(session, level):
    # while we could check if any debuggers are currently running
    # this script just kills each time - we're running it locally anyway!
    session.post(url + '/cpu/dbg/kill')
    session.post(url + '/cpu/set_level', data={'level': level})

    # we don't super care about this response because we will play with our own CPU
    # but it helps us check if we're at a good state so far
    response = session.get(url + '/cpu/debugger')
    if 'Debugger Console' not in response:
        raise ValueError(f'Couldn\'t load debugger for some unknown reason.\n\nRaw Response:\n{response.content}')

    # THE FOLLOWING PART OF THIS FUNCTION IS UNFINISHED AND UNTESTED

    # do I need to do is_alive?
    # do I need to do whoami? looks like {"name": username, "level": levelname}
    manual = session.get(url + '/get_manual')
    load = session.post(url + '/cpu/load') # not sure what this response means
    reset = session.post(url + '/cpu/reset/debug') # not sure what this response means
    # figure out wtf snapshots and events do and how to load them

    # we should be using all of these gets / posts to set up memory of our CPU

    # besides this part, the code here is almost done, and the rest of the work is on the disassembler
    # we have to do 4 things here
    # 1. add code to submit passwords to the locks, and handle responses properly
    # 2. add code to take us back to the level select page
    # 3. make sure the tutorial level works
    # 4. make sure that we recover from CPU timeouts gracefully. by "timeout" I mean, "microcorruption stopped hosting our state on their infrastructure, how do we re-run it again?"

    # at the end of this, we shouldn't be returning response
    return response

def play(user, password):
    with requests.Session() as s:
        print('Logging In...')
        response = login(s, user, password)

        print('Loading Level Select...')
        level = select_level(s)

        print('Loading Level...')
        print(load_level(s, level))
        # if selecting tutorial level, make sure to skip tutorial!
        # look for an a tag with

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        raise ValueError(f'Play microcorruption via command line.\nUsage: {sys.argv[0]} <username> <password>')

    play(sys.argv[1], sys.argv[2])
