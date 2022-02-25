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
    return session.post(url + '/login', data=form_data)

# requires we are at the level select page after login
def select_level(session):
    levels_dict = session.get(url + '/get_levels').json()

    if 'levels' not in levels_dict:
        raise ValueError(f'Something went wrong during level select...\n\nRaw Response:\n{response.content}')

    # do something better than this to add colorization to completed / not completed levels
    # also add point values to each level
    level_names = list(map(lambda x: x['name'], levels_dict['levels']))

    choice = inquirer.list_input('Select a Level', choices=level_names)
    return choice


def play(user, password):
    with requests.Session() as s:
        print('Logging In...')
        response = login(s, user, password)

        if 'Choose Your Next Level' not in response.text:
            if 'Login failed' in response.text:
                print('Login failed')
                return

            raise ValueError(f'Something went wrong during login...\n\nRaw HTML:\n{response.content}')

        print('Loading Level Select...')
        print(select_level(s))
        # if selecting tutorial level, make sure to skip tutorial!
        # look for an a tag with

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        raise ValueError(f'Play microcorruption via command line.\nUsage: {sys.argv[0]} <username> <password>')

    play(sys.argv[1], sys.argv[2])
